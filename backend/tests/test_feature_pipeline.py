import pandas as pd
import pytest

from backend.config import TRAINED_FEATURE_COLUMNS
from backend.feature_pipeline import FeatureAlignmentError, align_model_features, normalize_listings


def test_normalize_listings_parses_service_and_model_fields():
    raw = pd.DataFrame(
        [
            {
                "id": 1,
                "rent": "9.5万円",
                "management_fee": "10,000円",
                "area_m2": "34.2㎡",
                "building_age": "12年",
                "walking_distance_to_station": "JR京都線/新大阪駅 歩8分",
                "floor_raw": "3階/10階建",
                "conditions": "ペット可",
                "layout": "1LDK",
            }
        ]
    )

    normalized = normalize_listings(raw)
    row = normalized.iloc[0]

    assert row["rent"] == 9.5
    assert row["rent_yen"] == 95000
    assert row["management_fee_yen"] == 10000
    assert row["total_cost_yen"] == 105000
    assert row["walk_minutes"] == 8
    assert row["nearest_station"] == "新大阪駅"
    assert row["floor"] == 3
    assert row["pet_allowed"] == 1


def test_align_model_features_uses_exact_column_order():
    raw = pd.DataFrame(
        [
            {
                "rent": 7.0,
                "management_fee": 5000,
                "area_m2": 25.0,
                "building_age": 10,
                "walking_distance_to_station": "阪急線/十三駅 歩5分",
                "floor_raw": "2階",
                "conditions": "",
            }
        ]
    )
    normalized = normalize_listings(raw)

    features = align_model_features(normalized, TRAINED_FEATURE_COLUMNS)

    assert list(features.columns) == TRAINED_FEATURE_COLUMNS


def test_align_model_features_raises_for_missing_columns():
    with pytest.raises(FeatureAlignmentError):
        align_model_features(pd.DataFrame({"rent": [7.0]}), TRAINED_FEATURE_COLUMNS)

