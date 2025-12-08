"""
Tests for Bug Fixes

This module contains tests for specific bug fixes related to:
1. NewsSentiment attribute error
2. raw_data validation error for QuantamentalScore and TargetPrice
3. TimeframeType enum PostgreSQL error
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.services.dashboard_service import DashboardService
from app.models.stock_data import NewsSentiment, QuantamentalScore, TargetPrice, TechnicalIndicator, TimeframeType
from app.schemas.stock_schemas import QuantamentalScoreResponse, TargetPriceResponse


class TestNewsSentimentFix:
    """Tests for NewsSentiment attribute error fix"""
    
    def test_extract_sentiment_summary_with_bullish_scores(self):
        """Test _extract_sentiment_summary with bullish scores"""
        service = DashboardService()
        
        # Create mock NewsSentiment with bullish score higher than bearish
        mock_sentiment = MagicMock(spec=NewsSentiment)
        mock_sentiment.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_sentiment.stock_bullish_score = 0.75
        mock_sentiment.stock_bearish_score = 0.25
        mock_sentiment.sector_bullish_score = 0.65
        mock_sentiment.sector_bearish_score = 0.35
        
        result = service._extract_sentiment_summary(mock_sentiment)
        
        assert result["sentiment"] == "bullish"
        assert result["stock_bullish_score"] == 0.75
        assert result["stock_bearish_score"] == 0.25
        assert result["sector_bullish_score"] == 0.65
        assert result["sector_bearish_score"] == 0.35
        assert result["timestamp"] == "2023-01-01T12:00:00"
    
    def test_extract_sentiment_summary_with_bearish_scores(self):
        """Test _extract_sentiment_summary with bearish scores"""
        service = DashboardService()
        
        # Create mock NewsSentiment with bearish score higher than bullish
        mock_sentiment = MagicMock(spec=NewsSentiment)
        mock_sentiment.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_sentiment.stock_bullish_score = 0.30
        mock_sentiment.stock_bearish_score = 0.70
        mock_sentiment.sector_bullish_score = 0.40
        mock_sentiment.sector_bearish_score = 0.60
        
        result = service._extract_sentiment_summary(mock_sentiment)
        
        assert result["sentiment"] == "bearish"
        assert result["stock_bullish_score"] == 0.30
        assert result["stock_bearish_score"] == 0.70
    
    def test_extract_sentiment_summary_with_neutral_scores(self):
        """Test _extract_sentiment_summary with equal bullish and bearish scores"""
        service = DashboardService()
        
        # Create mock NewsSentiment with equal scores
        mock_sentiment = MagicMock(spec=NewsSentiment)
        mock_sentiment.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_sentiment.stock_bullish_score = 0.50
        mock_sentiment.stock_bearish_score = 0.50
        mock_sentiment.sector_bullish_score = 0.50
        mock_sentiment.sector_bearish_score = 0.50
        
        result = service._extract_sentiment_summary(mock_sentiment)
        
        assert result["sentiment"] == "neutral"
        assert result["stock_bullish_score"] == 0.50
        assert result["stock_bearish_score"] == 0.50
    
    def test_extract_sentiment_summary_with_none_scores(self):
        """Test _extract_sentiment_summary with None scores"""
        service = DashboardService()
        
        # Create mock NewsSentiment with None scores
        mock_sentiment = MagicMock(spec=NewsSentiment)
        mock_sentiment.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_sentiment.stock_bullish_score = None
        mock_sentiment.stock_bearish_score = None
        mock_sentiment.sector_bullish_score = None
        mock_sentiment.sector_bearish_score = None
        mock_sentiment.raw_data = None  # Explicitly set to None to prevent MagicMock issues
        
        result = service._extract_sentiment_summary(mock_sentiment)
        
        assert result["sentiment"] is None
        assert result["stock_bullish_score"] is None
        assert result["stock_bearish_score"] is None
    
    def test_extract_sentiment_summary_with_none_data(self):
        """Test _extract_sentiment_summary with None data"""
        service = DashboardService()
        
        result = service._extract_sentiment_summary(None)
        
        assert result == {}


class TestRawDataValidationFix:
    """Tests for raw_data validation error fix"""
    
    def test_quantamental_score_response_with_dict_raw_data(self):
        """Test QuantamentalScoreResponse accepts dict raw_data"""
        data = {
            "id": 1,
            "ticker": "AAPL",
            "timestamp": datetime(2023, 1, 1),
            "overall_score": 85.0,
            "quality_score": 90.0,
            "value_score": 80.0,
            "growth_score": 85.0,
            "momentum_score": 88.0,
            "source": "tipranks",
            "raw_data": {"key": "value", "nested": {"data": 123}}
        }
        
        # Should not raise validation error
        response = QuantamentalScoreResponse(**data)
        assert response.ticker == "AAPL"
        assert response.raw_data == {"key": "value", "nested": {"data": 123}}
    
    def test_quantamental_score_response_with_list_raw_data(self):
        """Test QuantamentalScoreResponse accepts list raw_data"""
        data = {
            "id": 1,
            "ticker": "AAPL",
            "timestamp": datetime(2023, 1, 1),
            "overall_score": 85.0,
            "quality_score": 90.0,
            "value_score": 80.0,
            "growth_score": 85.0,
            "momentum_score": 88.0,
            "source": "tipranks",
            "raw_data": [{"item": 1}, {"item": 2}]
        }
        
        # Should not raise validation error
        response = QuantamentalScoreResponse(**data)
        assert response.ticker == "AAPL"
        assert response.raw_data == [{"item": 1}, {"item": 2}]
    
    def test_target_price_response_with_list_raw_data(self):
        """Test TargetPriceResponse accepts list raw_data"""
        data = {
            "id": 1,
            "ticker": "AAPL",
            "timestamp": datetime(2023, 1, 1),
            "target_price": 200.0,
            "current_price_at_rating": 180.0,
            "source": "tipranks",
            "raw_data": [{"analyst": "ABC"}, {"analyst": "XYZ"}]
        }
        
        # Should not raise validation error
        response = TargetPriceResponse(**data)
        assert response.ticker == "AAPL"
        assert response.raw_data == [{"analyst": "ABC"}, {"analyst": "XYZ"}]


class TestTimeframeTypeEnumFix:
    """Tests for TimeframeType enum PostgreSQL error fix"""
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_technical_indicator_filter_uses_enum_value(self):
        """Test that filtering by timeframe uses enum value instead of enum object"""
        from app.api.current_data import router
        from app.database import get_db
        from sqlalchemy.orm import Session
        
        # This test verifies the fix is applied correctly
        # The actual filtering logic should use timeframe.value
        # This test would need a real database to execute the query
        pass
    
    def test_timeframe_enum_has_correct_values(self):
        """Test that TimeframeType enum has the expected string values"""
        assert TimeframeType.ONE_DAY.value == "1d"
        assert TimeframeType.ONE_HOUR.value == "1h"
        assert TimeframeType.ONE_WEEK.value == "1w"
        assert TimeframeType.ONE_MONTH.value == "1M"


class TestQuantamentalScoreFieldMapping:
    """Tests for QuantamentalScore field name mapping fix"""
    
    def test_extract_quantamental_summary_with_valid_data(self):
        """Test _extract_quantamental_summary uses correct field names"""
        service = DashboardService()
        
        # Create mock QuantamentalScore with correct field names
        mock_score = MagicMock(spec=QuantamentalScore)
        mock_score.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_score.overall = 85
        mock_score.quality = 90
        mock_score.value = 80
        mock_score.growth = 85
        mock_score.momentum = 88
        
        result = service._extract_quantamental_summary(mock_score)
        
        assert result["overall_score"] == 85
        assert result["quality_score"] == 90
        assert result["value_score"] == 80
        assert result["growth_score"] == 85
        assert result["momentum_score"] == 88
        assert result["timestamp"] == "2023-01-01T12:00:00"
    
    def test_extract_quantamental_summary_with_none(self):
        """Test _extract_quantamental_summary handles None data"""
        service = DashboardService()
        
        result = service._extract_quantamental_summary(None)
        
        assert result == {}
    
    def test_extract_quantamental_summary_with_none_values(self):
        """Test _extract_quantamental_summary handles None field values"""
        service = DashboardService()
        
        # Create mock with None values
        mock_score = MagicMock(spec=QuantamentalScore)
        mock_score.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_score.overall = None
        mock_score.quality = None
        mock_score.value = None
        mock_score.growth = None
        mock_score.momentum = None
        
        result = service._extract_quantamental_summary(mock_score)
        
        assert result["overall_score"] is None
        assert result["quality_score"] is None
        assert result["value_score"] is None
        assert result["growth_score"] is None
        assert result["momentum_score"] is None
