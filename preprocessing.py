from __future__ import annotations

import pandas as pd


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


def items_to_dataframe(items: list[dict]) -> pd.DataFrame:
    rows = []

    for item in items:
        row = {}

        for column in FEATURE_COLUMNS:
            row[column] = item.get(column, 0)

        rows.append(row)

    df = pd.DataFrame(rows)

    for column in FEATURE_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    return df[FEATURE_COLUMNS]