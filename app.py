from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException

from model_loader import ModelBundle, load_model_bundle
from preprocessing import items_to_dataframe
from schemas import (
    NextLessonRankRequest,
    NextLessonRankResponse,
    NextLessonRankResult,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("next_lesson_ranker_ml")


app = FastAPI(
    title="Next Lesson Recommendation ML Service",
    version="1.0.0",
)

model_bundle: ModelBundle | None = None


@app.on_event("startup")
def startup() -> None:
    global model_bundle

    try:
        model_bundle = load_model_bundle()
        logger.info(
            "Model loaded successfully: model=%s version=%s",
            model_bundle.model_name,
            model_bundle.model_version,
        )
    except Exception:
        logger.exception("Failed to load next lesson ranker model")
        raise


@app.get("/health")
def health() -> dict:
    logger.info("Health check requested")

    return {
        "status": "ok",
        "model_loaded": model_bundle is not None,
        "model_name": model_bundle.model_name if model_bundle else None,
        "model_version": model_bundle.model_version if model_bundle else None,
    }


@app.post("/rank/next-lessons", response_model=NextLessonRankResponse)
def rank_next_lessons(request: NextLessonRankRequest) -> NextLessonRankResponse:
    if model_bundle is None:
        logger.error("Rank request rejected: model is not loaded")
        raise HTTPException(status_code=503, detail="MODEL_NOT_LOADED")

    logger.info(
        "Rank request received: candidates=%d",
        len(request.items),
    )

    if not request.items:
        logger.info("Rank response generated: empty request")

        return NextLessonRankResponse(
            items=[],
            model_name=model_bundle.model_name,
            model_version=model_bundle.model_version,
        )

    first_candidates = [
        item.candidate_subtopic_code
        for item in request.items[:5]
    ]

    logger.info(
        "First candidates: %s",
        first_candidates,
    )

    try:
        raw_items = [item.model_dump() for item in request.items]
        df = items_to_dataframe(raw_items)

        logger.info(
            "DataFrame prepared: rows=%d columns=%d",
            df.shape[0],
            df.shape[1],
        )

        predictions = model_bundle.model.predict(df)

    except Exception as exc:
        logger.exception("Ranking prediction failed")
        raise HTTPException(status_code=500, detail="RANKING_PREDICTION_FAILED") from exc

    results = []

    for item, score in zip(request.items, predictions):
        results.append(
            NextLessonRankResult(
                candidate_subtopic_code=item.candidate_subtopic_code,
                score=float(score),
            )
        )

    results.sort(key=lambda x: x.score, reverse=True)

    top3 = [
        {
            "candidate_subtopic_code": item.candidate_subtopic_code,
            "score": round(item.score, 6),
        }
        for item in results[:3]
    ]

    logger.info(
        "Rank response generated: results=%d top3=%s",
        len(results),
        top3,
    )

    return NextLessonRankResponse(
        items=results,
        model_name=model_bundle.model_name,
        model_version=model_bundle.model_version,
    )