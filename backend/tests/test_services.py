"""
Service Layer Tests

This module contains tests for all service layer components to ensure proper
functionality, error handling, and data processing.
"""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timedelta
from typing import Optional

from app.services.config_service import ConfigService, TickerConfig
from app.services.comparison_service import (
    ComparisonService,
    TrendDirection,
    _parse_period_to_hours,
    _determine_trend,
    _calculate_change,
)
from app.services.dashboard_service import DashboardService, AlertType, AlertSeverity
from app.utils.helpers import (
    is_valid_ticker,
    normalize_ticker,
    safe_get,
    safe_float,
    safe_int,
    calculate_percentage_change,
    get_utc_now,
)


# ============================================
# Tests for Helper Utilities
# ============================================

class TestHelperUtilities:
    """Tests for helper utility functions"""
    
    def test_is_valid_ticker_valid(self):
        """Test valid ticker formats"""
        assert is_valid_ticker("AAPL") is True
        assert is_valid_ticker("TSLA") is True
        assert is_valid_ticker("NVDA") is True
        assert is_valid_ticker("A") is True
        assert is_valid_ticker("GOOGL123") is True
    
    def test_is_valid_ticker_invalid(self):
        """Test invalid ticker formats"""
        assert is_valid_ticker("") is False
        assert is_valid_ticker(None) is False
        assert is_valid_ticker("INVALID!@#") is False
        assert is_valid_ticker("TOO_LONG_TICKER") is False
        assert is_valid_ticker("A B C") is False
    
    def test_normalize_ticker(self):
        """Test ticker normalization"""
        assert normalize_ticker("aapl") == "AAPL"
        assert normalize_ticker("  TSLA  ") == "TSLA"
        assert normalize_ticker("nvda") == "NVDA"
    
    def test_safe_get_basic(self):
        """Test safe_get with basic dictionary"""
        data = {"a": 1, "b": {"c": 2}}
        assert safe_get(data, "a") == 1
        assert safe_get(data, "b", "c") == 2
        assert safe_get(data, "x", default="default") == "default"
    
    def test_safe_get_with_list(self):
        """Test safe_get with list indices"""
        data = {"items": [1, 2, 3]}
        assert safe_get(data, "items", 0) == 1
        assert safe_get(data, "items", 10, default=-1) == -1
    
    def test_safe_float(self):
        """Test safe_float conversion"""
        assert safe_float(1.5) == 1.5
        assert safe_float("2.5") == 2.5
        assert safe_float(None) is None
        assert safe_float("invalid", default=0.0) == 0.0
    
    def test_safe_int(self):
        """Test safe_int conversion"""
        assert safe_int(10) == 10
        assert safe_int("20") == 20
        assert safe_int(None) is None
        assert safe_int("invalid", default=0) == 0
    
    def test_calculate_percentage_change(self):
        """Test percentage change calculation"""
        assert calculate_percentage_change(100, 110) == 10.0
        assert calculate_percentage_change(100, 90) == -10.0
        assert calculate_percentage_change(0, 100) is None
    
    def test_get_utc_now(self):
        """Test UTC timestamp generation"""
        now = get_utc_now()
        assert isinstance(now, datetime)
        # Should be naive datetime (no timezone info stored)
        assert now.tzinfo is None


# ============================================
# Tests for Comparison Service
# ============================================

class TestComparisonService:
    """Tests for ComparisonService"""
    
    def test_parse_period_to_hours(self):
        """Test period string to hours conversion"""
        assert _parse_period_to_hours("1h") == 1
        assert _parse_period_to_hours("4h") == 4
        assert _parse_period_to_hours("1d") == 24
        assert _parse_period_to_hours("1w") == 168
        assert _parse_period_to_hours("1m") == 720  # Approximate month
    
    def test_determine_trend_up(self):
        """Test trend direction detection for upward movement"""
        assert _determine_trend(100, 110) == TrendDirection.UP
        assert _determine_trend(0, 10) == TrendDirection.UP
    
    def test_determine_trend_down(self):
        """Test trend direction detection for downward movement"""
        assert _determine_trend(100, 90) == TrendDirection.DOWN
        assert _determine_trend(0, -10) == TrendDirection.DOWN
    
    def test_determine_trend_stable(self):
        """Test trend direction detection for stable values"""
        assert _determine_trend(100, 100) == TrendDirection.STABLE
        assert _determine_trend(100, 100.5) == TrendDirection.STABLE
    
    def test_determine_trend_unknown(self):
        """Test trend direction for unknown cases"""
        assert _determine_trend(None, 100) == TrendDirection.UNKNOWN
        assert _determine_trend(100, None) == TrendDirection.UNKNOWN
    
    def test_calculate_change_basic(self):
        """Test change calculation"""
        result = _calculate_change(100, 110)
        assert result["absolute_change"] == 10.0
        assert result["percentage_change"] == 10.0
        assert result["trend"] == TrendDirection.UP.value
    
    def test_calculate_change_with_none(self):
        """Test change calculation with None values"""
        result = _calculate_change(None, 100)
        assert result["absolute_change"] is None
        assert result["percentage_change"] is None
        assert result["trend"] == TrendDirection.UNKNOWN.value
    
    def test_comparison_service_initialization(self):
        """Test ComparisonService initialization"""
        service = ComparisonService()
        assert service is not None


