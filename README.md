# Price Analyzer

Competitor price analysis module for automated pricing review.

## Problem
Manually comparing competitor prices against internal pricing is slow and
error-prone. This module calculates price gaps and flags items that require
human review.

## Business Rules
- `price_gap_percent` = (our_price - competitor_price) / competitor_price * 100
- Items with a gap exceeding 10% are flagged as `review_required`
- Negative or zero prices are rejected as invalid input

## Status
🚧 In development — Step 1 of 9 (Python module)

## Tech Stack
Python 3.12 · Pydantic · Pandas · pytest · uv

## Setup

```bash
uv sync
uv run pytest
```

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
- [ ] Price analysis module + tests
- [ ] FastAPI endpoint
- [ ] Docker
- [ ] n8n workflow integration