"""Rule-based fallback recommender adapted from the notebook flow."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .feature_pipeline import normalize_listings
from .preference_matching import (
    build_reason_flags,
    build_recommendation_item,
    filter_with_relaxation,
    preference_score,
)
from .schemas import PreferenceRequest, RecommendationResponse


def _norm(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    minimum = values.min()
    maximum = values.max()
    if maximum - minimum == 0:
        return values * 0
    return (values - minimum) / (maximum - minimum)


def _rule_rank(df: pd.DataFrame, preferences: PreferenceRequest) -> pd.DataFrame:
    ranked = df.copy()

    ideal_area = preferences.min_area_sqm if preferences.min_area_sqm else ranked["area_m2"].median()
    if not ideal_area or np.isnan(ideal_area):
        ideal_area = 25.0

    ranked["budget_score"] = 1 - _norm(ranked["total_cost_yen"])
    ranked["distance_score"] = 1 - _norm(ranked["walk_minutes"])
    ranked["size_score"] = np.exp(-abs(ranked["area_m2"] - ideal_area) / max(float(ideal_area), 1.0))
    ranked["age_score"] = 1 - _norm(ranked["building_age"])
    ranked["cost_performance_score"] = _norm(ranked["cost_performance"])

    ranked["rule_score"] = (
        ranked["budget_score"] * 0.30
        + ranked["distance_score"] * 0.25
        + ranked["size_score"] * 0.20
        + ranked["age_score"] * 0.10
        + ranked["cost_performance_score"] * 0.15
    ).clip(0, 1)

    preference_scores = []
    for _, row in ranked.iterrows():
        preference_scores.append(preference_score(build_reason_flags(row, preferences)))
    ranked["preference_score"] = preference_scores
    ranked["matching_score"] = (0.6 * ranked["rule_score"] + 0.4 * ranked["preference_score"]).clip(0, 1)

    return ranked.sort_values("matching_score", ascending=False)


def recommend_with_fallback(
    listings_df: pd.DataFrame,
    preferences: PreferenceRequest,
    *,
    warnings: list[str] | None = None,
) -> RecommendationResponse:
    response_warnings = list(warnings or [])
    normalized = normalize_listings(listings_df)
    candidates, filter_warnings = filter_with_relaxation(normalized, preferences)
    response_warnings.extend(filter_warnings)
    response_warnings.append("Using rule-based fallback ranking.")

    ranked = _rule_rank(candidates, preferences)
    recommendations = []
    for _, row in ranked.head(preferences.limit).iterrows():
        recommendations.append(
            build_recommendation_item(
                row,
                preferences,
                matching_score=row["matching_score"],
                model_score=None,
                preference_score_value=row["preference_score"],
            )
        )

    return RecommendationResponse(
        recommendations=recommendations,
        ranking_mode="fallback",
        warnings=response_warnings,
    )

