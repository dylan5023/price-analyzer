# Price Analyzer

Competitor price analysis module for automated pricing review.

## Problem

Manually comparing competitor prices against internal pricing is slow and
error-prone. This module calculates price gaps and flags items that require
human review.

## Business Rules

### Analysis

| Rule                | Definition                                                                       |
| ------------------- | -------------------------------------------------------------------------------- |
| `price_gap_percent` | `(our_price - competitor_price) / competitor_price * 100`, rounded to 2 decimals |
| `review_required`   | **Absolute** gap **exceeds** 10% (both directions: too expensive or too cheap)   |
| `is_outlier`        | **Absolute** gap **exceeds** 50% — likely a data quality issue, not a real price |

### Input Handling

| Rule                             | Behavior                                                       |
| -------------------------------- | -------------------------------------------------------------- |
| Duplicate rows                   | Removed before validation                                      |
| Thousands separator (`1,299.00`) | Normalized to `1299.00`                                        |
| Whitespace in SKU                | Stripped                                                       |
| Zero, negative, or missing price | **Rejected** with a reason — never silently dropped or imputed |
| Non-numeric price (`abc`)        | **Rejected** with a reason — not coerced to NaN                |

## Configuration

All settings are read from environment variables (see `.env.example`).
Values are validated at startup — invalid configuration fails fast.

| Variable                    | Default | Description                                                |
| --------------------------- | ------- | ---------------------------------------------------------- |
| `REVIEW_THRESHOLD_PERCENT`  | `10.0`  | Gap above which an item is flagged for review              |
| `OUTLIER_THRESHOLD_PERCENT` | `50.0`  | Gap above which an item is treated as a data quality issue |
| `REQUEST_TIMEOUT_SECONDS`   | `10`    | HTTP request timeout                                       |
| `MAX_ATTEMPTS`              | `3`     | Max attempts for retryable failures (5xx, 429, network)    |
| `BACKOFF_BASE_SECONDS`      | `1.0`   | Base for exponential backoff                               |

Retryable status codes are intentionally **not** configurable — they follow
the HTTP spec rather than local policy.

## Status

🚧 In development — Step 1 of 9 (Python module)

## Tech Stack

Python 3.12 · Pydantic · Pandas · pytest · uv

## Setup

```bash
uv sync
uv run pytest
```

## Tests

6 tests covering: gap calculation, zero-gap, the 10% boundary,
invalid input rejection at both the model and the analyzer boundary.

## Project Structure

```
src/
  models.py      # Pydantic input/output models
  analyzer.py    # Core calculation logic
  loader.py      # CSV/JSON loading and cleaning
  client.py      # External API client (retry, timeout)
  exceptions.py  # Domain-specific exceptions
tests/           # pytest suite
data/            # Sample datasets
```

## Roadmap

- [x] Project setup
- [x] Pydantic models & domain exceptions
- [x] CSV loader with normalization
- [x] Price analysis pipeline + tests
- [ ] FastAPI endpoint
