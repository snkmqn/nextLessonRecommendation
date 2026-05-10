# Next Lesson Recommendation ML Service

This project is an ML service for ranking next lesson candidates in a financial literacy learning application.

The service receives candidate subtopics from the backend, analyzes user profile data, learning progress, quiz history, activity information, and candidate lesson features, then returns the candidates sorted by predicted relevance.

## Project Structure

```text
nextLessonRecommendation/
├── app.py
├── train_next_lesson_ranker.py
├── generate_next_lesson_ranker_dataset.py
├── model_loader.py
├── preprocessing.py
├── schemas.py
├── requirements.txt
├── data/
│   ├── next_lesson_ranker_train.csv
│   └── next_lesson_ranker_test.csv
├── models/
│   ├── next_lesson_ranker_lgbm.pkl
│   └── next_lesson_ranker_metadata.json
└── README.md
```

## Requirements

- Python 3.10+
- pip
- Git

Check Python version:

```bash
python --version
```

## Installation

Clone the repository:

```bash
git clone https://github.com/snkmqn/nextLessonRecommendation.git
cd nextLessonRecommendation
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\activate
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Dataset Generation

The project uses a synthetic dataset for training and testing the ranking model.

To generate the dataset, run:

```bash
python generate_next_lesson_ranker_dataset.py
```

The generated files will be saved to:

```text
data/next_lesson_ranker_train.csv
data/next_lesson_ranker_test.csv
```

## Training the Model

To train the model, run:

```bash
python train_next_lesson_ranker.py
```

The trained model will be saved to:

```text
models/next_lesson_ranker_lgbm.pkl
```

Model metadata will be saved to:

```text
models/next_lesson_ranker_metadata.json
```

The metadata file contains the model name, model version, feature columns, dataset sizes, group counts, and evaluation metrics.

## Running the API

Start the service:

```bash
uvicorn app:app --reload
```

The API will be available locally at:

```text
http://127.0.0.1:8000
```

## Health Check Endpoint

Endpoint:

```text
GET /health
```

Example request:

```text
GET http://127.0.0.1:8000/health
```

Example response:

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_name": "next_lesson_ranker_lgbm",
  "model_version": "v2"
}
```

## Ranking Endpoint

Endpoint:

```text
POST /rank/next-lessons
```

Example request:

```text
POST http://127.0.0.1:8000/rank/next-lessons
```

Example request body:

```json
{
  "items": [
    {
      "candidate_subtopic_code": "fixed_variable_expenses",
      "user_level_num": 0,
      "practical_experience_num": 1,
      "learning_goal_num": 1,
      "time_commitment_minutes": 10,
      "completed_subtopics_count": 1,
      "completion_ratio": 0.04,
      "average_best_score_percent": 85.0,
      "average_all_attempts_score_percent": 82.0,
      "last_quiz_score": 85.0,
      "failed_quiz_count": 0,
      "days_since_last_activity": 2,
      "candidate_level_num": 0,
      "candidate_topic_order_index": 1,
      "candidate_subtopic_order_index": 2,
      "candidate_estimated_minutes": 5,
      "is_preferred_topic": 1,
      "is_same_topic_as_last_completed": 1,
      "is_next_subtopic_in_same_topic": 1,
      "is_first_subtopic_in_topic": 0,
      "is_level_match": 1,
      "is_time_commitment_match": 1,
      "is_topic_not_started": 0,
      "is_topic_in_progress": 1,
      "need_reinforcement": 0,
      "last_score_for_candidate": -1,
      "best_score_for_candidate": -1,
      "attempts_for_candidate": 0
    },
    {
      "candidate_subtopic_code": "why_save",
      "user_level_num": 0,
      "practical_experience_num": 1,
      "learning_goal_num": 1,
      "time_commitment_minutes": 10,
      "completed_subtopics_count": 1,
      "completion_ratio": 0.04,
      "average_best_score_percent": 85.0,
      "average_all_attempts_score_percent": 82.0,
      "last_quiz_score": 85.0,
      "failed_quiz_count": 0,
      "days_since_last_activity": 2,
      "candidate_level_num": 0,
      "candidate_topic_order_index": 2,
      "candidate_subtopic_order_index": 1,
      "candidate_estimated_minutes": 5,
      "is_preferred_topic": 1,
      "is_same_topic_as_last_completed": 0,
      "is_next_subtopic_in_same_topic": 0,
      "is_first_subtopic_in_topic": 1,
      "is_level_match": 1,
      "is_time_commitment_match": 1,
      "is_topic_not_started": 1,
      "is_topic_in_progress": 0,
      "need_reinforcement": 0,
      "last_score_for_candidate": -1,
      "best_score_for_candidate": -1,
      "attempts_for_candidate": 0
    }
  ]
}
```

Example response:

