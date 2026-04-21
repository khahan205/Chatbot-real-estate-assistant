from fastapi.testclient import TestClient

from backend import api
from backend.schemas import ExplanationFlags, RecommendationItem, RecommendationResponse


class FakeRecommender:
    def health(self):
        return {
            "status": "ok",
            "listings_path_exists": True,
            "model_path_exists": True,
            "feature_metadata_path_exists": False,
            "listings_count": 1,
            "model_loadable": True,
            "feature_columns": ["rent"],
            "warnings": [],
        }

    def recommend(self, preferences):
        return RecommendationResponse(
            recommendations=[
                RecommendationItem(
                    id=1,
                    property_name="Listing 1",
                    rent=85000,
                    management_fee_yen=8000,
                    total_cost_yen=93000,
                    layout="1LDK",
                    area_sqm=32.0,
                    walk_minutes=8,
                    nearest_station="新大阪駅",
                    station_access_raw="JR京都線/新大阪駅 歩8分",
                    building_age_years=8,
                    matching_score=0.91,
                    model_score=0.9,
                    preference_score=0.95,
                    reasons=ExplanationFlags(
                        within_budget=True,
                        layout_match=True,
                        walk_match=True,
                        station_match=True,
                        area_match=True,
                        building_age_match=True,
                    ),
                )
            ],
            ranking_mode="model",
            warnings=[],
        )


def test_recommend_endpoint_contract(monkeypatch):
    monkeypatch.setattr(api, "recommender", FakeRecommender())
    client = TestClient(api.app)

    response = client.post(
        "/recommend",
        json={
            "budget_max": 95000,
            "min_area_sqm": 30,
            "max_walk_minutes": 10,
            "preferred_layouts": ["1LDK"],
            "preferred_station": "Shin-Osaka",
            "age_max_years": 15,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ranking_mode"] == "model"
    assert payload["recommendations"][0]["matching_score"] == 0.91
    assert payload["recommendations"][0]["reasons"]["within_budget"] is True

