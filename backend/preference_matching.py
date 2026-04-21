"""Preference filtering, flags, and API response assembly."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from .feature_pipeline import (
    build_station_query,
    normalize_for_match,
    normalize_layouts,
    station_matches,
)
from .schemas import ExplanationFlags, PreferenceRequest, RecommendationItem


RELAX_ORDER = ["station", "layout", "age", "walk", "area", "budget"]


def _is_missing(value: object) -> bool:
    return value is None or (isinstance(value, float) and np.isnan(value))


def _as_int(value: object, default: int = 0) -> int:
    if _is_missing(value):
        return default
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return default


def _as_float_or_none(value: object) -> float | None:
    if _is_missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int_or_none(value: object) -> int | None:
    number = _as_float_or_none(value)
    return None if number is None else int(round(number))


def _truthy_flags(flags: ExplanationFlags) -> list[bool]:
    values = [
        flags.within_budget,
        flags.layout_match,
        flags.walk_match,
        flags.station_match,
        flags.area_match,
        flags.building_age_match,
    ]
    return [value for value in values if value is not None]


def preference_score(flags: ExplanationFlags) -> float:
    evaluated = _truthy_flags(flags)
    if not evaluated:
        return 0.0
    return sum(1 for value in evaluated if value) / len(evaluated)


def build_reason_flags(row: pd.Series, preferences: PreferenceRequest) -> ExplanationFlags:
    layouts = normalize_layouts(preferences.preferred_layouts)
    station_query = build_station_query(preferences.preferred_station)

    layout = normalize_for_match(row.get("layout", ""))
    walk_minutes = _as_float_or_none(row.get("walk_minutes"))
    total_cost_yen = _as_float_or_none(row.get("total_cost_yen"))
    area_sqm = _as_float_or_none(row.get("area_m2"))
    building_age = _as_float_or_none(row.get("building_age"))

    return ExplanationFlags(
        within_budget=None
        if preferences.budget_max is None
        else bool(total_cost_yen is not None and total_cost_yen <= preferences.budget_max),
        layout_match=None if not layouts else layout in layouts,
        walk_match=None
        if preferences.max_walk_minutes is None
        else bool(walk_minutes is not None and walk_minutes <= preferences.max_walk_minutes),
        station_match=station_matches(row.get("station_access_raw"), row.get("nearest_station"), station_query),
        area_match=None
        if preferences.min_area_sqm is None
        else bool(area_sqm is not None and area_sqm >= preferences.min_area_sqm),
        building_age_match=None
        if preferences.age_max_years is None
        else bool(building_age is not None and building_age <= preferences.age_max_years),
    )


def active_filter_keys(preferences: PreferenceRequest) -> set[str]:
    keys: set[str] = set()
    if preferences.budget_max is not None:
        keys.add("budget")
    if preferences.min_area_sqm is not None:
        keys.add("area")
    if preferences.max_walk_minutes is not None:
        keys.add("walk")
    if preferences.preferred_layouts:
        keys.add("layout")
    if preferences.preferred_station:
        keys.add("station")
    if preferences.age_max_years is not None:
        keys.add("age")
    return keys


def apply_filters_once(
    df: pd.DataFrame,
    preferences: PreferenceRequest,
    *,
    disabled: Iterable[str] = (),
) -> pd.DataFrame:
    disabled_keys = set(disabled)
    filtered = df.copy()

    if "budget" not in disabled_keys and preferences.budget_max is not None:
        filtered = filtered[filtered["total_cost_yen"] <= preferences.budget_max]

    if "area" not in disabled_keys and preferences.min_area_sqm is not None:
        filtered = filtered[filtered["area_m2"] >= preferences.min_area_sqm]

    if "walk" not in disabled_keys and preferences.max_walk_minutes is not None:
        walk_values = pd.to_numeric(filtered["walk_minutes"], errors="coerce")
        filtered = filtered[walk_values <= preferences.max_walk_minutes]

    if "layout" not in disabled_keys and preferences.preferred_layouts:
        layouts = set(normalize_layouts(preferences.preferred_layouts))
        normalized_layouts = filtered["layout"].fillna("").map(normalize_for_match)
        filtered = filtered[normalized_layouts.isin(layouts)]

    if "station" not in disabled_keys and preferences.preferred_station:
        station_query = build_station_query(preferences.preferred_station)
        station_mask = filtered.apply(
            lambda row: bool(station_matches(row.get("station_access_raw"), row.get("nearest_station"), station_query)),
            axis=1,
        )
        filtered = filtered[station_mask]

    if "age" not in disabled_keys and preferences.age_max_years is not None:
        filtered = filtered[filtered["building_age"] <= preferences.age_max_years]

    return filtered


def filter_with_relaxation(df: pd.DataFrame, preferences: PreferenceRequest) -> tuple[pd.DataFrame, list[str]]:
    warnings: list[str] = []
    active = active_filter_keys(preferences)

    if not active:
        warnings.append("No preference constraints supplied; returning model-ranked listings.")
        return df.copy(), warnings

    strict = apply_filters_once(df, preferences)
    if not strict.empty:
        return strict, warnings

    disabled: set[str] = set()
    for key in RELAX_ORDER:
        if key not in active:
            continue
        disabled.add(key)
        relaxed = apply_filters_once(df, preferences, disabled=disabled)
        if not relaxed.empty:
            warnings.append(
                "Relaxed filters because no listing matched all criteria: "
                + ", ".join(disabled)
                + "."
            )
            return relaxed, warnings

    warnings.append("No listings matched the supplied preferences; showing general candidates.")
    return df.copy(), warnings


def build_recommendation_item(
    row: pd.Series,
    preferences: PreferenceRequest,
    *,
    matching_score: float,
    model_score: float | None,
    preference_score_value: float,
) -> RecommendationItem:
    listing_id = row.get("id")
    if isinstance(listing_id, float) and listing_id.is_integer():
        listing_id = int(listing_id)

    property_name = None
    for field in ("property_name", "name", "title"):
        value = row.get(field)
        if not _is_missing(value) and str(value).strip():
            property_name = str(value).strip()
            break
    if not property_name:
        property_name = f"Listing {listing_id}" if listing_id is not None else "Listing"

    flags = build_reason_flags(row, preferences)

    return RecommendationItem(
        id=listing_id,
        property_name=property_name,
        rent=_as_int(row.get("rent_yen")),
        management_fee_yen=_as_int(row.get("management_fee_yen")),
        total_cost_yen=_as_int(row.get("total_cost_yen")),
        layout=None if _is_missing(row.get("layout")) else str(row.get("layout")),
        area_sqm=_as_float_or_none(row.get("area_m2")),
        walk_minutes=_as_int_or_none(row.get("walk_minutes")),
        nearest_station=None if _is_missing(row.get("nearest_station")) else str(row.get("nearest_station")),
        station_access_raw=None if _is_missing(row.get("station_access_raw")) else str(row.get("station_access_raw")),
        building_age_years=_as_float_or_none(row.get("building_age")),
        matching_score=round(float(matching_score), 4),
        model_score=None if model_score is None else round(float(model_score), 4),
        preference_score=round(float(preference_score_value), 4),
        reasons=flags,
    )

