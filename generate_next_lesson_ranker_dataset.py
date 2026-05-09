import csv
import random
from dataclasses import dataclass
from pathlib import Path


RANDOM_SEED = 42
SYNTHETIC_USERS_COUNT = 3000

OUTPUT_DIR = Path("data")
TRAIN_PATH = OUTPUT_DIR / "next_lesson_ranker_train.csv"
TEST_PATH = OUTPUT_DIR / "next_lesson_ranker_test.csv"


@dataclass(frozen=True)
class Subtopic:
    topic_code: str
    subtopic_code: str
    topic_level_num: int
    topic_order_index: int
    subtopic_order_index: int
    estimated_minutes: int


SUBTOPICS = [
    # budgeting, beginner
    Subtopic("budgeting", "income_expenses", 0, 1, 1, 5),
    Subtopic("budgeting", "fixed_variable_expenses", 0, 1, 2, 5),
    Subtopic("budgeting", "expense_accounting", 0, 1, 3, 5),
    Subtopic("budgeting", "budgeting_rule_50_30_20", 0, 1, 4, 5),
    Subtopic("budgeting", "budget_analysis", 0, 1, 5, 5),

    # savings, beginner
    Subtopic("savings", "why_save", 0, 2, 1, 5),
    Subtopic("savings", "emergency_fund", 0, 2, 2, 10),
    Subtopic("savings", "how_to_save", 0, 2, 3, 10),
    Subtopic("savings", "interest_on_savings", 0, 2, 4, 10),
    Subtopic("savings", "saving_mistakes", 0, 2, 5, 5),

    # credit_and_debt, intermediate
    Subtopic("credit_and_debt", "what_is_credit", 2, 1, 1, 5),
    Subtopic("credit_and_debt", "interest_rate", 2, 1, 2, 10),
    Subtopic("credit_and_debt", "credit_overpayment", 2, 1, 3, 10),
    Subtopic("credit_and_debt", "credit_load", 2, 1, 4, 10),
    Subtopic("credit_and_debt", "choose_credit", 2, 1, 5, 10),

    # financial_planning, intermediate
    Subtopic("financial_planning", "financial_goals", 2, 2, 1, 5),
    Subtopic("financial_planning", "short_vs_long_goals", 2, 2, 2, 10),
    Subtopic("financial_planning", "spending_priorities", 2, 2, 3, 10),
    Subtopic("financial_planning", "savings_plan", 2, 2, 4, 10),
    Subtopic("financial_planning", "progress_control", 2, 2, 5, 10),

    # investments, advanced
    Subtopic("investments", "what_are_investments", 3, 1, 1, 10),
    Subtopic("investments", "risk_and_return", 3, 1, 2, 10),
    Subtopic("investments", "diversification", 3, 1, 3, 15),
    Subtopic("investments", "simple_instruments", 3, 1, 4, 15),
    Subtopic("investments", "beginner_mistakes", 3, 1, 5, 10),
]


TOPICS = sorted(set(s.topic_code for s in SUBTOPICS))

TOPIC_TO_SUBTOPICS = {}
for subtopic in SUBTOPICS:
    TOPIC_TO_SUBTOPICS.setdefault(subtopic.topic_code, []).append(subtopic)

for items in TOPIC_TO_SUBTOPICS.values():
    items.sort(key=lambda x: x.subtopic_order_index)


def content_topic_to_preferred_topic_code(topic_code: str) -> str:
    if topic_code == "credit_and_debt":
        return "credits_and_debts"
    if topic_code == "investments":
        return "investing"
    return topic_code


PREFERRED_TOPIC_CODES = [
    "budgeting",
    "savings",
    "credits_and_debts",
    "financial_planning",
    "investing",
]


