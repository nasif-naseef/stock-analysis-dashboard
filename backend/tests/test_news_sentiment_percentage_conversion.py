"""
Tests for News Sentiment Percentage Conversion Fix

This module tests the fixes for converting sentiment values from decimal (0-1) 
to percentage (0-100) format in both response builder and API endpoint.
"""
import pytest
from app.utils.data_processor import ResponseBuilder
from app.api.stock import get_news_sentiment


class TestNewsSentimentPercentageConversion:
    """Tests for news sentiment percentage conversion"""

    def test_build_news_sentiment_converts_decimal_to_percentage(self):
        """Test that build_news_sentiment converts decimal values (0-1) to percentage (0-100)"""
        builder = ResponseBuilder()
        
        # Mock raw data with decimal values (0-1)
        raw_data = {
            "newsSentimentScore": {
                "stock": {
                    "bullishPercent": 1.0,  # Should become 100.0
                    "bearishPercent": 0.0   # Should become 0.0
                },
                "sector": {
                    "bullishPercent": 0.6,  # Should become 60.0
                    "bearishPercent": 0.4   # Should become 40.0
                }
            }
        }
        
        result = builder.build_news_sentiment(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["stock_bullish_score"] == 100.0
        assert result["stock_bearish_score"] == 0.0
        assert result["sector_bullish_score"] == 60.0
        assert result["sector_bearish_score"] == 40.0

    def test_build_news_sentiment_handles_already_percentage_values(self):
        """Test that build_news_sentiment doesn't convert values already in percentage format"""
        builder = ResponseBuilder()
        
        # Mock raw data with percentage values (already 0-100)
        raw_data = {
            "newsSentimentScore": {
                "stock": {
                    "bullishPercent": 75.5,  # Already percentage, should stay 75.5
                    "bearishPercent": 24.5   # Already percentage, should stay 24.5
                },
                "sector": {
                    "bullishPercent": 65.0,  # Already percentage, should stay 65.0
                    "bearishPercent": 35.0   # Already percentage, should stay 35.0
                }
            }
        }
        
        result = builder.build_news_sentiment(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["stock_bullish_score"] == 75.5
        assert result["stock_bearish_score"] == 24.5
        assert result["sector_bullish_score"] == 65.0
        assert result["sector_bearish_score"] == 35.0

    def test_build_news_sentiment_handles_mixed_format(self):
        """Test that build_news_sentiment handles mixed decimal and percentage values"""
        builder = ResponseBuilder()
        
        # Mock raw data with mixed values
        raw_data = {
            "newsSentimentScore": {
                "stock": {
                    "bullishPercent": 0.8,   # Decimal, should become 80.0
                    "bearishPercent": 15.5   # Already percentage, should stay 15.5
                },
                "sector": {
                    "bullishPercent": 70.0,  # Already percentage, should stay 70.0
                    "bearishPercent": 0.3    # Decimal, should become 30.0
                }
            }
        }
        
        result = builder.build_news_sentiment(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["stock_bullish_score"] == 80.0
        assert result["stock_bearish_score"] == 15.5
        assert result["sector_bullish_score"] == 70.0
        assert result["sector_bearish_score"] == 30.0

    def test_build_news_sentiment_handles_null_values(self):
        """Test that build_news_sentiment handles null/None values gracefully"""
        builder = ResponseBuilder()
        
        # Mock raw data with null values
        raw_data = {
            "newsSentimentScore": {
                "stock": {
                    "bullishPercent": None,
                    "bearishPercent": None
                },
                "sector": {
                    "bullishPercent": None,
                    "bearishPercent": None
                }
            }
        }
        
        result = builder.build_news_sentiment(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["stock_bullish_score"] is None
        assert result["stock_bearish_score"] is None
        assert result["sector_bullish_score"] is None
        assert result["sector_bearish_score"] is None

    def test_build_news_sentiment_handles_empty_data(self):
        """Test that build_news_sentiment handles empty data structure"""
        builder = ResponseBuilder()
        
        # Mock raw data with empty structure
        raw_data = {
            "newsSentimentScore": {}
        }
        
        result = builder.build_news_sentiment(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["stock_bullish_score"] is None
        assert result["stock_bearish_score"] is None
        assert result["sector_bullish_score"] is None
        assert result["sector_bearish_score"] is None

    def test_build_news_sentiment_handles_missing_keys(self):
        """Test that build_news_sentiment handles missing keys gracefully"""
        builder = ResponseBuilder()
        
        # Mock raw data with missing keys
        raw_data = {}
        
        result = builder.build_news_sentiment(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["stock_bullish_score"] is None
        assert result["stock_bearish_score"] is None
        assert result["sector_bullish_score"] is None
        assert result["sector_bearish_score"] is None

    def test_build_news_sentiment_edge_case_exactly_one(self):
        """Test that value of exactly 1.0 is converted to 100.0"""
        builder = ResponseBuilder()
        
        raw_data = {
            "newsSentimentScore": {
                "stock": {
                    "bullishPercent": 1.0,
                    "bearishPercent": 1.0
                },
                "sector": {
                    "bullishPercent": 1.0,
                    "bearishPercent": 1.0
                }
            }
        }
        
        result = builder.build_news_sentiment(raw_data, "AAPL")
        
        # 1.0 should be converted to 100.0
        assert result["stock_bullish_score"] == 100.0
        assert result["stock_bearish_score"] == 100.0
        assert result["sector_bullish_score"] == 100.0
        assert result["sector_bearish_score"] == 100.0

    def test_build_news_sentiment_edge_case_zero(self):
        """Test that value of 0.0 remains 0.0 (not converted)"""
        builder = ResponseBuilder()
        
        raw_data = {
            "newsSentimentScore": {
                "stock": {
                    "bullishPercent": 0.0,
                    "bearishPercent": 0.0
                },
                "sector": {
                    "bullishPercent": 0.0,
                    "bearishPercent": 0.0
                }
            }
        }
        
        result = builder.build_news_sentiment(raw_data, "AAPL")
        
        # 0.0 stays 0.0 (but it's in range 0-1, so it gets multiplied by 100)
        assert result["stock_bullish_score"] == 0.0
        assert result["stock_bearish_score"] == 0.0
        assert result["sector_bullish_score"] == 0.0
        assert result["sector_bearish_score"] == 0.0
