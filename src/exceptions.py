"""Domain-specific exceptions for the price analyzer."""


class PriceAnalyzerError(Exception):
    """Base exception for all price analyzer errors.

    Catch this to handle any expected failure in this package.
    Anything not derived from this is a bug.
    """


class InvalidPriceError(PriceAnalyzerError):
    """Raised when a price value is invalid (zero, negative, or unparseable)."""


class DataSourceError(PriceAnalyzerError):
    """Raised when input data cannot be loaded (missing file, API failure)."""