def bool_to_int(value: bool) -> int:
    return 1 if value else 0


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def pick_preferred_topics(user_level_num: int) -> list[str]:
    if user_level_num == 0:
        weights = {
            "budgeting": 4,
            "savings": 4,
            "credits_and_debts": 2,
            "financial_planning": 2,
            "investing": 1,
        }
    elif user_level_num == 1:
        weights = {
            "budgeting": 3,
            "savings": 3,
            "credits_and_debts": 3,
            "financial_planning": 3,
            "investing": 1,
        }
    elif user_level_num == 2:
        weights = {
            "budgeting": 2,
            "savings": 2,
            "credits_and_debts": 4,
            "financial_planning": 4,
            "investing": 2,
        }
    else:
        weights = {
            "budgeting": 1,
            "savings": 2,
            "credits_and_debts": 3,
            "financial_planning": 3,
            "investing": 4,
        }

    count = random.choice([1, 2, 2, 3])
    available = PREFERRED_TOPIC_CODES[:]
    selected = []

    for _ in range(count):
        total = sum(weights[x] for x in available)
        r = random.uniform(0, total)
        acc = 0
        chosen = available[-1]

        for topic in available:
            acc += weights[topic]
            if r <= acc:
                chosen = topic
                break

        selected.append(chosen)
        available.remove(chosen)

    return selected


def generate_completed_subtopics(user_level_num: int) -> dict[str, float]:
    completed = {}

    if user_level_num == 0:
        max_completed = random.randint(0, 7)
    elif user_level_num == 1:
        max_completed = random.randint(0, 10)
    elif user_level_num == 2:
        max_completed = random.randint(3, 17)
    else:
        max_completed = random.randint(8, 24)

    ordered = SUBTOPICS[:]

    # Пользователь чаще проходит beginner/intermediate раньше advanced.
    ordered.sort(key=lambda s: (s.topic_level_num, s.topic_order_index, s.subtopic_order_index))

    for subtopic in ordered[:max_completed]:
        # completed значит >= 70
        completed[subtopic.subtopic_code] = round(random.uniform(70, 100), 2)

    return completed


def generate_failed_subtopics(completed: dict[str, float]) -> dict[str, float]:
    failed = {}

    available = [s for s in SUBTOPICS if s.subtopic_code not in completed]
    random.shuffle(available)

    failed_count = random.choices([0, 1, 2, 3], weights=[5, 3, 1, 1])[0]

    for subtopic in available[:failed_count]:
        failed[subtopic.subtopic_code] = round(random.uniform(20, 69.99), 2)

    return failed


def latest_completed_topic(completed: dict[str, float]) -> str | None:
    completed_subtopics = [
        s for s in SUBTOPICS
        if s.subtopic_code in completed
    ]

    if not completed_subtopics:
        return None

    # Упрощённо считаем, что последний — самый поздний по порядку обучения.
    completed_subtopics.sort(
        key=lambda s: (s.topic_level_num, s.topic_order_index, s.subtopic_order_index)
    )

    return completed_subtopics[-1].topic_code


def max_completed_order_in_topic(topic_code: str, completed: dict[str, float]) -> int:
    max_order = 0

    for subtopic in TOPIC_TO_SUBTOPICS[topic_code]:
        if subtopic.subtopic_code in completed:
            max_order = max(max_order, subtopic.subtopic_order_index)

    return max_order


def topic_has_completed(topic_code: str, completed: dict[str, float]) -> bool:
    return any(s.subtopic_code in completed for s in TOPIC_TO_SUBTOPICS[topic_code])


def topic_not_started(topic_code: str, completed: dict[str, float], failed: dict[str, float]) -> bool:
    for subtopic in TOPIC_TO_SUBTOPICS[topic_code]:
        if subtopic.subtopic_code in completed or subtopic.subtopic_code in failed:
            return False
    return True


def is_next_subtopic_in_same_topic(candidate: Subtopic, completed: dict[str, float]) -> bool:
    max_order = max_completed_order_in_topic(candidate.topic_code, completed)
    return max_order > 0 and candidate.subtopic_order_index == max_order + 1


def is_level_match(user_level_num: int, candidate_level_num: int) -> bool:
    return candidate_level_num <= user_level_num + 1


def time_commitment_match(time_commitment_minutes: int, estimated_minutes: int) -> bool:
    return estimated_minutes <= time_commitment_minutes


def score_to_relevance(score: float) -> int:
    if score <= 0:
        return 0
    if score <= 3:
        return 1
    if score <= 6:
        return 2
    return 3