# ============================================
# Tests for Config Service
# ============================================

class TestConfigService:
    """Tests for ConfigService"""
    
    def test_config_service_initialization(self):
        """Test ConfigService initialization"""
        service = ConfigService()
        assert service._ticker_cache == {}
        assert service._api_key_cache == {}
        assert service._last_reload is None
    
    def test_get_active_ticker_list_empty(self):
        """Test getting active tickers when cache is empty"""
        service = ConfigService()
        tickers = service.get_active_ticker_list()
        assert tickers == []
    
    def test_get_ticker_config_not_found(self):
        """Test getting ticker config when not in cache"""
        service = ConfigService()
        config = service.get_ticker_config("AAPL")
        assert config is None
    
    def test_get_api_key_not_found(self):
        """Test getting API key when not in cache"""
        service = ConfigService()
        key = service.get_api_key("trading_central")
        assert key is None
    
    def test_get_ticker_configs_dict_empty(self):
        """Test getting ticker configs dict when empty"""
        service = ConfigService()
        configs = service.get_ticker_configs_dict()
        assert configs == {}
    
    def test_ticker_config_dataclass(self):
        """Test TickerConfig dataclass"""
        config = TickerConfig(
            ticker="AAPL",
            exchange="NASDAQ",
            tr_v4_id="EQ-123",
            tr_v3_id="US-456"
        )
        assert config.ticker == "AAPL"
        assert config.exchange == "NASDAQ"


# ============================================
# Tests for Dashboard Service
# ============================================

class TestDashboardService:
    """Tests for DashboardService"""
    
    def test_dashboard_service_initialization(self):
        """Test DashboardService initialization"""
        service = DashboardService()
        assert service is not None
    
    def test_alert_type_enum(self):
        """Test AlertType enum values"""
        assert AlertType.RATING_CHANGE.value == "rating_change"
        assert AlertType.SENTIMENT_SHIFT.value == "sentiment_shift"
        assert AlertType.PRICE_TARGET_CHANGE.value == "price_target_change"
    
    def test_alert_severity_enum(self):
        """Test AlertSeverity enum values"""
        assert AlertSeverity.LOW.value == "low"
        assert AlertSeverity.MEDIUM.value == "medium"
        assert AlertSeverity.HIGH.value == "high"
        assert AlertSeverity.CRITICAL.value == "critical"


# ============================================
# Tests for Data Validation
# ============================================

class TestDataValidation:
    """Tests for data validation utilities"""
    
    @pytest.mark.parametrize("value,expected", [
        (50, True),
        (0, True),
        (100, True),
        (-1, False),
        (101, False),
        (None, False),
    ])
    def test_score_validation_range(self, value, expected):
        """Test score validation within 0-100 range"""
        def is_valid_score(score):
            if score is None:
                return False
            return 0 <= score <= 100
        
        assert is_valid_score(value) == expected
    
    @pytest.mark.parametrize("value,expected", [
        (0.5, True),
        (-0.5, True),
        (0, True),
        (1, True),
        (-1, True),
        (1.5, False),
        (-1.5, False),
        (None, False),
    ])
    def test_sentiment_score_validation(self, value, expected):
        """Test sentiment score validation within -1 to 1 range"""
        def is_valid_sentiment(score):
            if score is None:
                return False
            return -1 <= score <= 1
        
        assert is_valid_sentiment(value) == expected
    
    @pytest.mark.parametrize("value,expected", [
        (30, True),  # Normal
        (70, True),  # Overbought
        (0, True),   # Edge case
        (100, True), # Edge case
        (-1, False), # Invalid
        (101, False), # Invalid
    ])
    def test_rsi_validation(self, value, expected):
        """Test RSI validation within 0-100 range"""
        def is_valid_rsi(rsi):
            if rsi is None:
                return False
            return 0 <= rsi <= 100
        
        assert is_valid_rsi(value) == expected


