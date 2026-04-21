"""Pydantic models shared by the API and recommendation layer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .config import DEFAULT_LIMIT, MAX_LIMIT


class PreferenceRequest(BaseModel):
    budget_max: int | None = Field(None, ge=0)
    min_area_sqm: float | None = Field(None, ge=0)
    max_walk_minutes: int | None = Field(None, ge=0)
    preferred_layouts: list[str] = Field(default_factory=list)
    preferred_station: str | None = None
    age_max_years: int | None = Field(None, ge=0)
    limit: int = Field(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)


class ExplanationFlags(BaseModel):
    within_budget: bool | None = None
    layout_match: bool | None = None
    walk_match: bool | None = None
    station_match: bool | None = None
    area_match: bool | None = None
    building_age_match: bool | None = None


class RecommendationItem(BaseModel):
    id: int | str | None = None
    property_name: str
    rent: int
    management_fee_yen: int
    total_cost_yen: int
    layout: str | None = None
    area_sqm: float | None = None
    walk_minutes: int | None = None
    nearest_station: str | None = None
    station_access_raw: str | None = None
    building_age_years: float | None = None
    matching_score: float
    model_score: float | None = None
    preference_score: float
    reasons: ExplanationFlags


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
    ranking_mode: Literal["model", "fallback"]
    warnings: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    listings_path_exists: bool
    model_path_exists: bool
    feature_metadata_path_exists: bool
    listings_count: int | None = None
    model_loadable: bool
    feature_columns: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

