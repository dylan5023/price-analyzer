"""HTTP client for fetching competitor price data."""

import time 
import requests
from src.exceptions import DataSourceError

DEFAULT_TIMEOUT_SECONDS = 10
MAX_ATTEMPTS = 3
BACKOFF_BASE_SECONDS = 1
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

def fetch_price(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    """Fetch price data from an external API.

    Retries on transient failures (5xx, 429, network errors) with
    exponential backoff. Client errors (4xx) fail immediately.
    """

    last_error: Exception | None = None 

    for attempt in range(1, MAX_ATTEMPTS +1):
        try:
            response = requests.get(url, timeout=timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            last_error = e

        else:
            if response.status_code < 400:
                return response.json()  
            
            if response.status_code not in RETRYABLE_STATUS_CODES:
                raise DataSourceError(
                    f"Request failed with status {response.status_code}: {url}"
                )

            last_error = requests.HTTPError(
                f"status {response.status_code}"
            )

        if attempt < MAX_ATTEMPTS:
            time.sleep(BACKOFF_BASE_SECONDS * (2 ** (attempt - 1)))
    
    raise DataSourceError(
        f"Failed after {MAX_ATTEMPTS} attempts: {url}"
    ) from last_error