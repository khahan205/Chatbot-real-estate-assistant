"""Listing normalization and model feature preparation."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from os import PathLike
from typing import Iterable

import numpy as np
import pandas as pd


class FeatureAlignmentError(ValueError):
    """Raised when listing data cannot be aligned to the trained model schema."""


@dataclass(frozen=True)
class StationQuery:
    raw: str
    terms: tuple[str, ...]


COLUMN_ALIASES = {
    "所在地": "location",
    "管理費_共益費": "management_fee",
    "向き": "direction",
    "階": "floor_raw",
    "条件": "conditions",
    "専有面積": "area_m2",
    "築年数": "building_age",
    "駅徒歩": "walking_distance_to_station",
    "area": "area_m2",
    "age": "building_age",
    "distance": "walking_distance_to_station",
    "price": "rent",
}

STATION_ALIASES = {
    "shin-osaka": ("shin-osaka", "shin osaka", "新大阪"),
    "shinosaka": ("shinosaka", "shin-osaka", "shin osaka", "新大阪"),
    "juso": ("juso", "十三"),
    "higashi-mikuni": ("higashi-mikuni", "higashi mikuni", "東三国"),
    "higashimikuni": ("higashimikuni", "higashi-mikuni", "東三国"),
    "nishinakajima-minamigata": (
        "nishinakajima-minamigata",
        "nishinakajima minamigata",
        "西中島南方",
    ),
    "nishinakajimaminamigata": (
        "nishinakajimaminamigata",
        "nishinakajima-minamigata",
        "西中島南方",
    ),
    "minamikata": ("minamikata", "南方"),
    "mikuni": ("mikuni", "三国", "三國"),
    "kanzakigawa": ("kanzakigawa", "神崎川"),
    "tsukamoto": ("tsukamoto", "塚本"),
    "kashima": ("kashima", "加島"),
}


def normalize_text(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    return " ".join(text.replace("\r\n", "\n").replace("\r", "\n").split())


def normalize_for_match(value: object) -> str:
    return normalize_text(value).casefold().replace("‐", "-").replace("‑", "-").replace("－", "-")


def load_listings(csv_path: str | bytes | PathLike[str]) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {col: COLUMN_ALIASES[col] for col in df.columns if col in COLUMN_ALIASES}
    return df.rename(columns=rename_map).copy()


def parse_number(value: object) -> float:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 0.0
    if isinstance(value, (int, float, np.number)):
        return float(value)
    text = unicodedata.normalize("NFKC", str(value))
    text = text.replace(",", "").replace("¥", "").replace("円", "")
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else 0.0


def parse_money(value: object, *, rent_man_yen: bool = False) -> float:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 0.0
    text = unicodedata.normalize("NFKC", str(value))
    number = parse_number(text)
    contains_man = "万" in text

    if rent_man_yen:
        if contains_man:
            return number
        return number / 10000 if number >= 1000 else number

    if contains_man:
        return number * 10000
    return number


def parse_floor(value: object) -> float:
    text = normalize_text(value)
    match = re.search(r"(\d+)", text)
    return float(match.group(1)) if match else 0.0


def parse_walk_minutes(value: object) -> int | None:
    text = normalize_text(value)
    if not text:
        return None
    patterns = [
        r"(?:徒歩|歩)\s*(\d+)\s*分",
        r"walk\s*(\d+)\s*(?:min|minutes?)?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else None


def parse_nearest_station(value: object) -> str | None:
    text = unicodedata.normalize("NFKC", "" if value is None else str(value))
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if not first_line:
        return None

    station_match = re.search(r"/\s*([^/\s]+?駅)", first_line)
    if station_match:
        return station_match.group(1).strip()

    station_match = re.search(r"([^/\s]+?駅)", first_line)
    if station_match:
        return station_match.group(1).strip()

    candidate = re.split(r"(?:徒歩|歩|walk)\s*\d+", first_line, maxsplit=1, flags=re.IGNORECASE)[0]
    if "/" in candidate:
        candidate = candidate.split("/")[-1]
    candidate = candidate.strip(" -:：")
    return candidate or None


def pet_allowed_flag(value: object) -> int:
    text = normalize_text(value)
    if not text:
        return 0
    lowered = text.casefold()
    if "pet" in lowered:
        return 0 if "no pet" in lowered or "not allowed" in lowered else 1
    if "ペット" not in text:
        return 0
    return 0 if "不可" in text else 1


def normalize_layouts(layouts: Iterable[str]) -> tuple[str, ...]:
    return tuple(normalize_for_match(layout) for layout in layouts if normalize_for_match(layout))


def build_station_query(preferred_station: str | None) -> StationQuery | None:
    if not preferred_station:
        return None
    raw = normalize_for_match(preferred_station)
    compact = raw.replace(" ", "").replace("-", "")
    terms = {raw, compact}
    terms.update(STATION_ALIASES.get(raw, ()))
    terms.update(STATION_ALIASES.get(compact, ()))
    normalized_terms = tuple(sorted({normalize_for_match(term) for term in terms if term}))
    return StationQuery(raw=preferred_station, terms=normalized_terms)


def station_matches(station_access_raw: object, nearest_station: object, query: StationQuery | None) -> bool | None:
    if query is None:
        return None
    nearest = normalize_for_match(nearest_station)
    if nearest:
        return any(term in nearest for term in query.terms)
    return any(term in normalize_for_match(station_access_raw) for term in query.terms)


def normalize_listings(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized service fields and model features."""

    df = standardize_columns(df)

    for col in ["rent", "management_fee", "area_m2", "building_age"]:
        if col not in df.columns:
            df[col] = 0

    df["rent"] = df["rent"].apply(lambda value: parse_money(value, rent_man_yen=True))
    df["management_fee"] = df["management_fee"].apply(parse_money)
    df["area_m2"] = df["area_m2"].apply(parse_number)
    df["building_age"] = df["building_age"].apply(parse_number)

    if "floor_raw" in df.columns:
        df["floor"] = df["floor_raw"].apply(parse_floor)
    elif "floor" in df.columns:
        df["floor"] = df["floor"].apply(parse_floor)
    else:
        df["floor"] = 0.0

    if "conditions" in df.columns:
        df["pet_allowed"] = df["conditions"].apply(pet_allowed_flag)
    elif "pet_allowed" not in df.columns:
        df["pet_allowed"] = 0

    if "walking_distance_to_station" not in df.columns:
        df["walking_distance_to_station"] = ""
    if "station_access_raw" not in df.columns:
        df["station_access_raw"] = df["walking_distance_to_station"].fillna("").astype(str)
    df["walk_minutes"] = df["station_access_raw"].apply(parse_walk_minutes)
    df["nearest_station"] = df["station_access_raw"].apply(parse_nearest_station)
    df["walking_distance_to_station"] = df["walk_minutes"].fillna(0).astype(float)

    df["rent_yen"] = (df["rent"] * 10000).round().astype(int)
    df["management_fee_yen"] = df["management_fee"].fillna(0).round().astype(int)
    df["total_cost_yen"] = df["rent_yen"] + df["management_fee_yen"]

    total_cost_nonzero = df["total_cost_yen"].replace(0, np.nan)
    df["cost_performance"] = (df["area_m2"] / total_cost_nonzero).replace([np.inf, -np.inf], np.nan).fillna(0)

    return df


def align_model_features(df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    missing = [column for column in feature_columns if column not in df.columns]
    if missing:
        raise FeatureAlignmentError(f"Missing model feature columns: {', '.join(missing)}")
    features = df.loc[:, feature_columns].copy()
    for column in feature_columns:
        features[column] = pd.to_numeric(features[column], errors="coerce").fillna(0)
    return features
