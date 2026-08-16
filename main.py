"""CLI entry point for the price analyzer."""

import sys

from src.exceptions import PriceAnalyzerError
from src.pipeline import run_analysis

DEFAULT_DATA_PATH = "data/sample_prices.csv"


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA_PATH

    try:
        results, failures = run_analysis(path)
    except PriceAnalyzerError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"Analyzed: {len(results)} passed, {len(failures)} rejected\n")

    print("--- Results ---")
    for r in results:
        flag = "REVIEW" if r.review_required else "  OK  "
        outlier = "  <- OUTLIER" if r.is_outlier else ""
        print(f"[{flag}] {r.sku:8} {r.price_gap_percent:>8.2f}%{outlier}")

    if failures:
        print("\n--- Rejected ---")
        for f in failures:
            print(f"{f['sku']:8} -> {f['reason']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())