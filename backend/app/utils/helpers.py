"""
Helper Utilities

This module contains helper utilities for the stock analysis application including:
- Date/time utilities
- Ticker validation
- Error formatting
- Logging helpers
"""
import re
import logging
from datetime import datetime, timezone
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


def get_utc_now() -> datetime:
    """
    Get current UTC timestamp as a naive datetime.
    
    Returns a naive datetime representing the current UTC time.
    This is suitable for database storage where the timestamp column
    doesn't store timezone info but is understood to be UTC.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_utc_now_aware() -> datetime:
    """
    Get current UTC timestamp as a timezone-aware datetime.
    
    Returns a timezone-aware datetime with UTC timezone.
    Use this when you need to preserve timezone information.
    """
    return datetime.now(timezone.utc)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime to ISO 8601 string"""
    if dt is None:
        dt = get_utc_now()
    return dt.isoformat()


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse ISO 8601 timestamp string to datetime"""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def is_valid_ticker(ticker: str) -> bool:
    """
    Validate ticker symbol format.
    
    Valid tickers are 1-10 uppercase alphanumeric characters.
    """
    if not ticker:
        return False
    # Ticker should be 1-10 uppercase letters/numbers
    pattern = r'^[A-Z0-9]{1,10}$'
    return bool(re.match(pattern, ticker.upper()))


def normalize_ticker(ticker: str) -> str:
    """Normalize ticker to uppercase and strip whitespace"""
    return ticker.strip().upper()


def format_error(error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Format an exception into a structured error dictionary.
    
    Args:
        error: The exception to format
        context: Optional context about where the error occurred
        
    Returns:
        Dictionary with error details
    """
    error_dict = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": format_timestamp()
    }
    if context:
        error_dict["context"] = context
    return error_dict


def safe_get(data: Dict[str, Any], *keys, default: Any = None) -> Any:
    """
    Safely get nested values from a dictionary.
    
    Args:
        data: The dictionary to get values from
        *keys: The nested keys to traverse
        default: Default value if key not found
        
    Returns:
        The value at the nested key path, or default if not found
    """
    result = data
    for key in keys:
        try:
            if isinstance(result, dict):
                result = result.get(key, default)
            elif isinstance(result, (list, tuple)) and isinstance(key, int):
                result = result[key] if 0 <= key < len(result) else default
            else:
                return default
        except (KeyError, IndexError, TypeError):
            return default
    return result if result is not None else default


def safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    """Safely convert value to float"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """Safely convert value to int"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def calculate_percentage_change(old_value: float, new_value: float) -> Optional[float]:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return None
    return ((new_value - old_value) / old_value) * 100


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    log = logging.getLogger(name)
    log.setLevel(level)
    
    if not log.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)
    
    return log
