from src.models import PriceInput, PriceResult
from pydantic import ValidationError
from src.exceptions import InvalidPriceError, PriceAnalyzerError

REVIEW_THRESHOLD_PERCENT = 10.0
OUTLIER_THRESHOLD_PERCENT = 50.0

def analyze(price_input: PriceInput) -> PriceResult:
    """Calculate the price gap and determine whether review is required."""
    our = price_input.our_price
    competitor = price_input.competitor_price

    gap = round((our - competitor) / competitor * 100, 2)


    review_required = abs(gap) > REVIEW_THRESHOLD_PERCENT
    is_outlier = abs(gap) > OUTLIER_THRESHOLD_PERCENT

    return PriceResult(
        sku = price_input.sku,
        price_gap_percent=gap,
        is_outlier= is_outlier,
        review_required= review_required
    )


def analyze_raw(row: dict) -> PriceResult:
    """Validate a raw dict and analyze it. Wraps validation errors."""

    try:
        price_input = PriceInput(**row)
    except ValidationError as e:
        detail = "; ".join(
            f"{err['loc'][0]}: {err['msg']}" for err in e.errors()
        )
        raise InvalidPriceError(f"SKU {row.get('sku', 'unknown')}: {detail}") from e

    return analyze(price_input)
        
    
def analyze_rows(rows: list[dict]) -> tuple[list[PriceResult], list[dict]]:
    """Analyze multiple rows, separating successes from failures.

    Returns:
        (results, failures) where each failure records the original row
        and the reason it was rejected.
    """
    results: list[PriceResult] = []
    failures: list[dict] = []

    for row in rows:
        try:
            results.append(analyze_raw(row))
        except PriceAnalyzerError as e: 
            failures.append({
                "sku": row.get("sku", "unknown"),
                "reason": str(e),
                "row": row,

            })
    return results, failures