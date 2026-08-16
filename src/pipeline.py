"""End-to-end price analysis pipeline."""

from pathlib import Path

from src.analyzer import analyze_rows
from src.loader import load_rows
from src.models import PriceResult


def run_analysis(path: str | Path) -> tuple[list[PriceResult], list[dict]]:
    """Load a CSV file, analyze every row, and return results and failures."""
    rows = load_rows(path)        
    return analyze_rows(rows)     

