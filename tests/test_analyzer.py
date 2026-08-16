import pytest
from pydantic import ValidationError

from src.analyzer import analyze, analyze_raw
from src.exceptions import InvalidPriceError
from src.models import PriceInput

def test_analyze_calculates_gap_percent():
    """A 14.29% gap should be calculated correctly and flagged for review."""
    result = analyze(
        PriceInput(sku="A-100", our_price=39.99, competitor_price=34.99)
    )

    assert result.price_gap_percent == 14.29
    assert result.review_required is True
    assert result.is_outlier is False


def test_identical_prices_produce_zero_gap():
    """Equal prices should not be flagged."""
    result = analyze(
        PriceInput(sku="B-200", our_price=25.00, competitor_price=25.00)
    )

    assert result.price_gap_percent == 0.0
    assert result.review_required is False


def test_gap_exactly_at_threshold_is_not_flagged():
    """A gap of exactly 10.00% is NOT flagged — the rule is 'exceeds', not 'at least'."""
    result = analyze(
        PriceInput(sku="EDGE-1", our_price=110.00, competitor_price=100.00)
    )

    assert result.price_gap_percent == 10.0
    assert result.review_required is False


def test_zero_competitor_price_is_rejected():
    """A zero price must be rejected, not divided by."""
    with pytest.raises(InvalidPriceError):
        analyze_raw(
            {"sku": "D-400", "our_price": 15.50, "competitor_price": 0}
        )


def test_negative_price_is_rejected():
    """Negative prices are invalid input."""
    with pytest.raises(InvalidPriceError):                      
        analyze_raw(
            {"sku": "E-500", "our_price": -8.00, "competitor_price": 12.00}
            
        )
        
def test_price_input_rejects_zero_directly():
    """The model itself rejects invalid values, independent of the analyzer."""
    with pytest.raises(ValidationError):
        PriceInput(sku="X", our_price=0, competitor_price=10)


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