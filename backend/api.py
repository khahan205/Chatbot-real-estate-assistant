"""FastAPI entrypoint for the Yodogawa recommendation backend."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .recommender import YodogawaRecommender
from .schemas import HealthResponse, PreferenceRequest, RecommendationResponse


app = FastAPI(
    title="Yodogawa Apartment Recommendation Backend",
    version="0.1.0",
    description="Model-backed recommendation API for Yodogawa apartment matching.",
)

recommender = YodogawaRecommender()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(**recommender.health())


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(preferences: PreferenceRequest) -> RecommendationResponse:
    try:
        return recommender.recommend(preferences)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - final API safety net.
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {exc}") from exc

