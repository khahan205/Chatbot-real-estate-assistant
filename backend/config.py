"""Runtime configuration and artifact paths for the backend service."""

from __future__ import annotations

import os
from pathlib import Path


def _path_from_env(env_name: str, default: Path) -> Path:
    """Resolve a path from an environment variable, falling back to a repo path."""

    configured = os.getenv(env_name)
    if configured:
        return Path(configured).expanduser().resolve()
    return default


BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
DATA_DIR = _path_from_env("DATA_DIR", REPO_ROOT / "data")
MODEL_DIR = _path_from_env("MODEL_DIR", REPO_ROOT / "model")

LISTINGS_CSV = _path_from_env("LISTINGS_CSV_PATH", DATA_DIR / "yodogawa_feature_eng.csv")
MODEL_PATH = _path_from_env("MODEL_ARTIFACT_PATH", MODEL_DIR / "yodogawa_match_model.pkl")
FEATURE_COLUMNS_PATH = _path_from_env("FEATURE_COLUMNS_PATH", MODEL_DIR / "feature_columns.json")

DEFAULT_LIMIT = 5
MAX_LIMIT = 20

TRAINED_FEATURE_COLUMNS = [
    "rent",
    "management_fee",
    "area_m2",
    "building_age",
    "walking_distance_to_station",
    "floor",
    "pet_allowed",
    "cost_performance",
]

