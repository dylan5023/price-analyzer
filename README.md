# Price Analyzer

Competitor price analysis module for automated pricing review.

## Problem

Manually comparing competitor prices against internal pricing is slow and
error-prone. This module calculates price gaps, detects outliers, and flags
items that require human review before any price change is applied.

## Business Rules

| Rule                | Definition                                                 |
| ------------------- | ---------------------------------------------------------- |
| `price_gap_percent` | `(our_price - competitor_price) / competitor_price * 100`  |
| `review_required`   | Absolute gap exceeds **10%** (threshold is configurable)   |
| Invalid input       | Zero or negative prices are rejected, not silently skipped |

## Tech Stack

Python 3.12 · Pydantic · Pandas · pytest · uv

## Setup

uv sync
uv run pytest

## Project Structure

src/
models.py # Pydantic input/output models
analyzer.py # Core calculation logic
loader.py # CSV/JSON loading and cleaning
client.py # External API client (retry, timeout)
exceptions.py # Domain-specific exceptions
tests/ # pytest suite
data/ # Sample datasets

## Roadmap

- [x] Project setup
- [ ] Price analysis module + tests
- [ ] FastAPI endpoint
- [ ] Docker
- [ ] n8n workflow integration
- [ ] LLM-based recommendation with structured output

## Status

🚧 In development — Step 1 of 9
