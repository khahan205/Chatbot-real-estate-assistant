import pytest

from backend.schemas import PreferenceRequest


def test_preference_request_accepts_full_payload():
    request = PreferenceRequest(
        budget_max=95000,
        min_area_sqm=30,
        max_walk_minutes=10,
        preferred_layouts=["1LDK"],
        preferred_station="Shin-Osaka",
        age_max_years=15,
    )

    assert request.limit == 5
    assert request.preferred_layouts == ["1LDK"]


def test_preference_request_accepts_partial_payload():
    request = PreferenceRequest()

    assert request.budget_max is None
    assert request.preferred_layouts == []


def test_preference_request_rejects_negative_values():
    with pytest.raises(Exception):
        PreferenceRequest(budget_max=-1)


def test_preference_request_rejects_limit_out_of_bounds():
    with pytest.raises(Exception):
        PreferenceRequest(limit=21)

