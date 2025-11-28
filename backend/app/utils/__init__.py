"""
Utility Functions Package

This module exports utility classes and functions for the stock analysis application.
"""
from app.utils.helpers import (
    get_utc_now,
    get_utc_now_aware,
    format_timestamp,
    parse_timestamp,
    is_valid_ticker,
    normalize_ticker,
    format_error,
    safe_get,
    safe_float,
    safe_int,
    calculate_percentage_change,
    setup_logger,
)
from app.utils.api_client import (
    APIClient,
    SimpleCache,
    RateLimiter,
)
from app.utils.data_processor import (
    ResponseBuilder as DataProcessorResponseBuilder,
    DataFrameOptimizer,
    determine_sentiment,
    determine_rating,
)
from app.utils.response_builders import ResponseBuilder
from app.utils.data_fetchers import (
    BaseDataFetcher,
    TipRanksDataFetcher,
    TradingCentralDataFetcher,
    tipranks_fetcher,
    trading_central_fetcher,
)

__all__ = [
    # Helpers
    "get_utc_now",
    "get_utc_now_aware",
    "format_timestamp",
    "parse_timestamp",
    "is_valid_ticker",
    "normalize_ticker",
    "format_error",
    "safe_get",
    "safe_float",
    "safe_int",
    "calculate_percentage_change",
    "setup_logger",
    # API Client
    "APIClient",
    "SimpleCache",
    "RateLimiter",
    # Data Processor
    "DataProcessorResponseBuilder",
    "DataFrameOptimizer",
    "determine_sentiment",
    "determine_rating",
    # Response Builders (new)
    "ResponseBuilder",
    # Data Fetchers (new)
    "BaseDataFetcher",
    "TipRanksDataFetcher",
    "TradingCentralDataFetcher",
    "tipranks_fetcher",
    "trading_central_fetcher",
]