def make_row(user_id: int, candidate: Subtopic, user: dict) -> dict:
    completed = user["completed"]
    failed = user["failed"]

    is_completed = candidate.subtopic_code in completed
    is_failed = candidate.subtopic_code in failed

    preferred_topic_code = content_topic_to_preferred_topic_code(candidate.topic_code)

    is_preferred_topic = preferred_topic_code in user["preferred_topics"]
    last_topic = latest_completed_topic(completed)

    is_same_topic_as_last_completed = last_topic == candidate.topic_code
    is_next = is_next_subtopic_in_same_topic(candidate, completed)

    is_first = candidate.subtopic_order_index == 1
    level_match = is_level_match(user["user_level_num"], candidate.topic_level_num)
    time_match = time_commitment_match(user["time_commitment_minutes"], candidate.estimated_minutes)
    not_started = topic_not_started(candidate.topic_code, completed, failed)
    in_progress = topic_has_completed(candidate.topic_code, completed)

    need_reinforcement = 1 if user["need_reinforcement"] else 0
    is_reinforcement_subtopic = user["reinforcement_subtopic_code"] == candidate.subtopic_code

    last_score_for_candidate = -1
    best_score_for_candidate = -1
    attempts_for_candidate = 0

    if is_completed:
        best_score_for_candidate = completed[candidate.subtopic_code]
        last_score_for_candidate = best_score_for_candidate
        attempts_for_candidate = random.randint(1, 3)

    if is_failed:
        best_score_for_candidate = failed[candidate.subtopic_code]
        last_score_for_candidate = best_score_for_candidate
        attempts_for_candidate = random.randint(1, 3)

    # Candidate filtering как на backend:
    # completed subtopic не должен быть нормальным кандидатом.
    # Но в dataset оставляем его с relevance 0, чтобы модель училась не выбирать такие случаи.
    rule_score = 0

    if is_completed:
        rule_score -= 10

    if is_reinforcement_subtopic:
        rule_score -= 5

    if is_next:
        rule_score += 4

    if is_preferred_topic:
        rule_score += 3

    if level_match:
        rule_score += 2
    else:
        rule_score -= 3

    if time_match:
        rule_score += 1
    else:
        rule_score -= 1

    if in_progress:
        rule_score += 1

    if is_first and is_preferred_topic:
        rule_score += 1

    if need_reinforcement and candidate.topic_level_num > user["user_level_num"]:
        rule_score -= 2

    # Если пользователь ещё ничего не проходил, первые подтемы preferred beginner topics должны быть сильнее.
    if user["completed_subtopics_count"] == 0 and is_first and is_preferred_topic and level_match:
        rule_score += 3

    # Если candidate failed, но не reinforcement, можно рекомендовать позже, но слабее.
    if is_failed and not is_reinforcement_subtopic:
        rule_score -= 2

    relevance = score_to_relevance(rule_score)

    return {
        "group_id": user_id,
        "user_id": user_id,
        "candidate_subtopic_code": candidate.subtopic_code,

        "user_level_num": user["user_level_num"],
        "practical_experience_num": user["practical_experience_num"],
        "learning_goal_num": user["learning_goal_num"],
        "time_commitment_minutes": user["time_commitment_minutes"],

        "completed_subtopics_count": user["completed_subtopics_count"],
        "completion_ratio": round(user["completed_subtopics_count"] / len(SUBTOPICS), 4),
        "average_best_score_percent": user["average_best_score_percent"],
        "average_all_attempts_score_percent": user["average_all_attempts_score_percent"],
        "last_quiz_score": user["last_quiz_score"],
        "failed_quiz_count": user["failed_quiz_count"],
        "days_since_last_activity": user["days_since_last_activity"],

        "candidate_level_num": candidate.topic_level_num,
        "candidate_topic_order_index": candidate.topic_order_index,
        "candidate_subtopic_order_index": candidate.subtopic_order_index,
        "candidate_estimated_minutes": candidate.estimated_minutes,

        "is_preferred_topic": bool_to_int(is_preferred_topic),
        "is_same_topic_as_last_completed": bool_to_int(is_same_topic_as_last_completed),
        "is_next_subtopic_in_same_topic": bool_to_int(is_next),
        "is_first_subtopic_in_topic": bool_to_int(is_first),
        "is_level_match": bool_to_int(level_match),
        "is_time_commitment_match": bool_to_int(time_match),
        "is_topic_not_started": bool_to_int(not_started),
        "is_topic_in_progress": bool_to_int(in_progress),

        "need_reinforcement": need_reinforcement,
        "last_score_for_candidate": last_score_for_candidate,
        "best_score_for_candidate": best_score_for_candidate,
        "attempts_for_candidate": attempts_for_candidate,

        "relevance": relevance,
    }


