import numpy as np
import pandas as pd

from backend.config import TRAINED_FEATURE_COLUMNS
from backend.fallback import recommend_with_fallback
from backend.feature_pipeline import normalize_listings
from backend.recommender import rank_candidates
from backend.schemas import PreferenceRequest


class FakeModel:
    def predict(self, features):
        return np.array([20.0, 90.0])


def _sample_listings():
    return pd.DataFrame(
        [
            {
                "id": 1,
                "rent": 7.0,
                "management_fee": 5000,
                "area_m2": 24.0,
                "building_age": 20,
                "walking_distance_to_station": "阪急線/十三駅 歩5分",
                "floor_raw": "2階",
                "conditions": "",
                "layout": "1K",
            },
            {
                "id": 2,
                "rent": 8.5,
                "management_fee": 8000,
                "area_m2": 32.0,
                "building_age": 8,
                "walking_distance_to_station": "JR京都線/新大阪駅 歩8分",
                "floor_raw": "4階",
                "conditions": "ペット可",
                "layout": "1LDK",
            },
        ]
    )


def test_rank_candidates_sorts_by_matching_score_with_fake_model():
    normalized = normalize_listings(_sample_listings())

    ranked = rank_candidates(
        normalized,
        FakeModel(),
        TRAINED_FEATURE_COLUMNS,
        PreferenceRequest(),
    )

    assert ranked.iloc[0]["id"] == 2
    assert ranked.iloc[0]["model_score"] == 0.9


def test_fallback_returns_ranked_response_when_model_unavailable():
    response = recommend_with_fallback(
        _sample_listings(),
        PreferenceRequest(
            budget_max=95000,
            min_area_sqm=25,
            max_walk_minutes=10,
            preferred_layouts=["1LDK"],
            preferred_station="Shin-Osaka",
            age_max_years=15,
        ),
        warnings=["Model ranking unavailable: test"],
    )

    assert response.ranking_mode == "fallback"
    assert response.recommendations
    assert response.recommendations[0].reasons.within_budget is not None

