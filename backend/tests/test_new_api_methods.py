"""
Tests for New API Methods

This module contains tests for the newly added API methods and service
layer changes to match the Final.ipynb notebook implementation.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.utils.api_client import APIClient
from app.utils.data_processor import ResponseBuilder
from app.services.stock_data_service import StockDataService


class TestFetchMultiple:
    """Tests for fetch_multiple method in APIClient"""
    
    def test_fetch_multiple_success(self):
        """Test parallel fetching of multiple URLs"""
        client = APIClient()
        
        # Mock the fetch method to return different data for each URL
        def mock_fetch(url, headers=None, use_cache=True):
            if 'sentiment' in url:
                return [{"sentiment": {"id": 1, "label": "positive"}}]
            elif 'subjectivity' in url:
                return [{"subjectivity": {"id": 2, "label": "subjective"}}]
            elif 'confidence' in url:
                return [{"confidence": {"id": 3, "name": "high"}}]
            return None
        
        with patch.object(client, 'fetch', side_effect=mock_fetch):
            urls = [
                ('sentiment', 'http://api.test/sentiment', None),
                ('subjectivity', 'http://api.test/subjectivity', None),
                ('confidence', 'http://api.test/confidence', None)
            ]
            
            result = client.fetch_multiple(urls)
            
            assert 'sentiment' in result
            assert 'subjectivity' in result
            assert 'confidence' in result
            assert result['sentiment'][0]['sentiment']['id'] == 1
            assert result['subjectivity'][0]['subjectivity']['id'] == 2
            assert result['confidence'][0]['confidence']['id'] == 3
    
    def test_fetch_multiple_with_failures(self):
        """Test fetch_multiple handles individual failures gracefully"""
        client = APIClient()
        
        # Mock fetch to fail for one URL
        def mock_fetch(url, headers=None, use_cache=True):
            if 'fail' in url:
                raise Exception("API Error")
            return {"success": True}
        
        with patch.object(client, 'fetch', side_effect=mock_fetch):
            urls = [
                ('success', 'http://api.test/success', None),
                ('fail', 'http://api.test/fail', None)
            ]
            
            result = client.fetch_multiple(urls)
            
            assert result['success'] == {"success": True}
            assert result['fail'] is None


class TestArticleSentimentFull:
    """Tests for fetch_tc_article_sentiment_full method"""
    
    def test_fetch_article_sentiment_full(self):
        """Test fetching article sentiment from 3 endpoints"""
        client = APIClient()
        client.tc_token = "test_token"
        
        mock_results = {
            'sentiment': [{"sentiment": {"id": 1, "label": "positive"}}],
            'subjectivity': [{"subjectivity": {"id": 2, "label": "subjective"}}],
            'confidence': [{"confidence": {"id": 3, "name": "high"}}]
        }
        
        with patch.object(client, 'fetch_multiple', return_value=mock_results):
            result = client.fetch_tc_article_sentiment_full("EQ-0C00000ADA")
            
            assert 'sentiment' in result
            assert 'subjectivity' in result
            assert 'confidence' in result
    
    def test_fetch_article_sentiment_full_no_token(self):
        """Test article sentiment without token configured"""
        client = APIClient()
        client.tc_token = None
        
        result = client.fetch_tc_article_sentiment_full("EQ-0C00000ADA")
        
        assert result['sentiment'] is None
        assert result['subjectivity'] is None
        assert result['confidence'] is None


class TestQuantamentalTimeseries:
    """Tests for fetch_tc_quantamental_timeseries method"""
    
    def test_fetch_quantamental_timeseries_with_dates(self):
        """Test quantamental timeseries with date range"""
        client = APIClient()
        client.tc_token = "test_token"
        
        mock_data = {
            "timestamps": ["2024-01-01", "2024-01-02"],
            "quantamental": [75, 80],
            "growth": [70, 72]
        }
        
        with patch.object(client, 'fetch_trading_central', return_value=mock_data):
            result = client.fetch_tc_quantamental_timeseries(
                "AAPL:NASDAQ",
                start_date="2024-01-01",
                end_date="2024-01-02"
            )
            
            assert result is not None
            assert "timestamps" in result
            assert len(result["timestamps"]) == 2


class TestSentimentTimeseries:
    """Tests for fetch_tc_sentiment_timeseries method"""
    
    def test_fetch_sentiment_timeseries(self):
        """Test sentiment timeseries endpoint"""
        client = APIClient()
        client.tc_token = "test_token"
        
        mock_data = {
            "dates": ["2024-01-01", "2024-01-02"],
            "sentiment": [0.75, 0.80]
        }
        
        with patch.object(client, 'fetch', return_value=mock_data):
            result = client.fetch_tc_sentiment_timeseries("EQ-0C00000ADA")
            
            assert result is not None
            assert "dates" in result
            assert "sentiment" in result


class TestBloggerArticleDistribution:
    """Tests for build_blogger_article_distribution method"""
    
    def test_build_blogger_article_distribution_success(self):
        """Test building blogger article distribution from TipRanks data"""
        builder = ResponseBuilder()
        
        raw_data = {
            "bloggerArticleDistribution": [
                {"sentiment": "bullish", "count": 15},
                {"sentiment": "neutral", "count": 10},
                {"sentiment": "bearish", "count": 5}
            ]
        }
        
        result = builder.build_blogger_article_distribution(raw_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["total_articles"] == 30
        assert result["bullish_count"] == 15
        assert result["neutral_count"] == 10
        assert result["bearish_count"] == 5
        assert result["bullish_percentage"] == 50.0
    
    def test_build_blogger_article_distribution_empty(self):
        """Test blogger article distribution with empty data"""
        builder = ResponseBuilder()
        
        result = builder.build_blogger_article_distribution({}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["total_articles"] == 0
        assert result["bullish_count"] == 0


class TestStockDataServiceUpdates:
    """Tests for updated stock data service methods"""
    
    @patch('app.services.stock_data_service.APIClient')
    @patch('app.services.stock_data_service.settings')
    def test_get_article_sentiment_uses_trading_central(self, mock_settings, mock_api_client):
        """Test get_article_sentiment uses Trading Central API"""
        mock_settings.ticker_list = ["AAPL"]
        mock_settings.TICKER_CONFIGS = {
            "AAPL": {"tr_v4_id": "EQ-0C00000ADA", "exchange": "NASDAQ"}
        }
        
        mock_client_instance = Mock()
        mock_client_instance.fetch_tc_article_sentiment_full.return_value = {
            'sentiment': [{"sentiment": {"id": 1, "label": "positive"}}],
            'subjectivity': [{"subjectivity": {"id": 2, "label": "subjective"}}],
            'confidence': [{"confidence": {"id": 3, "name": "high"}}]
        }
        mock_api_client.return_value = mock_client_instance
        
        service = StockDataService()
        service.api_client = mock_client_instance
        
        result = service.get_article_sentiment("AAPL")
        
        # Verify Trading Central API was called
        mock_client_instance.fetch_tc_article_sentiment_full.assert_called_once()
    
    @patch('app.services.stock_data_service.APIClient')
    @patch('app.services.stock_data_service.settings')
    def test_get_quantamental_timeseries_with_date_range(self, mock_settings, mock_api_client):
        """Test get_quantamental_timeseries uses timeseries endpoint"""
        mock_settings.ticker_list = ["AAPL"]
        mock_settings.TICKER_CONFIGS = {
            "AAPL": {"tr_v4_id": "EQ-0C00000ADA", "exchange": "NASDAQ"}
        }
        mock_settings.HISTORICAL_DAYS = 365
        
        mock_client_instance = Mock()
        mock_client_instance.fetch_tc_quantamental_timeseries.return_value = {
            "timestamps": ["2024-01-01"],
            "quantamental": [75]
        }
        mock_api_client.return_value = mock_client_instance
        
        service = StockDataService()
        service.api_client = mock_client_instance
        
        result = service.get_quantamental_timeseries("AAPL")
        
        # Verify timeseries endpoint was called with date range
        mock_client_instance.fetch_tc_quantamental_timeseries.assert_called_once()
        call_args = mock_client_instance.fetch_tc_quantamental_timeseries.call_args
        assert call_args[0][0] == "AAPL:NASDAQ"  # ticker_id format
        assert 'start_date' in call_args[1]
        assert 'end_date' in call_args[1]
    
    @patch('app.services.stock_data_service.APIClient')
    @patch('app.services.stock_data_service.settings')
    def test_get_sentiment_history_uses_trading_central(self, mock_settings, mock_api_client):
        """Test get_sentiment_history uses Trading Central sentiment timeseries"""
        mock_settings.ticker_list = ["AAPL"]
        mock_settings.TICKER_CONFIGS = {
            "AAPL": {"tr_v4_id": "EQ-0C00000ADA", "exchange": "NASDAQ"}
        }
        
        mock_client_instance = Mock()
        mock_client_instance.fetch_tc_sentiment_timeseries.return_value = {
            "dates": ["2024-01-01"],
            "sentiment": [0.75]
        }
        mock_api_client.return_value = mock_client_instance
        
        service = StockDataService()
        service.api_client = mock_client_instance
        
        result = service.get_sentiment_history("AAPL")
        
        # Verify Trading Central sentiment timeseries was called
        mock_client_instance.fetch_tc_sentiment_timeseries.assert_called_once()
        assert "dates" in result
        assert "sentiment_score" in result
    
    @patch('app.services.stock_data_service.APIClient')
    @patch('app.services.stock_data_service.settings')
    def test_get_article_distribution_uses_trading_central(self, mock_settings, mock_api_client):
        """Test get_article_distribution uses Trading Central article analytics"""
        mock_settings.ticker_list = ["AAPL"]
        mock_settings.TICKER_CONFIGS = {
            "AAPL": {"tr_v4_id": "EQ-0C00000ADA", "exchange": "NASDAQ"}
        }
        
        mock_client_instance = Mock()
        mock_client_instance.fetch_tc_article_analytics.return_value = {
            "topics": [{"news": 10, "social": 20, "web": 5, "total": 35}]
        }
        mock_api_client.return_value = mock_client_instance
        
        service = StockDataService()
        service.api_client = mock_client_instance
        
        result = service.get_article_distribution("AAPL")
        
        # Verify Trading Central article analytics was called
        mock_client_instance.fetch_tc_article_analytics.assert_called_once()
    
    @patch('app.services.stock_data_service.APIClient')
    @patch('app.services.stock_data_service.settings')
    def test_get_article_topics_uses_trading_central(self, mock_settings, mock_api_client):
        """Test get_article_topics uses Trading Central article analytics"""
        mock_settings.ticker_list = ["AAPL"]
        mock_settings.TICKER_CONFIGS = {
            "AAPL": {"tr_v4_id": "EQ-0C00000ADA", "exchange": "NASDAQ"}
        }
        
        mock_client_instance = Mock()
        mock_client_instance.fetch_tc_article_analytics.return_value = {
            "topics": [{"name": "Topic A", "count": 10}]
        }
        mock_api_client.return_value = mock_client_instance
        
        service = StockDataService()
        service.api_client = mock_client_instance
        
        result = service.get_article_topics("AAPL")
        
        # Verify Trading Central article analytics was called
        mock_client_instance.fetch_tc_article_analytics.assert_called_once()
    
    @patch('app.services.stock_data_service.APIClient')
    @patch('app.services.stock_data_service.settings')
    def test_get_blogger_article_distribution_uses_correct_builder(self, mock_settings, mock_api_client):
        """Test get_blogger_article_distribution uses build_blogger_article_distribution"""
        mock_settings.ticker_list = ["AAPL"]
        
        mock_client_instance = Mock()
        mock_client_instance.fetch_tipranks_bloggers.return_value = {
            "bloggerArticleDistribution": [
                {"sentiment": "bullish", "count": 15}
            ]
        }
        mock_api_client.return_value = mock_client_instance
        
        service = StockDataService()
        service.api_client = mock_client_instance
        
        # Mock the response builder
        with patch.object(service.response_builder, 'build_blogger_article_distribution') as mock_builder:
            mock_builder.return_value = {"ticker": "AAPL", "total_articles": 15}
            
            result = service.get_blogger_article_distribution("AAPL")
            
            # Verify the correct builder was called
            mock_builder.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
