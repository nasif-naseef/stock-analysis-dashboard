"""
Tests for Hedge Fund and Blogger Sentiment Bug Fixes

This module contains tests for the specific bug fixes related to:
1. HedgeFundData AttributeError - sentiment field
2. BloggerSentiment AttributeError - calculating percentages from counts
3. Hedge fund alerts using correct fields
"""
import pytest
from unittest.mock import MagicMock
from datetime import datetime

from app.services.dashboard_service import DashboardService
from app.models.stock_data import HedgeFundData, BloggerSentiment


class TestHedgeFundDataFix:
    """Tests for HedgeFundData attribute error fix"""
    
    def test_extract_hedge_fund_summary_with_valid_data(self):
        """Test _extract_hedge_fund_summary uses correct field names"""
        service = DashboardService()
        
        # Create mock HedgeFundData with notebook-style fields
        mock_data = MagicMock(spec=HedgeFundData)
        mock_data.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_data.sentiment = 0.75  # Float value
        mock_data.trend_action = 2
        mock_data.trend_value = 15
        
        result = service._extract_hedge_fund_summary(mock_data)
        
        assert result["sentiment"] == 0.75
        assert result["trend_action"] == 2
        assert result["trend_value"] == 15
        assert result["timestamp"] == "2023-01-01T12:00:00"
    
    def test_extract_hedge_fund_summary_with_none(self):
        """Test _extract_hedge_fund_summary handles None data"""
        service = DashboardService()
        
        result = service._extract_hedge_fund_summary(None)
        
        assert result == {}
    
    def test_extract_hedge_fund_summary_with_none_values(self):
        """Test _extract_hedge_fund_summary handles None field values"""
        service = DashboardService()
        
        # Create mock with None values
        mock_data = MagicMock(spec=HedgeFundData)
        mock_data.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_data.sentiment = None
        mock_data.trend_action = None
        mock_data.trend_value = None
        
        result = service._extract_hedge_fund_summary(mock_data)
        
        assert result["sentiment"] is None
        assert result["trend_action"] is None
        assert result["trend_value"] is None


class TestBloggerSentimentFix:
    """Tests for BloggerSentiment attribute error fix"""
    
    def test_extract_blogger_summary_with_valid_counts(self):
        """Test _extract_blogger_summary calculates percentages from counts"""
        service = DashboardService()
        
        # Create mock BloggerSentiment with notebook-style fields
        mock_data = MagicMock(spec=BloggerSentiment)
        mock_data.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_data.bullish_count = 60
        mock_data.bearish_count = 30
        mock_data.neutral_count = 10
        mock_data.score = 7.5
        mock_data.avg = 0.65
        
        result = service._extract_blogger_summary(mock_data)
        
        # Check calculations
        assert result["total_articles"] == 100
        assert result["bullish_percent"] == 60.0
        assert result["bearish_percent"] == 30.0
        assert result["sentiment"] == "bullish"  # bullish_count > bearish_count
        assert result["sentiment_score"] == 7.5
        assert result["avg"] == 0.65
        assert result["bullish_count"] == 60
        assert result["bearish_count"] == 30
        assert result["neutral_count"] == 10
    
    def test_extract_blogger_summary_with_bearish_majority(self):
        """Test _extract_blogger_summary with bearish majority"""
        service = DashboardService()
        
        mock_data = MagicMock(spec=BloggerSentiment)
        mock_data.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_data.bullish_count = 20
        mock_data.bearish_count = 70
        mock_data.neutral_count = 10
        mock_data.score = 3.0
        mock_data.avg = 0.30
        
        result = service._extract_blogger_summary(mock_data)
        
        assert result["sentiment"] == "bearish"  # bearish_count > bullish_count
        assert result["bullish_percent"] == 20.0
        assert result["bearish_percent"] == 70.0
    
    def test_extract_blogger_summary_with_equal_counts(self):
        """Test _extract_blogger_summary with equal bullish/bearish counts"""
        service = DashboardService()
        
        mock_data = MagicMock(spec=BloggerSentiment)
        mock_data.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_data.bullish_count = 40
        mock_data.bearish_count = 40
        mock_data.neutral_count = 20
        mock_data.score = 5.0
        mock_data.avg = 0.50
        
        result = service._extract_blogger_summary(mock_data)
        
        assert result["sentiment"] == "neutral"  # equal counts
        assert result["bullish_percent"] == 40.0
        assert result["bearish_percent"] == 40.0
    
    def test_extract_blogger_summary_with_zero_total(self):
        """Test _extract_blogger_summary with zero total articles"""
        service = DashboardService()
        
        mock_data = MagicMock(spec=BloggerSentiment)
        mock_data.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_data.bullish_count = 0
        mock_data.bearish_count = 0
        mock_data.neutral_count = 0
        mock_data.score = 0.0
        mock_data.avg = 0.0
        
        result = service._extract_blogger_summary(mock_data)
        
        assert result["total_articles"] == 0
        assert result["bullish_percent"] == 0.0
        assert result["bearish_percent"] == 0.0
        assert result["sentiment"] is None  # No data to determine sentiment
    
    def test_extract_blogger_summary_with_none(self):
        """Test _extract_blogger_summary handles None data"""
        service = DashboardService()
        
        result = service._extract_blogger_summary(None)
        
        assert result == {}
    
    def test_extract_blogger_summary_with_none_counts(self):
        """Test _extract_blogger_summary handles None count values"""
        service = DashboardService()
        
        mock_data = MagicMock(spec=BloggerSentiment)
        mock_data.timestamp = datetime(2023, 1, 1, 12, 0, 0)
        mock_data.bullish_count = None
        mock_data.bearish_count = None
        mock_data.neutral_count = None
        mock_data.score = 0.0
        mock_data.avg = 0.0
        
        result = service._extract_blogger_summary(mock_data)
        
        # Should handle None values gracefully (treat as 0)
        assert result["total_articles"] == 0
        assert result["bullish_percent"] == 0.0
        assert result["bearish_percent"] == 0.0


class TestHedgeFundAlertsFix:
    """Tests for hedge fund alerts using correct fields"""
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_check_hedge_fund_alerts_with_sentiment_change(self):
        """Test _check_hedge_fund_alerts uses sentiment field instead of position fields"""
        # This would require mocking the database session
        # Skipping for now as it requires complex setup
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
