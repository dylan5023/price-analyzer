"""HTTP client for fetching competitor price data."""

import time 
import requests
from src.exceptions import DataSourceError
from src.config import settings 


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

def fetch_price(url: str, timeout: int | None) -> dict:
    """Fetch price data from an external API.

    Retries on transient failures (5xx, 429, network errors) with
    exponential backoff. Client errors (4xx) fail immediately.
    """
    
    if timeout is None:
        timeout = settings.request_timeout_seconds

    last_error: Exception | None = None 

    for attempt in range(1, settings.max_attempts +1):
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

        if attempt < settings.max_attempts:
            time.sleep(settings.backoff_base_seconds * (2 ** (attempt - 1)))
    
    raise DataSourceError(
        f"Failed after {settings.max_attempts} attempts: {url}"
    ) from last_error