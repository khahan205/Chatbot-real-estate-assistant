"""FastAPI entrypoint for the Yodogawa recommendation backend."""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .recommender import YodogawaRecommender
from .schemas import HealthResponse, PreferenceRequest, RecommendationResponse


app = FastAPI(
    title="Yodogawa Apartment Recommendation Backend",
    version="0.1.0",
    description="Model-backed recommendation API for Yodogawa apartment matching.",
)


def _cors_origins_from_env() -> list[str]:
    """Read comma-separated CORS origins from CORS_ALLOWED_ORIGINS.

    Example:
        CORS_ALLOWED_ORIGINS=https://frontend.vercel.app,http://localhost:3000
    """

    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


cors_origins = _cors_origins_from_env()
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


recommender = YodogawaRecommender()


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "service": app.title,
        "health": "/health",
        "recommend": "/recommend",
    }


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

