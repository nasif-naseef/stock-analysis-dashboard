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


# ============================================
# Tests for ResponseBuilder (Data Processor)
# ============================================

class TestResponseBuilder:
    """Tests for ResponseBuilder in data_processor.py"""
    
    def test_build_analyst_consensus_with_tipranks_format(self):
        """Test parsing TipRanks API format with analystConsensus/analystPriceTarget"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # TipRanks format API response
        raw_data = {
            "analystConsensus": {
                "numberOfAnalystRatings": 35,
                "buy": 21,
                "hold": 12,
                "sell": 2,
                "consensus": "Moderate Buy",
                "consensusRating": 4
            },
            "analystPriceTarget": {
                "average": 289.17,
                "high": 345.0,
                "low": 225.0
            }
        }
        
        result = builder.build_analyst_consensus(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["buy_ratings"] == 21
        assert result["hold_ratings"] == 12
        assert result["sell_ratings"] == 2
        assert result["total_ratings"] == 35
        assert result["price_target_average"] == 289.17
        assert result["price_target_high"] == 345.0
        assert result["price_target_low"] == 225.0
        assert result["consensus_rating_score"] == 4
        assert result["consensus_recommendation"] == "Moderate Buy"
    
    def test_build_analyst_consensus_with_empty_data(self):
        """Test parsing empty data"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        result = builder.build_analyst_consensus({}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["buy_ratings"] is None
        assert result["hold_ratings"] is None
        assert result["sell_ratings"] is None
        assert result["total_ratings"] is None
        assert result["price_target_average"] is None
    
    def test_build_analyst_consensus_with_list_response(self):
        """Test parsing list response (extracts first item)"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        raw_data = [{
            "analystConsensus": {
                "numberOfAnalystRatings": 10,
                "buy": 5,
                "hold": 3,
                "sell": 2,
                "consensus": "Buy",
                "consensusRating": 4.2
            },
            "analystPriceTarget": {
                "average": 100.0,
                "high": 120.0,
                "low": 80.0
            }
        }]
        
        result = builder.build_analyst_consensus(raw_data, "GOOG")
        
        assert result["ticker"] == "GOOG"
        assert result["buy_ratings"] == 5
        assert result["hold_ratings"] == 3
        assert result["sell_ratings"] == 2
        assert result["total_ratings"] == 10
        assert result["price_target_average"] == 100.0
    
    def test_build_news_sentiment_with_correct_paths(self):
        """Test news sentiment parsing with newsSentimentScore.stock and sector paths"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # TipRanks format with newsSentimentScore
        raw_data = {
            "newsSentimentScore": {
                "stock": {
                    "bullishPercent": 65.5,
                    "bearishPercent": 34.5
                },
                "sector": {
                    "bullishPercent": 55.0,
                    "bearishPercent": 45.0
                }
            }
        }
        
        result = builder.build_news_sentiment(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["stock_bullish_score"] == 65.5
        assert result["stock_bearish_score"] == 34.5
        assert result["sector_bullish_score"] == 55.0
        assert result["sector_bearish_score"] == 45.0
    
    def test_build_news_sentiment_with_empty_data(self):
        """Test news sentiment parsing with empty data"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        result = builder.build_news_sentiment({}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["stock_bullish_score"] is None
        assert result["stock_bearish_score"] is None
        assert result["sector_bullish_score"] is None
        assert result["sector_bearish_score"] is None
    
    def test_build_crowd_stats_with_correct_paths(self):
        """Test crowd statistics parsing with generalStatsAll path"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # TipRanks format with generalStatsAll
        raw_data = {
            "generalStatsAll": {
                "portfoliosHolding": 1500,
                "amountOfPortfolios": 25000,
                "percentAllocated": 3.5,
                "percentOverLast7Days": 1.2,
                "percentOverLast30Days": 5.8,
                "score": 7.5
            }
        }
        
        result = builder.build_crowd_stats(raw_data, "TSLA")
        
        assert result["ticker"] == "TSLA"
        assert result["portfolio_holding"] == 1500
        assert result["amount_of_portfolios"] == 25000
        assert result["percent_allocated"] == 3.5
        assert result["percent_over_last_7d"] == 1.2
        assert result["percent_over_last_30d"] == 5.8
        assert result["score"] == 7.5
    
    def test_build_crowd_stats_with_stats_type(self):
        """Test crowd statistics with different stats types"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        raw_data = {
            "generalStatsIndividual": {
                "portfoliosHolding": 1000,
                "score": 6.5
            }
        }
        
        result = builder.build_crowd_stats(raw_data, "NVDA", stats_type='individual')
        
        assert result["ticker"] == "NVDA"
        assert result["portfolio_holding"] == 1000
        assert result["score"] == 6.5
    
    def test_build_crowd_stats_with_empty_data(self):
        """Test crowd statistics with empty data"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        result = builder.build_crowd_stats({}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["portfolio_holding"] == 0
        assert result["amount_of_portfolios"] == 0
        assert result["percent_allocated"] == 0.0
        assert result["score"] == 0.0
    
    def test_build_hedge_fund_with_overview_path(self):
        """Test hedge fund data parsing with overview.hedgeFundData path"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # TipRanks format with overview.hedgeFundData
        raw_data = {
            "overview": {
                "hedgeFundData": {
                    "sentiment": 0.75,
                    "trendAction": 2,
                    "trendValue": 15
                }
            }
        }
        
        result = builder.build_hedge_fund(raw_data, "GOOGL")
        
        assert result["ticker"] == "GOOGL"
        assert result["sentiment"] == 0.75
        assert result["trend_action"] == 2
        assert result["trend_value"] == 15
    
    def test_build_hedge_fund_with_empty_data(self):
        """Test hedge fund data with empty data"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        result = builder.build_hedge_fund({}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["sentiment"] is None
        assert result["trend_action"] is None
        assert result["trend_value"] is None
    
    def test_build_article_distribution_with_topics_dataframe(self):
        """Test article distribution parsing using pandas DataFrame with column sums"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Notebook format with topics containing news, social, web, total columns
        raw_data = {
            "topics": [
                {"name": "Topic A", "news": 10, "social": 20, "web": 5, "total": 35},
                {"name": "Topic B", "news": 15, "social": 25, "web": 10, "total": 50},
            ]
        }
        
        result = builder.build_article_distribution(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["news_count"] == 25  # 10 + 15
        assert result["social_count"] == 45  # 20 + 25
        assert result["web_count"] == 15  # 5 + 10
        assert result["total_articles"] == 85  # 35 + 50
    
    def test_build_article_distribution_empty_topics(self):
        """Test article distribution with empty topics"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        result = builder.build_article_distribution({"topics": []}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["total_articles"] == 0
        assert result["news_count"] == 0
        assert result["social_count"] == 0
        assert result["web_count"] == 0
    
    def test_build_article_sentiment_with_nested_structure(self):
        """Test article sentiment parsing with nested arrays"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Notebook format with sentiment_responses structure
        sentiment_responses = {
            "sentiment": [{"sentiment": {"id": 1, "label": "positive", "value": 75}}],
            "subjectivity": [{"subjectivity": {"id": 2, "label": "subjective", "value": 60}}],
            "confidence": [{"confidence": {"id": 3, "name": "high"}}]
        }
        
        result = builder.build_article_sentiment(sentiment_responses, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["sentiment_id"] == 1
        assert result["sentiment_label"] == "positive"
        assert result["sentiment_value"] == 75
        assert result["subjectivity_id"] == 2
        assert result["subjectivity_label"] == "subjective"
        assert result["subjectivity_value"] == 60
        assert result["confidence_id"] == 3
        assert result["confidence_name"] == "high"
    
    def test_build_article_sentiment_empty_data(self):
        """Test article sentiment with empty arrays"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        result = builder.build_article_sentiment({}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["sentiment_id"] is None
        assert result["sentiment_label"] is None
        assert result["sentiment_value"] is None
    
    def test_build_support_resistance_with_prefixed_keys(self):
        """Test support/resistance parsing with support10, resistance10 keys"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Notebook format with prefixed keys
        raw_item = {
            "instrument": {"symbol": "AAPL", "exchange": "NASDAQ"},
            "date": "2024-01-15",
            "support": {
                "support10": 150.5,
                "support20": 148.0,
                "support40": 145.0,
                "support100": 140.0,
                "support250": 135.0,
                "support500": 130.0
            },
            "resistance": {
                "resistance10": 155.5,
                "resistance20": 158.0,
                "resistance40": 160.0,
                "resistance100": 165.0,
                "resistance250": 170.0,
                "resistance500": 175.0
            }
        }
        
        result = builder.build_support_resistance(raw_item)
        
        assert result["symbol"] == "AAPL"
        assert result["date"] == "2024-01-15"
        assert result["exchange"] == "NASDAQ"
        assert result["support_10"] == 150.5
        assert result["resistance_10"] == 155.5
        assert result["support_20"] == 148.0
        assert result["resistance_20"] == 158.0
    
    def test_build_support_resistance_empty_data(self):
        """Test support/resistance with empty data"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        result = builder.build_support_resistance({})
        
        assert result["symbol"] == "N/A"
        assert result["date"] == "N/A"
        assert result["support_10"] is None
        assert result["resistance_10"] is None
    
    def test_build_stop_loss_uses_first_element(self):
        """Test stop loss uses first element [0] not last element [-1]"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        raw_data = {
            "stops": [100.0, 95.0, 90.0],  # First should be used
            "timestamps": ["2024-01-01", "2024-01-02", "2024-01-03"]
        }
        
        result = builder.build_stop_loss(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["recommended_stop_price"] == 100.0  # First element
        assert result["calculation_timestamp"] == "2024-01-01"  # First element
    
    def test_build_stop_loss_empty_data(self):
        """Test stop loss with empty arrays"""
        from app.utils.data_processor import ResponseBuilder
        
        builder = ResponseBuilder()
        
        result = builder.build_stop_loss({}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["recommended_stop_price"] is None
        assert result["calculation_timestamp"] is None
    
    def test_build_chart_events_dataframe_with_events_key(self):
        """Test chart events returns DataFrame with events key check"""
        from app.utils.data_processor import ResponseBuilder
        import pandas as pd
        
        builder = ResponseBuilder()
        
        raw_data = {
            "events": [
                {"id": 1, "type": "breakout", "price": 150.0},
                {"id": 2, "type": "breakdown", "price": 145.0}
            ]
        }
        
        result = builder.build_chart_events_dataframe(raw_data, "AAPL")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "ticker" in result.columns
        assert "is_active" in result.columns
        assert result["ticker"].iloc[0] == "AAPL"
    
    def test_build_chart_events_dataframe_no_events_key(self):
        """Test chart events returns empty DataFrame when no events key"""
        from app.utils.data_processor import ResponseBuilder
        import pandas as pd
        
        builder = ResponseBuilder()
        
        result = builder.build_chart_events_dataframe({}, "TEST")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_build_technical_summaries_dataframe_with_categories(self):
        """Test technical summaries with instrument items and categories"""
        from app.utils.data_processor import ResponseBuilder
        import pandas as pd
        
        builder = ResponseBuilder()
        
        raw_data = {
            "scores": [
                {
                    "instrument": {
                        "symbol": "AAPL",
                        "name": "Apple Inc",
                        "exchange": "NASDAQ",
                        "isin": "US0378331005",
                        "instrumentId": "123"
                    },
                    "intermediate": {"score": 7.5, "signal": "buy"},
                    "long": {"score": 8.0, "signal": "strong_buy"}
                }
            ]
        }
        
        result = builder.build_technical_summaries_dataframe(raw_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 6  # 6 categories per instrument
        assert "symbol" in result.columns
        assert "category" in result.columns
        assert "AAPL" in result["symbol"].values
    
    def test_build_technical_summaries_dataframe_no_scores(self):
        """Test technical summaries with no scores key"""
        from app.utils.data_processor import ResponseBuilder
        import pandas as pd
        
        builder = ResponseBuilder()
        
        result = builder.build_technical_summaries_dataframe({})
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_build_quantamental_timeseries_dataframe_all_columns(self):
        """Test quantamental timeseries includes all score columns"""
        from app.utils.data_processor import ResponseBuilder
        import pandas as pd
        
        builder = ResponseBuilder()
        
        raw_data = {
            "timestamps": ["2024-01-01", "2024-01-02"],
            "quantamental": [75, 80],
            "growth": [70, 72],
            "income": [65, 68],
            "momentum": [80, 85],
            "quality": [90, 92],
            "valuation": [60, 62]
        }
        
        result = builder.build_quantamental_timeseries_dataframe(raw_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "timestamp" in result.columns
        assert "quantamental_score" in result.columns
        assert "growth_score" in result.columns
        assert "income_score" in result.columns
        assert "momentum_score" in result.columns
        assert "quality_score" in result.columns
        assert "valuation_score" in result.columns
    
    def test_build_quantamental_timeseries_dataframe_with_list(self):
        """Test quantamental timeseries handles list input by using first element"""
        from app.utils.data_processor import ResponseBuilder
        import pandas as pd
        
        builder = ResponseBuilder()
        
        raw_data = [{
            "timestamps": ["2024-01-01"],
            "quantamental": [75],
            "growth": [70],
            "income": [65],
            "momentum": [80],
            "quality": [90],
            "valuation": [60]
        }]
        
        result = builder.build_quantamental_timeseries_dataframe(raw_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "quantamental_score" in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