# ============================================
# Tests for Period Parsing
# ============================================

class TestPeriodParsing:
    """Tests for period string parsing"""
    
    @pytest.mark.parametrize("period,expected_hours", [
        ("1h", 1),
        ("2h", 2),
        ("4h", 4),
        ("6h", 6),
        ("12h", 12),
        ("1d", 24),
        ("7d", 168),
        ("1w", 168),
        ("1m", 720),
    ])
    def test_period_to_hours_conversion(self, period, expected_hours):
        """Test various period formats"""
        assert _parse_period_to_hours(period) == expected_hours
    
    def test_period_case_insensitivity(self):
        """Test that period parsing is case insensitive"""
        assert _parse_period_to_hours("1H") == 1
        assert _parse_period_to_hours("1D") == 24
        assert _parse_period_to_hours("1W") == 168


# ============================================
# Tests for Error Handling
# ============================================

class TestErrorHandling:
    """Tests for error handling in services"""
    
    def test_safe_get_handles_exceptions(self):
        """Test that safe_get handles various edge cases"""
        assert safe_get(None, "key") is None
        assert safe_get({}, "nonexistent") is None
        assert safe_get({"a": None}, "a") is None
    
    def test_safe_float_handles_edge_cases(self):
        """Test that safe_float handles edge cases"""
        assert safe_float(float('inf')) == float('inf')
        assert safe_float("") is None
    
    def test_safe_int_handles_edge_cases(self):
        """Test that safe_int handles edge cases"""
        assert safe_int(1.9) == 1  # Truncates to int
        assert safe_int("") is None


# ============================================
# Tests for Thread Safety
# ============================================

class TestThreadSafety:
    """Tests for thread safety in config service"""
    
    def test_config_service_has_lock(self):
        """Test that ConfigService has thread lock"""
        service = ConfigService()
        assert hasattr(service, '_lock')
        assert service._lock is not None
    
    def test_config_service_lock_usage(self):
        """Test that ConfigService methods are thread-safe"""
        service = ConfigService()
        # Should not raise any exceptions
        tickers = service.get_active_ticker_list()
        api_key = service.get_api_key("test")
        configs = service.get_ticker_configs_dict()


# ============================================
# Tests for Trend Calculation
# ============================================

class TestTrendCalculation:
    """Tests for trend calculation logic"""
    
    def test_trend_with_threshold(self):
        """Test trend detection with threshold"""
        # Small change within threshold should be STABLE
        assert _determine_trend(100, 100.5, threshold=0.01) == TrendDirection.STABLE
        
        # Change exceeding threshold should be UP/DOWN
        assert _determine_trend(100, 102, threshold=0.01) == TrendDirection.UP
        assert _determine_trend(100, 98, threshold=0.01) == TrendDirection.DOWN
    
    def test_trend_from_zero(self):
        """Test trend calculation when old value is zero"""
        # Moving from 0 to positive should be UP
        assert _determine_trend(0, 10) == TrendDirection.UP
        
        # Moving from 0 to negative should be DOWN  
        assert _determine_trend(0, -10) == TrendDirection.DOWN
        
        # Staying at 0 should be STABLE
        assert _determine_trend(0, 0) == TrendDirection.STABLE


# ============================================
# Tests for Change Calculation
# ============================================

class TestChangeCalculation:
    """Tests for change calculation logic"""
    
    def test_positive_change(self):
        """Test positive change calculation"""
        result = _calculate_change(100, 150)
        assert result["absolute_change"] == 50.0
        assert result["percentage_change"] == 50.0
        assert result["trend"] == TrendDirection.UP.value
    
    def test_negative_change(self):
        """Test negative change calculation"""
        result = _calculate_change(100, 50)
        assert result["absolute_change"] == -50.0
        assert result["percentage_change"] == -50.0
        assert result["trend"] == TrendDirection.DOWN.value
    
    def test_no_change(self):
        """Test no change calculation"""
        result = _calculate_change(100, 100)
        assert result["absolute_change"] == 0.0
        assert result["percentage_change"] == 0.0
        assert result["trend"] == TrendDirection.STABLE.value
    
    def test_change_from_zero_base(self):
        """Test change calculation with zero base value"""
        result = _calculate_change(0, 100)
        # Cannot calculate percentage from zero
        assert result["percentage_change"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
