"""
Tests for News Sentiment N/A Display and toFixed Fixes

This module tests the fixes for:
1. News sentiment raw_data fallback extraction
2. Dashboard service sentiment summary extraction with fallback
"""
import pytest
from unittest.mock import MagicMock
from datetime import datetime

from app.services.dashboard_service import DashboardService
from app.models.stock_data import NewsSentiment


class TestNewsSentimentFixes:
    """Tests for news sentiment fixes"""

    def test_extract_sentiment_summary_with_direct_values(self):
        """Test sentiment extraction when model has direct values"""
        service = DashboardService()
        
        # Create mock NewsSentiment with direct values
        mock_data = MagicMock(spec=NewsSentiment)
        mock_data.timestamp = datetime.now()
        mock_data.stock_bullish_score = 65.5
        mock_data.stock_bearish_score = 34.5
        mock_data.sector_bullish_score = 70.0
        mock_data.sector_bearish_score = 30.0
        mock_data.raw_data = None
        
        result = service._extract_sentiment_summary(mock_data)
        
        assert result["stock_bullish_score"] == 65.5
        assert result["stock_bearish_score"] == 34.5
        assert result["sector_bullish_score"] == 70.0
        assert result["sector_bearish_score"] == 30.0
        assert result["sentiment"] == "bullish"

    def test_extract_sentiment_summary_with_raw_data_fallback(self):
        """Test sentiment extraction falls back to raw_data when model values are None"""
        service = DashboardService()
        
        # Create mock NewsSentiment with null direct values but valid raw_data
        mock_data = MagicMock(spec=NewsSentiment)
        mock_data.timestamp = datetime.now()
        mock_data.stock_bullish_score = None
        mock_data.stock_bearish_score = None
        mock_data.sector_bullish_score = None
        mock_data.sector_bearish_score = None
        mock_data.raw_data = {
            "newsSentimentScore": {
                "stock": {
                    "bullishPercent": 55.2,
                    "bearishPercent": 44.8
                },
                "sector": {
                    "bullishPercent": 60.0,
                    "bearishPercent": 40.0
                }
            }
        }
        
        result = service._extract_sentiment_summary(mock_data)
        
        assert result["stock_bullish_score"] == 55.2
        assert result["stock_bearish_score"] == 44.8
        assert result["sector_bullish_score"] == 60.0
        assert result["sector_bearish_score"] == 40.0
        assert result["sentiment"] == "bullish"

    def test_extract_sentiment_summary_bearish_sentiment(self):
        """Test sentiment calculation for bearish case"""
        service = DashboardService()
        
        mock_data = MagicMock(spec=NewsSentiment)
        mock_data.timestamp = datetime.now()
        mock_data.stock_bullish_score = None
        mock_data.stock_bearish_score = None
        mock_data.sector_bullish_score = None
        mock_data.sector_bearish_score = None
        mock_data.raw_data = {
            "newsSentimentScore": {
                "stock": {
                    "bullishPercent": 30.0,
                    "bearishPercent": 70.0
                },
                "sector": {
                    "bullishPercent": 35.0,
                    "bearishPercent": 65.0
                }
            }
        }
        
        result = service._extract_sentiment_summary(mock_data)
        
        assert result["sentiment"] == "bearish"

    def test_extract_sentiment_summary_neutral_sentiment(self):
        """Test sentiment calculation for neutral case"""
        service = DashboardService()
        
        mock_data = MagicMock(spec=NewsSentiment)
        mock_data.timestamp = datetime.now()
        mock_data.stock_bullish_score = 50.0
        mock_data.stock_bearish_score = 50.0
        mock_data.sector_bullish_score = 50.0
        mock_data.sector_bearish_score = 50.0
        mock_data.raw_data = None
        
        result = service._extract_sentiment_summary(mock_data)
        
        assert result["sentiment"] == "neutral"

    def test_extract_sentiment_summary_with_no_data(self):
        """Test sentiment extraction returns empty dict when data is None"""
        service = DashboardService()
        
        result = service._extract_sentiment_summary(None)
        
        assert result == {}

    def test_extract_sentiment_summary_with_missing_raw_data_keys(self):
        """Test sentiment extraction handles missing keys in raw_data gracefully"""
        service = DashboardService()
        
        mock_data = MagicMock(spec=NewsSentiment)
        mock_data.timestamp = datetime.now()
        mock_data.stock_bullish_score = None
        mock_data.stock_bearish_score = None
        mock_data.sector_bullish_score = None
        mock_data.sector_bearish_score = None
        mock_data.raw_data = {
            "newsSentimentScore": {}
        }
        
        result = service._extract_sentiment_summary(mock_data)
        
        # Should have None values since raw_data doesn't have the expected structure
        assert result["stock_bullish_score"] is None
        assert result["stock_bearish_score"] is None
        assert result["sentiment"] is None

    def test_extract_sentiment_summary_with_empty_raw_data(self):
        """Test sentiment extraction when raw_data is empty dict"""
        service = DashboardService()
        
        mock_data = MagicMock(spec=NewsSentiment)
        mock_data.timestamp = datetime.now()
        mock_data.stock_bullish_score = None
        mock_data.stock_bearish_score = None
        mock_data.sector_bullish_score = None
        mock_data.sector_bearish_score = None
        mock_data.raw_data = {}
        
        result = service._extract_sentiment_summary(mock_data)
        
        assert result["stock_bullish_score"] is None
        assert result["stock_bearish_score"] is None
        assert result["sentiment"] is None
