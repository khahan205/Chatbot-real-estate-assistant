"""Runtime configuration and artifact paths for the backend service."""

from __future__ import annotations

from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
DATA_DIR = REPO_ROOT / "data"
MODEL_DIR = REPO_ROOT / "model"

LISTINGS_CSV = DATA_DIR / "yodogawa_feature_eng.csv"
MODEL_PATH = MODEL_DIR / "yodogawa_match_model.pkl"
FEATURE_COLUMNS_PATH = MODEL_DIR / "feature_columns.json"

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

