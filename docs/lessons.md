# Lessons Learned

Bugs and design decisions from building this project.
Kept for interview preparation and future reference.

---

## 1. Unit mismatch: dollars compared against a percentage threshold

**What happened**

The gap calculation was written as a plain subtraction:

```python
gap = our_price - competitor_price          # a dollar amount
review_required = abs(gap) > 10.0           # a percentage threshold
```

**Why it was dangerous**

No exception was raised. For 39.99 vs 34.99 the difference is $5.00, and
`abs(5.0) > 10.0` evaluates to `False` — so an item with a real gap of
14.29% was silently marked as not requiring review.

The pipeline reported success. Every row was processed. The only thing
wrong was the answer.

**How it was caught**

Code review, not execution. Running the program produced plausible-looking
output.

**Prevention**

`test_analyze_calculates_gap_percent` asserts the exact expected value
(`14.29`) rather than checking that the function returns "something."

---

## 2. String truncation instead of character removal

**What happened**

To strip a thousands separator from `"1,299.00"`, the first attempt used:

```python
value.split(",")[0]     # returns "1", not "1299.00"
```

**Why it was dangerous**

$1,299 would have silently become $1. That value passes every downstream
check — it is a positive, finite number, so Pydantic accepts it. It would
have flowed through to a ~99% price gap, been flagged as an outlier, and
sent a false alert to the pricing team.

The correct operation is removal, not splitting:

```python
value.replace(",", "")  # "1299.00"
```

**Prevention**

`test_thousands_separator_is_preserved_not_truncated` asserts the loader
returns `"1299.00"` for that row.

---

## 3. Copy-paste error in a configuration default

**What happened**

Two thresholds were defined in the settings model. The second one was
copied from the first and its default value was not updated:

```python
review_threshold_percent:  float = Field(default=10.0, gt=0)
outlier_threshold_percent: float = Field(default=10.0, gt=0)   # should be 50.0
```

**Why it was dangerous**

The constraint `gt=0` was satisfied, so validation passed. But with both
thresholds equal, `is_outlier` becomes identical to `review_required` —
every item flagged for review is also labeled a data-quality problem.

In practice this destroys the signal the flag exists to provide. A legitimate
14% price difference would be reported as a suspected bad record, and the
reviewer would spend time investigating clean data. Repeat that often enough
and the team stops trusting the alerts entirely.

**Prevention**

The two thresholds are documented as distinct rules in the README, and the
boundary behaviour is asserted in tests rather than assumed.

---

## 4. A default value that violated its own constraint

**What happened**

```python
backoff_base_seconds: float = Field(default=1, gt=1)   # 1 > 1 is False
```

**Why this one was different**

This failed immediately. `Settings()` is instantiated at module import, so
the `ValidationError` was raised before any data was read, any request was
sent, or any result was produced.

The three bugs above all produced wrong output while appearing to succeed.
This one produced no output at all.

**Why that is better**

A crash at startup is caught by the deploy pipeline. A wrong number is caught
by whoever notices — possibly weeks later, possibly never. Given the choice,
failing loudly and early is far cheaper than failing quietly and late.

This is the reasoning behind validating configuration with Pydantic at import
time rather than reading environment variables lazily with `os.getenv`.

---

## Pattern

Three of these four bugs produced **incorrect results without raising an
error**. Only the one that violated an explicit constraint failed loudly —
and it failed at import time, before touching any data.

That asymmetry shaped three decisions in this project:

- **Validate at boundaries.** Data is checked where it enters the system
  (CSV rows, API responses, configuration), not wherever it happens to be used.
- **Assert exact values in tests.** "It ran without errors" is not evidence
  of correctness, because none of these bugs raised an error.
- **Never coerce silently.** `pd.to_numeric(errors="coerce")` would have
  turned malformed prices, missing prices, and formatting problems into the
  same `NaN`, discarding the reason each row failed. Rejected rows are
  returned with their specific cause instead.

---

## Design decisions worth explaining

**Why the price gap is calculated in Python rather than by an LLM**

The calculation must be deterministic, testable, and explainable. The same
input must always produce the same output, and it must be possible to state
why a given item was flagged. An LLM satisfies none of those requirements.
The LLM's role in later stages is interpretation — summarizing, classifying,
and citing policy — not arithmetic.

**Why retries are limited to 5xx, 429, and network errors**

Retrying a 400 or 404 cannot change the outcome; the request itself is wrong.
Retrying only wastes time while the caller waits. 429 is the exception among
4xx codes: it explicitly means "try again later."

**Why the retryable status codes are not configurable**

Every environment variable is an implicit promise that the value can be
changed safely. Allowing `404` into the retry list would create a foot-gun
with no corresponding benefit. Retry semantics follow the HTTP specification,
not local policy — so they stay in code.

**Why failures are returned rather than logged and dropped**

`analyze_rows` returns `(results, failures)` instead of filtering silently.
The caller decides what to do with rejected rows — in the next stage of this
project, they become the content of a Slack notification. A count alone
("4 rows failed") would not be actionable.