```json
{
  "items": [
    {
      "candidate_subtopic_code": "fixed_variable_expenses",
      "score": 2.4186
    },
    {
      "candidate_subtopic_code": "why_save",
      "score": 1.9043
    }
  ],
  "model_name": "next_lesson_ranker_lgbm",
  "model_version": "v2"
}
```

## Request Fields

| Field | Description |
|---|---|
| `candidate_subtopic_code` | Candidate subtopic identifier. |
| `user_level_num` | Encoded user financial literacy level. |
| `practical_experience_num` | Encoded practical experience level. |
| `learning_goal_num` | Encoded learning goal. |
| `time_commitment_minutes` | User's available learning time in minutes. |
| `completed_subtopics_count` | Number of successfully completed subtopics. |
| `completion_ratio` | Ratio of completed subtopics to total subtopics. |
| `average_best_score_percent` | Average best score across attempted quizzes. |
| `average_all_attempts_score_percent` | Average score across all completed quiz attempts. |
| `last_quiz_score` | Score of the latest completed quiz attempt. |
| `failed_quiz_count` | Number of quizzes where the latest attempt is below the passing score. |
| `days_since_last_activity` | Number of days since the user's last learning activity. |
| `candidate_level_num` | Encoded level of the candidate subtopic. |
| `candidate_topic_order_index` | Order index of the candidate topic. |
| `candidate_subtopic_order_index` | Order index of the candidate subtopic within the topic. |
| `candidate_estimated_minutes` | Estimated time required to complete the candidate subtopic. |
| `is_preferred_topic` | Whether the candidate topic matches the user's preferred topics. |
| `is_same_topic_as_last_completed` | Whether the candidate belongs to the same topic as the latest completed subtopic. |
| `is_next_subtopic_in_same_topic` | Whether the candidate is the next logical subtopic in the same topic. |
| `is_first_subtopic_in_topic` | Whether the candidate is the first subtopic of its topic. |
| `is_level_match` | Whether the candidate level matches the user's level. |
| `is_time_commitment_match` | Whether the candidate duration fits the user's time commitment. |
| `is_topic_not_started` | Whether the user has not started the candidate topic. |
| `is_topic_in_progress` | Whether the user has already started the candidate topic. |
| `need_reinforcement` | Whether the candidate is related to reinforcement. |
| `last_score_for_candidate` | Latest score for the candidate subtopic, or `-1` if the user has not attempted it. |
| `best_score_for_candidate` | Best historical score for the candidate subtopic, or `-1` if the user has not attempted it. |
| `attempts_for_candidate` | Number of attempts for the candidate subtopic. |

## Model Details

The service uses a LightGBM ranking model:

```text
LightGBM LGBMRanker
```

The model objective is:

```text
lambdarank
```

The target column is:

```text
relevance
```

The model ranks candidate lessons within the same user group. Each group represents one recommendation request for one user. The service returns a predicted score for each candidate, and the backend can sort candidates by this score in descending order.

## Feature Columns

The model is trained using the following feature columns:

```text
user_level_num
practical_experience_num
learning_goal_num
time_commitment_minutes
completed_subtopics_count
completion_ratio
average_best_score_percent
average_all_attempts_score_percent
last_quiz_score
failed_quiz_count
days_since_last_activity
candidate_level_num
candidate_topic_order_index
candidate_subtopic_order_index
candidate_estimated_minutes
is_preferred_topic
is_same_topic_as_last_completed
is_next_subtopic_in_same_topic
is_first_subtopic_in_topic
is_level_match
is_time_commitment_match
is_topic_not_started
is_topic_in_progress
need_reinforcement
last_score_for_candidate
best_score_for_candidate
attempts_for_candidate
```

## Evaluation Metrics

The model is evaluated using NDCG metrics:

```text
NDCG@1
NDCG@3
NDCG@5
```

These metrics evaluate whether the most relevant candidate lessons are ranked near the top of the recommendation list.

The exact metric values are stored in:

```text
models/next_lesson_ranker_metadata.json
```

## Backend Integration

The backend service prepares candidate lessons and feature values, sends them to this ML service, and uses the returned scores to rank the candidates.

Recommended backend flow:

```text
1. Build candidate subtopics.
2. Calculate user profile, progress, activity, and candidate features.
3. Send all candidates to POST /rank/next-lessons.
4. Receive predicted scores.
5. Sort candidates by score in descending order.
6. Use the highest-ranked candidates as next lesson recommendations.
```

If the ML service is unavailable, the backend should use a rule-based fallback recommendation strategy.

## Notes

The dataset is synthetic and does not contain real user personal data.

The ML service is responsible only for ranking already prepared candidates. Core application logic such as quiz submission, score calculation, XP assignment, progress updates, and learning statistics calculation must remain on the backend side.
