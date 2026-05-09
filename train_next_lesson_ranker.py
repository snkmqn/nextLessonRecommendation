import json
import pickle
from pathlib import Path

import lightgbm as lgb
import pandas as pd
from sklearn.metrics import ndcg_score


DATA_DIR = Path("data")
MODEL_DIR = Path("models")

TRAIN_PATH = DATA_DIR / "next_lesson_ranker_train.csv"
TEST_PATH = DATA_DIR / "next_lesson_ranker_test.csv"

MODEL_PATH = MODEL_DIR / "next_lesson_ranker_lgbm.pkl"
METADATA_PATH = MODEL_DIR / "next_lesson_ranker_metadata.json"


TARGET_COLUMN = "relevance"

ID_COLUMNS = [
    "group_id",
    "user_id",
    "candidate_subtopic_code",
]

FEATURE_COLUMNS = [
    "user_level_num",
    "practical_experience_num",
    "learning_goal_num",
    "time_commitment_minutes",

    "completed_subtopics_count",
    "completion_ratio",
    "average_best_score_percent",
    "average_all_attempts_score_percent",
    "last_quiz_score",
    "failed_quiz_count",
    "days_since_last_activity",

    "candidate_level_num",
    "candidate_topic_order_index",
    "candidate_subtopic_order_index",
    "candidate_estimated_minutes",

    "is_preferred_topic",
    "is_same_topic_as_last_completed",
    "is_next_subtopic_in_same_topic",
    "is_first_subtopic_in_topic",
    "is_level_match",
    "is_time_commitment_match",
    "is_topic_not_started",
    "is_topic_in_progress",

    "need_reinforcement",
    "last_score_for_candidate",
    "best_score_for_candidate",
    "attempts_for_candidate",
]


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}. "
            f"First run: python ml/generate_next_lesson_ranker_dataset.py"
        )

    df = pd.read_csv(path)

    required_columns = set(ID_COLUMNS + FEATURE_COLUMNS + [TARGET_COLUMN])
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing columns in {path}: {sorted(missing_columns)}")

    return df


def sort_by_group(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(
        by=["group_id", "candidate_topic_order_index", "candidate_subtopic_order_index"],
        kind="mergesort",
    ).reset_index(drop=True)


def make_group_sizes(df: pd.DataFrame) -> list[int]:
    return df.groupby("group_id", sort=False).size().tolist()


def evaluate_ndcg_by_group(
    model: lgb.LGBMRanker,
    df: pd.DataFrame,
    k: int = 3,
) -> float:
    scores = []

    for _, group in df.groupby("group_id", sort=False):
        y_true = group[TARGET_COLUMN].to_numpy().reshape(1, -1)
        y_score = model.predict(group[FEATURE_COLUMNS]).reshape(1, -1)

        # Если в группе все relevance одинаковые, ndcg малоинформативен.
        # sklearn всё равно посчитает, но такие группы лучше пропускать.
        if len(set(group[TARGET_COLUMN].tolist())) <= 1:
            continue

        scores.append(ndcg_score(y_true, y_score, k=k))

    if not scores:
        return 0.0

    return float(sum(scores) / len(scores))


def train() -> None:
    train_df = sort_by_group(load_dataset(TRAIN_PATH))
    test_df = sort_by_group(load_dataset(TEST_PATH))

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    train_group = make_group_sizes(train_df)
    test_group = make_group_sizes(test_df)

    model = lgb.LGBMRanker(
        objective="lambdarank",
        metric="ndcg",
        boosting_type="gbdt",
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        max_depth=-1,
        min_child_samples=20,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        importance_type="gain",
    )

    model.fit(
        X_train,
        y_train,
        group=train_group,
        eval_set=[(X_test, y_test)],
        eval_group=[test_group],
        eval_at=[1, 3, 5],
        callbacks=[
            lgb.early_stopping(stopping_rounds=30),
            lgb.log_evaluation(period=25),
        ],
    )

    ndcg_1 = evaluate_ndcg_by_group(model, test_df, k=1)
    ndcg_3 = evaluate_ndcg_by_group(model, test_df, k=3)
    ndcg_5 = evaluate_ndcg_by_group(model, test_df, k=5)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    with MODEL_PATH.open("wb") as file:
        pickle.dump(model, file)

    metadata = {
        "model_name": "next_lesson_ranker_lgbm",
        "model_version": "v1",
        "model_type": "LightGBM LGBMRanker",
        "objective": "lambdarank",
        "target": TARGET_COLUMN,
        "feature_columns": FEATURE_COLUMNS,
        "id_columns": ID_COLUMNS,
        "train_path": str(TRAIN_PATH),
        "test_path": str(TEST_PATH),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "train_groups": int(train_df["group_id"].nunique()),
        "test_groups": int(test_df["group_id"].nunique()),
        "metrics": {
            "ndcg@1": round(ndcg_1, 6),
            "ndcg@3": round(ndcg_3, 6),
            "ndcg@5": round(ndcg_5, 6),
        },
    }

    with METADATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)

    print()
    print("Training completed")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")
    print("Metrics:")
    print(f"  NDCG@1 = {ndcg_1:.6f}")
    print(f"  NDCG@3 = {ndcg_3:.6f}")
    print(f"  NDCG@5 = {ndcg_5:.6f}")

    importances = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    print()
    print("Top feature importances:")
    print(importances.head(15).to_string(index=False))


if __name__ == "__main__":
    train()