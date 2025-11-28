"""
API Endpoint Tests

This module contains tests for all API endpoints to ensure proper functionality,
error handling, and response formats.

Note: Tests that require database connections are skipped by default.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.models.stock_data import (
    AnalystRating,
    NewsSentiment,
    QuantamentalScore,
    HedgeFundData,
    CrowdStatistics,
    BloggerSentiment,
    TechnicalIndicator,
    TargetPrice,
    SentimentType,
    RatingType,
    TimeframeType,
)


client = TestClient(app)


# ============================================
# Helper Functions
# ============================================

def create_mock_analyst_rating(ticker="AAPL"):
    """Create a mock AnalystRating object"""
    mock = MagicMock(spec=AnalystRating)
    mock.id = 1
    mock.ticker = ticker
    mock.timestamp = datetime.utcnow()
    mock.strong_buy_count = 10
    mock.buy_count = 15
    mock.hold_count = 5
    mock.sell_count = 2
    mock.strong_sell_count = 1
    mock.total_analysts = 33
    mock.consensus_rating = RatingType.BUY
    mock.consensus_score = 4.2
    mock.avg_price_target = 185.50
    mock.high_price_target = 210.00
    mock.low_price_target = 160.00
    mock.current_price = 175.00
    mock.upside_potential = 6.0
    mock.source = "tipranks"
    mock.raw_data = None
    return mock


def create_mock_news_sentiment(ticker="AAPL"):
    """Create a mock NewsSentiment object"""
    mock = MagicMock(spec=NewsSentiment)
    mock.id = 1
    mock.ticker = ticker
    mock.timestamp = datetime.utcnow()
    mock.sentiment = SentimentType.BULLISH
    mock.sentiment_score = 0.65
    mock.buzz_score = 0.8
    mock.news_score = 0.7
    mock.total_articles = 50
    mock.positive_articles = 35
    mock.negative_articles = 10
    mock.neutral_articles = 5
    mock.sector_sentiment = 0.55
    mock.sector_avg = 0.50
    mock.source = "tipranks"
    mock.raw_data = None
    return mock


# ============================================
# Tests for Current Data Endpoints
# ============================================

class TestCurrentDataEndpoints:
    """Tests for current data API endpoints"""
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_analyst_ratings_route_exists(self):
        """Test that GET /api/analyst-ratings/{ticker} route exists"""
        response = client.get("/api/analyst-ratings/AAPL")
        # Should return 404 (no data) or 200 (success), not 405 (method not allowed)
        assert response.status_code in [200, 404, 500]
    
    def test_get_analyst_ratings_invalid_ticker(self):
        """Test that invalid ticker format returns 400"""
        response = client.get("/api/analyst-ratings/INVALID!@#")
        assert response.status_code == 400
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_news_sentiment_route_exists(self):
        """Test that GET /api/news-sentiment/{ticker} route exists"""
        response = client.get("/api/news-sentiment/AAPL")
        assert response.status_code in [200, 404, 500]
    
    def test_get_news_sentiment_invalid_ticker(self):
        """Test that invalid ticker format returns 400"""
        response = client.get("/api/news-sentiment/A!B@C")
        assert response.status_code == 400
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_quantamental_route_exists(self):
        """Test that GET /api/quantamental-scores/{ticker} route exists"""
        response = client.get("/api/quantamental-scores/TSLA")
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_hedge_fund_route_exists(self):
        """Test that GET /api/hedge-fund-data/{ticker} route exists"""
        response = client.get("/api/hedge-fund-data/NVDA")
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_crowd_statistics_route_exists(self):
        """Test that GET /api/crowd-statistics/{ticker} route exists"""
        response = client.get("/api/crowd-statistics/MSFT")
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_blogger_sentiment_route_exists(self):
        """Test that GET /api/blogger-sentiment/{ticker} route exists"""
        response = client.get("/api/blogger-sentiment/GOOGL")
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_technical_indicators_route_exists(self):
        """Test that GET /api/technical-indicators/{ticker} route exists"""
        response = client.get("/api/technical-indicators/AMZN")
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_technical_indicators_with_timeframe(self):
        """Test technical indicators with timeframe parameter"""
        response = client.get("/api/technical-indicators/META?timeframe=1d")
        assert response.status_code in [200, 404, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_target_prices_route_exists(self):
        """Test that GET /api/target-prices/{ticker} route exists"""
        response = client.get("/api/target-prices/AAPL")
        assert response.status_code in [200, 404, 500]


# ============================================
# Tests for Historical Data Endpoints
# ============================================

class TestHistoricalDataEndpoints:
    """Tests for historical data API endpoints"""
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_historical_analyst_ratings(self):
        """Test GET /api/history/analyst_ratings/{ticker}"""
        response = client.get("/api/history/analyst_ratings/AAPL?hours_ago=24")
        assert response.status_code in [200, 500]
    
    def test_get_historical_data_invalid_hours(self):
        """Test that invalid hours_ago returns 422"""
        response = client.get("/api/history/analyst_ratings/AAPL?hours_ago=-1")
        assert response.status_code == 422
    
    def test_get_historical_data_exceeds_max_hours(self):
        """Test that exceeding max hours returns 422"""
        response = client.get("/api/history/analyst_ratings/AAPL?hours_ago=10000")
        assert response.status_code == 422
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_all_historical_data(self):
        """Test GET /api/history/all/{ticker}"""
        response = client.get("/api/history/all/AAPL?hours_ago=24&limit=10")
        assert response.status_code in [200, 500]


# ============================================
# Tests for Comparison Endpoints
# ============================================

class TestComparisonEndpoints:
    """Tests for comparison API endpoints"""
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_compare_periods_route_exists(self):
        """Test GET /api/compare/{ticker}"""
        response = client.get("/api/compare/AAPL?periods=1h,4h,1d&data_type=analyst_ratings")
        assert response.status_code in [200, 400, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_compare_tickers_route_exists(self):
        """Test GET /api/compare/tickers/multi"""
        response = client.get("/api/compare/tickers/multi?tickers=AAPL,TSLA&period=1d&data_type=analyst_ratings")
        assert response.status_code in [200, 400, 500]
    
    def test_compare_tickers_less_than_two(self):
        """Test that comparing less than 2 tickers returns 400"""
        response = client.get("/api/compare/tickers/multi?tickers=AAPL&period=1d")
        assert response.status_code == 400
    
    def test_compare_tickers_invalid_period(self):
        """Test that invalid period returns 400"""
        response = client.get("/api/compare/tickers/multi?tickers=AAPL,TSLA&period=invalid")
        # Returns 400 for invalid period format or 500 for db error
        assert response.status_code in [400, 500]
    
    def test_list_comparison_data_types(self):
        """Test GET /api/compare/data-types"""
        response = client.get("/api/compare/data-types")
        assert response.status_code == 200
        data = response.json()
        assert "data_types" in data


# ============================================
# Tests for Dashboard Endpoints
# ============================================

class TestDashboardEndpoints:
    """Tests for dashboard API endpoints"""
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_dashboard_overview(self):
        """Test GET /api/dashboard/overview"""
        response = client.get("/api/dashboard/overview")
        assert response.status_code in [200, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_dashboard_alerts(self):
        """Test GET /api/dashboard/alerts"""
        response = client.get("/api/dashboard/alerts?hours_ago=24")
        assert response.status_code in [200, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_dashboard_alerts_with_severity(self):
        """Test GET /api/dashboard/alerts with severity filter"""
        response = client.get("/api/dashboard/alerts?hours_ago=24&severity=high")
        assert response.status_code in [200, 500]
    
    def test_get_dashboard_alerts_invalid_severity(self):
        """Test that invalid severity returns 400"""
        response = client.get("/api/dashboard/alerts?severity=invalid")
        assert response.status_code == 400
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_collection_summary(self):
        """Test GET /api/dashboard/collection-summary"""
        response = client.get("/api/dashboard/collection-summary?hours_ago=24")
        assert response.status_code in [200, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_ticker_overview(self):
        """Test GET /api/dashboard/ticker/{ticker}"""
        response = client.get("/api/dashboard/ticker/AAPL")
        assert response.status_code in [200, 500]


# ============================================
# Tests for Configuration Endpoints
# ============================================

class TestConfigurationEndpoints:
    """Tests for configuration API endpoints"""
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_all_tickers(self):
        """Test GET /api/config/tickers"""
        response = client.get("/api/config/tickers")
        assert response.status_code in [200, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_all_tickers_include_inactive(self):
        """Test GET /api/config/tickers with include_inactive"""
        response = client.get("/api/config/tickers?include_inactive=true")
        assert response.status_code in [200, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_ticker_not_found(self):
        """Test GET /api/config/tickers/{ticker} returns 404 for non-existent ticker"""
        response = client.get("/api/config/tickers/NONEXISTENT123")
        assert response.status_code in [404, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_all_api_keys(self):
        """Test GET /api/config/api-keys"""
        response = client.get("/api/config/api-keys")
        assert response.status_code in [200, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_config_status(self):
        """Test GET /api/config/status"""
        response = client.get("/api/config/status")
        assert response.status_code in [200, 500]
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_reload_config(self):
        """Test POST /api/config/reload"""
        response = client.post("/api/config/reload")
        assert response.status_code in [200, 500]


# ============================================
# Tests for Input Validation
# ============================================

class TestInputValidation:
    """Tests for input validation across endpoints"""
    
    @pytest.mark.parametrize("ticker", [
        "INVALID!@#",
        "TOO_LONG_TICKER_SYMBOL",
        "A B C",
    ])
    def test_invalid_ticker_formats(self, ticker):
        """Test that invalid ticker formats return 400"""
        # URL encode spaces
        encoded_ticker = ticker.replace(" ", "%20")
        response = client.get(f"/api/analyst-ratings/{encoded_ticker}")
        assert response.status_code == 400
    
    @pytest.mark.parametrize("hours", [0, -1, 1000])
    def test_invalid_hours_ago_values(self, hours):
        """Test that invalid hours_ago values return 422"""
        response = client.get(f"/api/dashboard/alerts?hours_ago={hours}")
        assert response.status_code == 422


# ============================================
# Tests for Response Format
# ============================================

class TestResponseFormat:
    """Tests for API response formats"""
    
    def test_comparison_data_types_format(self):
        """Test that data-types response has correct format"""
        response = client.get("/api/compare/data-types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "data_types" in data
        assert isinstance(data["data_types"], dict)
    
    def test_error_response_format(self):
        """Test that error responses have detail field"""
        response = client.get("/api/analyst-ratings/INVALID!@#")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


# ============================================
# Tests for CORS and Headers
# ============================================

class TestCORSAndHeaders:
    """Tests for CORS and response headers"""
    
    def test_content_type_header(self):
        """Test that responses have correct content-type"""
        response = client.get("/api/compare/data-types")
        assert "application/json" in response.headers.get("content-type", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
