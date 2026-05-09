from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "next_lesson_ranker_lgbm.pkl"
METADATA_PATH = BASE_DIR / "models" / "next_lesson_ranker_metadata.json"


class ModelBundle:
    def __init__(self, model: Any, metadata: dict):
        self.model = model
        self.metadata = metadata

    @property
    def model_name(self) -> str:
        return self.metadata.get("model_name", "next_lesson_ranker_lgbm")

    @property
    def model_version(self) -> str:
        return self.metadata.get("model_version", "v1")


def load_model_bundle() -> ModelBundle:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")

    with MODEL_PATH.open("rb") as file:
        model = pickle.load(file)

    with METADATA_PATH.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    return ModelBundle(model=model, metadata=metadata)