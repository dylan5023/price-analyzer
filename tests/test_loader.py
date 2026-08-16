"""Tests for CSV loading and normalization."""

from src.loader import load_rows


def test_thousands_separator_is_preserved_not_truncated():
    rows = load_rows("data/sample_prices.csv")
    by_sku = {r["sku"]: r for r in rows}

    assert by_sku["F-600"]["our_price"] == "1299.00"


def test_duplicate_rows_are_removed():
    """The sample file has 9 rows with one duplicate."""
    rows = load_rows("data/sample_prices.csv")

    assert len(rows) == 8