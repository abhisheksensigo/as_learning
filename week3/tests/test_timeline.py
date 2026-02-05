import pytest

import timeline


def test_parse_timeline_last_year():
    parsed = timeline.parse_timeline("last 1 year")
    assert parsed is not None
    from_d, to_d = parsed
    assert from_d < to_d
    assert to_d.count("-") == 2  # YYYY-MM-DD format


def test_parse_timeline_in_2024():
    parsed = timeline.parse_timeline("in 2024")
    assert parsed == ("2024-01-01", "2024-12-31")


def test_parse_timeline_january_2023():
    parsed = timeline.parse_timeline("January 2023")
    assert parsed == ("2023-01-01", "2023-01-31")


def test_parse_timeline_empty():
    assert timeline.parse_timeline("") is None
    assert timeline.parse_timeline("   ") is None


def test_timeline_to_minutes_last_month():
    assert timeline.timeline_to_minutes("last month") == 30 * 24 * 60


def test_timeline_to_minutes_in_2024_returns_none():
    """GDELT doesn't support 'in 2024' - only 'last X' formats."""
    assert timeline.timeline_to_minutes("in 2024") is None
