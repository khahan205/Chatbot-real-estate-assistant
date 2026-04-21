"""Model-backed recommendation service."""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from . import config
from .fallback import recommend_with_fallback
from .feature_pipeline import (
    FeatureAlignmentError,
    align_model_features,
    load_listings,
    normalize_listings,
)
from .preference_matching import (
    build_reason_flags,
    build_recommendation_item,
    filter_with_relaxation,
    preference_score,
)
from .schemas import PreferenceRequest, RecommendationResponse


class ModelLoadError(RuntimeError):
    """Raised when the model artifact or metadata cannot be loaded."""


@dataclass(frozen=True)
class ModelArtifact:
    model: Any
    feature_columns: list[str]
    feature_source: str


def load_feature_columns_from_json(path: Path = config.FEATURE_COLUMNS_PATH) -> list[str] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        raise ModelLoadError(f"Invalid feature metadata in {path}")
    return data


def load_model_artifact(
    model_path: Path = config.MODEL_PATH,
    feature_columns_path: Path = config.FEATURE_COLUMNS_PATH,
) -> ModelArtifact:
    if not model_path.exists():
        raise ModelLoadError(f"Model artifact not found: {model_path}")

    with model_path.open("rb") as f:
        artifact = pickle.load(f)

    if isinstance(artifact, dict):
        model = artifact.get("model")
        embedded_feature_columns = artifact.get("feature_cols") or artifact.get("feature_columns")
    else:
        model = artifact
        embedded_feature_columns = None

    if model is None:
        raise ModelLoadError("Model artifact did not contain a model object.")

    json_feature_columns = load_feature_columns_from_json(feature_columns_path)
    if json_feature_columns:
        feature_columns = json_feature_columns
        feature_source = str(feature_columns_path)
    elif embedded_feature_columns:
        feature_columns = list(embedded_feature_columns)
        feature_source = f"{model_path}:feature_cols"
    else:
        raise ModelLoadError("No model feature column metadata was found.")

    if not feature_columns or not all(isinstance(column, str) for column in feature_columns):
        raise ModelLoadError("Feature column metadata must be a non-empty list of strings.")

    return ModelArtifact(model=model, feature_columns=feature_columns, feature_source=feature_source)


def normalize_model_scores(raw_scores: Any) -> np.ndarray:
    scores = np.asarray(raw_scores, dtype=float).reshape(-1)
    if scores.size == 0:
        return scores

    finite_mask = np.isfinite(scores)
    if not finite_mask.any():
        return np.zeros_like(scores, dtype=float)

    finite_scores = scores[finite_mask]
    minimum = float(finite_scores.min())
    maximum = float(finite_scores.max())

    normalized = np.zeros_like(scores, dtype=float)
    if minimum >= 0 and maximum <= 1:
        normalized[finite_mask] = finite_scores
    elif minimum >= 0 and maximum <= 100:
        normalized[finite_mask] = finite_scores / 100
    elif maximum - minimum > 0:
        normalized[finite_mask] = (finite_scores - minimum) / (maximum - minimum)
    else:
        normalized[finite_mask] = 0

    return np.clip(normalized, 0, 1)


def predict_model_scores(model: Any, features: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        raw_scores = model.predict_proba(features)
        raw_scores = np.asarray(raw_scores)
        if raw_scores.ndim == 2 and raw_scores.shape[1] > 1:
            raw_scores = raw_scores[:, 1]
    else:
        raw_scores = model.predict(features)
    return normalize_model_scores(raw_scores)


def rank_candidates(
    candidates: pd.DataFrame,
    model: Any,
    feature_columns: list[str],
    preferences: PreferenceRequest,
) -> pd.DataFrame:
    features = align_model_features(candidates, feature_columns)
    ranked = candidates.copy()
    ranked["model_score"] = predict_model_scores(model, features)

    preference_scores = []
    for _, row in ranked.iterrows():
        preference_scores.append(preference_score(build_reason_flags(row, preferences)))
    ranked["preference_score"] = preference_scores
    ranked["matching_score"] = (0.7 * ranked["model_score"] + 0.3 * ranked["preference_score"]).clip(0, 1)

    return ranked.sort_values("matching_score", ascending=False)


class YodogawaRecommender:
    def __init__(
        self,
        *,
        listings_path: Path = config.LISTINGS_CSV,
        model_path: Path = config.MODEL_PATH,
        feature_columns_path: Path = config.FEATURE_COLUMNS_PATH,
    ) -> None:
        self.listings_path = listings_path
        self.model_path = model_path
        self.feature_columns_path = feature_columns_path

    def load_raw_listings(self) -> pd.DataFrame:
        if not self.listings_path.exists():
            raise FileNotFoundError(f"Listings CSV not found: {self.listings_path}")
        return load_listings(self.listings_path)

    def load_model(self) -> ModelArtifact:
        return load_model_artifact(self.model_path, self.feature_columns_path)

    def recommend(self, preferences: PreferenceRequest) -> RecommendationResponse:
        raw_listings = self.load_raw_listings()
        warnings = [
            "Current model is weakly preference-aware; deterministic preference flags are blended for personalization."
        ]

        try:
            normalized = normalize_listings(raw_listings)
            candidates, filter_warnings = filter_with_relaxation(normalized, preferences)
            warnings.extend(filter_warnings)

            artifact = self.load_model()
            ranked = rank_candidates(candidates, artifact.model, artifact.feature_columns, preferences)

            recommendations = []
            for _, row in ranked.head(preferences.limit).iterrows():
                recommendations.append(
                    build_recommendation_item(
                        row,
                        preferences,
                        matching_score=row["matching_score"],
                        model_score=row["model_score"],
                        preference_score_value=row["preference_score"],
                    )
                )

            return RecommendationResponse(
                recommendations=recommendations,
                ranking_mode="model",
                warnings=warnings,
            )
        except (ModelLoadError, FeatureAlignmentError, ImportError, ModuleNotFoundError, AttributeError, ValueError) as exc:
            warnings.append(f"Model ranking unavailable: {exc}")
            return recommend_with_fallback(raw_listings, preferences, warnings=warnings)

    def health(self) -> dict[str, Any]:
        warnings: list[str] = []
        listings_count: int | None = None

        if self.listings_path.exists():
            try:
                listings_count = int(len(load_listings(self.listings_path)))
            except Exception as exc:  # pragma: no cover - health must stay defensive.
                warnings.append(f"Could not load listings CSV: {exc}")

        feature_columns: list[str] = []
        model_loadable = False
        try:
            artifact = self.load_model()
            feature_columns = artifact.feature_columns
            model_loadable = True
        except Exception as exc:  # pragma: no cover - depends on local artifacts/deps.
            warnings.append(f"Could not load model artifact: {exc}")

        status = "ok" if self.listings_path.exists() and self.model_path.exists() and model_loadable else "degraded"
        return {
            "status": status,
            "listings_path_exists": self.listings_path.exists(),
            "model_path_exists": self.model_path.exists(),
            "feature_metadata_path_exists": self.feature_columns_path.exists(),
            "listings_count": listings_count,
            "model_loadable": model_loadable,
            "feature_columns": feature_columns,
            "warnings": warnings,
        }

