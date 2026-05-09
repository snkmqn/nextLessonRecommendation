# Next Lesson Recommendation ML Service

This project is an ML service for ranking the best next lesson candidates for a user in a financial literacy learning application.

The model analyzes the user learning profile, progress history, quiz results, preferred topics, and candidate lesson features, then returns a sorted list of recommended next subtopics.

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

Install dependencies:

```bash
pip install -r requirements.txt
```

## Generating the Dataset

To generate the synthetic dataset again, run:

```bash
python generate_next_lesson_ranker_dataset.py
```

The generated datasets will be saved to:

```text
data/next_lesson_ranker_train.csv
data/next_lesson_ranker_test.csv
```

## Training the Model

To train the model again, run:

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

## Running the API

Start the service:

```bash
uvicorn app:app --reload
```

The API will be available locally, for example:

```text
http://127.0.0.1:8000
```

## Health Check Endpoint

Example endpoint:

```text
GET http://127.0.0.1:8000/health
```

Example response:

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_name": "next_lesson_ranker_lgbm",
  "model_version": "v1"
}
```

## Ranking Endpoint

Example endpoint:

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
  "model_version": "v1"
}
```

## Model Details

The project uses a LightGBM ranking model:

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

The model ranks candidate lessons inside one user group and returns candidates ordered by predicted score.

## Metrics

Current model metadata contains the following evaluation metrics:

```text
NDCG@1 = 1.0
NDCG@3 = 0.998367
NDCG@5 = 0.996309
```

## Notes

The project uses a synthetic dataset for training and testing:

```text
data/next_lesson_ranker_train.csv
data/next_lesson_ranker_test.csv
```

The model does not store real user personal data in this repository.

The backend service should prepare candidate lessons, send them to this ML service, and use the returned ranking to choose the most suitable next lesson for the user.