def generate_user(user_id: int) -> dict:
    user_level_num = random.choices(
        [0, 1, 2, 3],
        weights=[45, 20, 25, 10],
    )[0]

    practical_experience_num = clamp(
        round(random.gauss(user_level_num, 1)),
        0,
        3,
    )
    practical_experience_num = int(practical_experience_num)

    if user_level_num == 0:
        learning_goal_num = random.choice([0, 1, 5, 6])
    elif user_level_num == 1:
        learning_goal_num = random.choice([0, 1, 2, 3, 5, 6])
    elif user_level_num == 2:
        learning_goal_num = random.choice([2, 3, 4, 6, 7])
    else:
        learning_goal_num = random.choice([3, 4, 7])

    time_commitment_minutes = random.choices(
        [5, 10, 15, 20],
        weights=[25, 40, 25, 10],
    )[0]

    preferred_topics = pick_preferred_topics(user_level_num)

    completed = generate_completed_subtopics(user_level_num)
    failed = generate_failed_subtopics(completed)

    completed_scores = list(completed.values())
    failed_scores = list(failed.values())
    all_scores = completed_scores + failed_scores

    if completed_scores:
        average_best_score_percent = round(sum(completed_scores) / len(completed_scores), 2)
    else:
        average_best_score_percent = 0

    if all_scores:
        average_all_attempts_score_percent = round(sum(all_scores) / len(all_scores), 2)
        last_quiz_score = random.choice(all_scores)
    else:
        average_all_attempts_score_percent = 0
        last_quiz_score = -1

    need_reinforcement = False
    reinforcement_subtopic_code = ""

    if failed:
        need_reinforcement = random.choices([True, False], weights=[7, 3])[0]

    if need_reinforcement:
        reinforcement_subtopic_code = min(
            failed.items(),
            key=lambda item: item[1],
        )[0]

    return {
        "user_level_num": user_level_num,
        "practical_experience_num": practical_experience_num,
        "learning_goal_num": learning_goal_num,
        "time_commitment_minutes": time_commitment_minutes,
        "preferred_topics": preferred_topics,
        "completed": completed,
        "failed": failed,
        "need_reinforcement": need_reinforcement,
        "reinforcement_subtopic_code": reinforcement_subtopic_code,
        "completed_subtopics_count": len(completed),
        "average_best_score_percent": average_best_score_percent,
        "average_all_attempts_score_percent": average_all_attempts_score_percent,
        "last_quiz_score": last_quiz_score,
        "failed_quiz_count": len(failed),
        "days_since_last_activity": random.randint(0, 30),
    }


def generate_dataset() -> list[dict]:
    random.seed(RANDOM_SEED)

    rows = []

    for user_id in range(1, SYNTHETIC_USERS_COUNT + 1):
        user = generate_user(user_id)

        for candidate in SUBTOPICS:
            rows.append(make_row(user_id, candidate, user))

    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("No rows to write")

    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(rows[0].keys())

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def split_train_test(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    train_rows = []
    test_rows = []

    test_user_mod = 5

    for row in rows:
        if row["user_id"] % test_user_mod == 0:
            test_rows.append(row)
        else:
            train_rows.append(row)

    return train_rows, test_rows


def main() -> None:
    rows = generate_dataset()
    train_rows, test_rows = split_train_test(rows)

    write_csv(TRAIN_PATH, train_rows)
    write_csv(TEST_PATH, test_rows)

    print(f"Generated rows: {len(rows)}")
    print(f"Train rows: {len(train_rows)} -> {TRAIN_PATH}")
    print(f"Test rows: {len(test_rows)} -> {TEST_PATH}")


if __name__ == "__main__":
    main()