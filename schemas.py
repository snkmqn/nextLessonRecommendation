from __future__ import annotations

from pydantic import BaseModel, Field


class NextLessonRankItem(BaseModel):
    candidate_subtopic_code: str = Field(..., min_length=1)

    user_level_num: int
    practical_experience_num: int
    learning_goal_num: int
    time_commitment_minutes: int

    completed_subtopics_count: int
    completion_ratio: float
    average_best_score_percent: float
    average_all_attempts_score_percent: float
    last_quiz_score: float
    failed_quiz_count: int
    days_since_last_activity: int

    candidate_level_num: int
    candidate_topic_order_index: int
    candidate_subtopic_order_index: int
    candidate_estimated_minutes: int

    is_preferred_topic: int
    is_same_topic_as_last_completed: int
    is_next_subtopic_in_same_topic: int
    is_first_subtopic_in_topic: int
    is_level_match: int
    is_time_commitment_match: int
    is_topic_not_started: int
    is_topic_in_progress: int

    need_reinforcement: int
    last_score_for_candidate: float
    best_score_for_candidate: float
    attempts_for_candidate: int


class NextLessonRankRequest(BaseModel):
    items: list[NextLessonRankItem]


class NextLessonRankResult(BaseModel):
    candidate_subtopic_code: str
    score: float


class NextLessonRankResponse(BaseModel):
    items: list[NextLessonRankResult]
    model_name: str
    model_version: str