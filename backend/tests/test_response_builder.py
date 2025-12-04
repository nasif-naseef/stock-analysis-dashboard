"""
Comprehensive Unit Tests for ResponseBuilder Methods

This module contains comprehensive tests for the 7 critical ResponseBuilder methods:
1. build_article_distribution()
2. build_article_sentiment()
3. build_support_resistance()
4. build_stop_loss()
5. build_chart_events_dataframe()
6. build_technical_summaries_dataframe()
7. build_quantamental_timeseries_dataframe()

Each method is tested with:
- Valid input data (happy path)
- Empty/None input data (edge cases)
- Malformed input data (error handling)
"""
import pytest
import pandas as pd
from typing import Dict, Any
from app.utils.data_processor import ResponseBuilder


# ============================================
# Pytest Fixtures for Reusable Test Data
# ============================================

@pytest.fixture
def response_builder():
    """Create a ResponseBuilder instance for testing"""
    return ResponseBuilder()


@pytest.fixture
def valid_article_distribution_data():
    """Valid article distribution data with topics containing news, social, web columns"""
    return {
        "topics": [
            {"name": "Topic A", "news": 10, "social": 20, "web": 5, "total": 35},
            {"name": "Topic B", "news": 15, "social": 25, "web": 10, "total": 50},
            {"name": "Topic C", "news": 5, "social": 10, "web": 3, "total": 18},
        ]
    }


@pytest.fixture
def valid_article_sentiment_data():
    """Valid article sentiment data with nested arrays"""
    return {
        "sentiment": [{"sentiment": {"id": 1, "label": "positive", "value": 75}}],
        "subjectivity": [{"subjectivity": {"id": 2, "label": "subjective", "value": 60}}],
        "confidence": [{"confidence": {"id": 3, "name": "high"}}]
    }


@pytest.fixture
def valid_support_resistance_data():
    """Valid support/resistance data with prefixed keys"""
    return {
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


@pytest.fixture
def valid_stop_loss_data():
    """Valid stop loss data with stops and timestamps arrays"""
    return {
        "stops": [100.0, 95.0, 90.0, 85.0],
        "timestamps": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
    }


@pytest.fixture
def valid_chart_events_data():
    """Valid chart events data with events key"""
    return {
        "events": [
            {
                "id": 1,
                "type": "breakout",
                "price": 150.0,
                "dates": {"start": "2024-01-01", "end": "2024-01-02"},
                "endPrices": {"start": 145.0, "end": 155.0},
                "eventType": {"id": 1, "name": "breakout"},
                "targetPrice": {"value": 160.0}
            },
            {
                "id": 2,
                "type": "breakdown",
                "price": 145.0,
                "dates": {"start": "2024-01-03", "end": "2024-01-04"},
                "endPrices": {"start": 150.0, "end": 140.0},
                "eventType": {"id": 2, "name": "breakdown"},
                "targetPrice": {"value": 135.0}
            }
        ]
    }


@pytest.fixture
def valid_technical_summaries_data():
    """Valid technical summaries data with scores containing multiple instruments"""
    return {
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
                "intradayIntermediate": {"score": 6.5, "signal": "hold"},
                "intradayLong": {"score": 8.0, "signal": "strong_buy"},
                "intradayShort": {"score": 5.0, "signal": "sell"},
                "long": {"score": 8.5, "signal": "strong_buy"},
                "short": {"score": 4.5, "signal": "strong_sell"}
            },
            {
                "instrument": {
                    "symbol": "TSLA",
                    "name": "Tesla Inc",
                    "exchange": "NASDAQ",
                    "isin": "US88160R1014",
                    "instrumentId": "456"
                },
                "intermediate": {"score": 6.0, "signal": "hold"},
                "intradayIntermediate": {"score": 5.5, "signal": "hold"},
                "intradayLong": {"score": 7.0, "signal": "buy"},
                "intradayShort": {"score": 4.0, "signal": "sell"},
                "long": {"score": 7.5, "signal": "buy"},
                "short": {"score": 5.5, "signal": "hold"}
            }
        ]
    }


@pytest.fixture
def valid_quantamental_timeseries_data():
    """Valid quantamental timeseries data with all score columns"""
    return {
        "timestamps": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "quantamental": [75, 78, 80],
        "growth": [70, 72, 74],
        "income": [65, 67, 68],
        "momentum": [80, 82, 85],
        "quality": [90, 91, 92],
        "valuation": [60, 62, 64]
    }


# ============================================
# Tests for build_article_distribution()
# ============================================

class TestBuildArticleDistribution:
    """Test build_article_distribution() method"""
    
    def test_valid_data_happy_path(self, response_builder, valid_article_distribution_data):
        """Test with valid data - happy path"""
        result = response_builder.build_article_distribution(valid_article_distribution_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["news_count"] == 30  # 10 + 15 + 5
        assert result["social_count"] == 55  # 20 + 25 + 10
        assert result["web_count"] == 18  # 5 + 10 + 3
        assert result["total_articles"] == 103  # 35 + 50 + 18
        
        # Check percentages
        assert result["news_percentage"] == pytest.approx((30 / 103) * 100, rel=1e-2)
        assert result["social_percentage"] == pytest.approx((55 / 103) * 100, rel=1e-2)
        assert result["web_percentage"] == pytest.approx((18 / 103) * 100, rel=1e-2)
    
    def test_empty_topics_array(self, response_builder):
        """Test with empty topics array - edge case"""
        result = response_builder.build_article_distribution({"topics": []}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["total_articles"] == 0
        assert result["news_count"] == 0
        assert result["social_count"] == 0
        assert result["web_count"] == 0
        assert result["news_percentage"] == 0
        assert result["social_percentage"] == 0
        assert result["web_percentage"] == 0
    
    def test_missing_topics_key(self, response_builder):
        """Test with missing topics key - edge case"""
        result = response_builder.build_article_distribution({}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["total_articles"] == 0
        assert result["news_count"] == 0
    
    def test_none_input_data(self, response_builder):
        """Test with None input data - edge case (should raise exception)"""
        with pytest.raises(AttributeError):
            response_builder.build_article_distribution(None, "TEST")
    
    def test_topics_missing_columns(self, response_builder):
        """Test with topics missing some columns - malformed data"""
        malformed_data = {
            "topics": [
                {"name": "Topic A", "news": 10},  # Missing social, web, total
                {"name": "Topic B", "social": 20}  # Missing news, web, total
            ]
        }
        result = response_builder.build_article_distribution(malformed_data, "TEST")
        
        assert result["ticker"] == "TEST"
        # Should handle missing columns gracefully
        assert result["news_count"] == 10
        assert result["social_count"] == 20
        assert result["web_count"] == 0
    
    def test_topics_with_string_values(self, response_builder):
        """Test with string values instead of numbers - malformed data"""
        malformed_data = {
            "topics": [
                {"name": "Topic A", "news": "10", "social": "20", "web": "5", "total": "35"}
            ]
        }
        result = response_builder.build_article_distribution(malformed_data, "TEST")
        
        # Pandas should handle string to int conversion or result in 0
        assert result["ticker"] == "TEST"
        assert isinstance(result["total_articles"], (int, float))


# ============================================
# Tests for build_article_sentiment()
# ============================================

class TestBuildArticleSentiment:
    """Test build_article_sentiment() method"""
    
    def test_valid_data_happy_path(self, response_builder, valid_article_sentiment_data):
        """Test with valid data - happy path"""
        result = response_builder.build_article_sentiment(valid_article_sentiment_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["sentiment_id"] == 1
        assert result["sentiment_label"] == "positive"
        assert result["sentiment_value"] == 75
        assert result["subjectivity_id"] == 2
        assert result["subjectivity_label"] == "subjective"
        assert result["subjectivity_value"] == 60
        assert result["confidence_id"] == 3
        assert result["confidence_name"] == "high"
    
    def test_empty_sentiment_arrays(self, response_builder):
        """Test with empty sentiment arrays - edge case"""
        empty_data = {
            "sentiment": [],
            "subjectivity": [],
            "confidence": []
        }
        result = response_builder.build_article_sentiment(empty_data, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["sentiment_id"] is None
        assert result["sentiment_label"] is None
        assert result["sentiment_value"] is None
        assert result["subjectivity_id"] is None
        assert result["confidence_id"] is None
    
    def test_missing_keys(self, response_builder):
        """Test with missing sentiment/subjectivity/confidence keys - edge case"""
        result = response_builder.build_article_sentiment({}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["sentiment_id"] is None
        assert result["subjectivity_id"] is None
        assert result["confidence_id"] is None
    
    def test_none_input_data(self, response_builder):
        """Test with None input data - edge case (should raise exception)"""
        with pytest.raises(AttributeError):
            response_builder.build_article_sentiment(None, "TEST")
    
    def test_partial_data_sentiment_only(self, response_builder):
        """Test with only sentiment data present - partial data"""
        partial_data = {
            "sentiment": [{"sentiment": {"id": 1, "label": "positive", "value": 75}}]
        }
        result = response_builder.build_article_sentiment(partial_data, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["sentiment_id"] == 1
        assert result["sentiment_label"] == "positive"
        assert result["sentiment_value"] == 75
        assert result["subjectivity_id"] is None
        assert result["confidence_id"] is None
    
    def test_malformed_nested_structure(self, response_builder):
        """Test with malformed nested structure - malformed data"""
        malformed_data = {
            "sentiment": [{"wrong_key": {"id": 1}}],  # Wrong nested key
            "subjectivity": [{}],  # Empty dict
            "confidence": None  # None instead of list
        }
        result = response_builder.build_article_sentiment(malformed_data, "TEST")
        
        assert result["ticker"] == "TEST"
        # Should handle gracefully with None values
        assert result["sentiment_id"] is None
        assert result["subjectivity_id"] is None
        assert result["confidence_id"] is None
    
    def test_empty_nested_dicts(self, response_builder):
        """Test with empty nested dictionaries - malformed data"""
        malformed_data = {
            "sentiment": [{"sentiment": {}}],
            "subjectivity": [{"subjectivity": {}}],
            "confidence": [{"confidence": {}}]
        }
        result = response_builder.build_article_sentiment(malformed_data, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["sentiment_id"] is None
        assert result["subjectivity_id"] is None
        assert result["confidence_id"] is None


# ============================================
# Tests for build_support_resistance()
# ============================================

class TestBuildSupportResistance:
    """Test build_support_resistance() method"""
    
    def test_valid_data_happy_path(self, response_builder, valid_support_resistance_data):
        """Test with valid data - happy path"""
        result = response_builder.build_support_resistance(valid_support_resistance_data)
        
        assert result["symbol"] == "AAPL"
        assert result["date"] == "2024-01-15"
        assert result["exchange"] == "NASDAQ"
        
        # Check support levels
        assert result["support_10"] == 150.5
        assert result["support_20"] == 148.0
        assert result["support_40"] == 145.0
        assert result["support_100"] == 140.0
        assert result["support_250"] == 135.0
        assert result["support_500"] == 130.0
        
        # Check resistance levels
        assert result["resistance_10"] == 155.5
        assert result["resistance_20"] == 158.0
        assert result["resistance_40"] == 160.0
        assert result["resistance_100"] == 165.0
        assert result["resistance_250"] == 170.0
        assert result["resistance_500"] == 175.0
    
    def test_empty_data(self, response_builder):
        """Test with empty dictionary - edge case"""
        result = response_builder.build_support_resistance({})
        
        assert result["symbol"] == "N/A"
        assert result["date"] == "N/A"
        assert result["exchange"] == "N/A"
        assert result["support_10"] is None
        assert result["resistance_10"] is None
    
    def test_none_input_data(self, response_builder):
        """Test with None input data - edge case"""
        result = response_builder.build_support_resistance(None)
        
        assert result["symbol"] == "N/A"
        assert result["date"] == "N/A"
    
    def test_missing_support_resistance_keys(self, response_builder):
        """Test with missing support/resistance keys - edge case"""
        partial_data = {
            "instrument": {"symbol": "TEST", "exchange": "NYSE"},
            "date": "2024-01-01"
        }
        result = response_builder.build_support_resistance(partial_data)
        
        assert result["symbol"] == "TEST"
        assert result["date"] == "2024-01-01"
        assert result["exchange"] == "NYSE"
        assert result["support_10"] is None
        assert result["resistance_10"] is None
    
    def test_partial_support_resistance_values(self, response_builder):
        """Test with partial support/resistance values - malformed data"""
        partial_data = {
            "instrument": {"symbol": "TEST"},
            "support": {"support10": 100.0, "support20": 95.0},  # Missing other levels
            "resistance": {"resistance10": 105.0}  # Missing other levels
        }
        result = response_builder.build_support_resistance(partial_data)
        
        assert result["symbol"] == "TEST"
        assert result["support_10"] == 100.0
        assert result["support_20"] == 95.0
        assert result["support_40"] is None
        assert result["resistance_10"] == 105.0
        assert result["resistance_20"] is None
    
    def test_string_numeric_values(self, response_builder):
        """Test with string values instead of floats - malformed data"""
        malformed_data = {
            "instrument": {"symbol": "TEST"},
            "support": {"support10": "150.5"},
            "resistance": {"resistance10": "155.5"}
        }
        result = response_builder.build_support_resistance(malformed_data)
        
        assert result["symbol"] == "TEST"
        # safe_float should handle string conversion
        assert result["support_10"] == 150.5
        assert result["resistance_10"] == 155.5


# ============================================
# Tests for build_stop_loss()
# ============================================

class TestBuildStopLoss:
    """Test build_stop_loss() method"""
    
    def test_valid_data_happy_path(self, response_builder, valid_stop_loss_data):
        """Test with valid data - happy path"""
        result = response_builder.build_stop_loss(valid_stop_loss_data, "AAPL")
        
        assert result["ticker"] == "AAPL"
        assert result["recommended_stop_price"] == 100.0  # First element
        assert result["calculation_timestamp"] == "2024-01-01"  # First element
        assert result["stop_type"] == "Volatility-Based"
        assert result["direction"] == "Below (Long Position)"
        assert result["tightness"] == "Medium"
    
    def test_uses_first_element_not_last(self, response_builder):
        """Test that first element [0] is used, not last element [-1]"""
        data = {
            "stops": [100.0, 95.0, 90.0],
            "timestamps": ["2024-01-01", "2024-01-02", "2024-01-03"]
        }
        result = response_builder.build_stop_loss(data, "AAPL")
        
        # Should use first element, not last
        assert result["recommended_stop_price"] == 100.0
        assert result["calculation_timestamp"] == "2024-01-01"
    
    def test_empty_arrays(self, response_builder):
        """Test with empty stops and timestamps arrays - edge case"""
        empty_data = {
            "stops": [],
            "timestamps": []
        }
        result = response_builder.build_stop_loss(empty_data, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["recommended_stop_price"] is None
        assert result["calculation_timestamp"] is None
    
    def test_missing_keys(self, response_builder):
        """Test with missing stops/timestamps keys - edge case"""
        result = response_builder.build_stop_loss({}, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["recommended_stop_price"] is None
        assert result["calculation_timestamp"] is None
    
    def test_none_input_data(self, response_builder):
        """Test with None input data - edge case"""
        result = response_builder.build_stop_loss(None, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["recommended_stop_price"] is None
    
    def test_list_input_extracts_first(self, response_builder):
        """Test with list input (extracts first item) - edge case"""
        list_data = [{
            "stops": [100.0, 95.0],
            "timestamps": ["2024-01-01", "2024-01-02"]
        }]
        result = response_builder.build_stop_loss(list_data, "TEST")
        
        assert result["ticker"] == "TEST"
        assert result["recommended_stop_price"] == 100.0
    
    def test_custom_stop_parameters(self, response_builder, valid_stop_loss_data):
        """Test with custom stop type, direction, and tightness"""
        result = response_builder.build_stop_loss(
            valid_stop_loss_data,
            "TEST",
            stop_type="ATR-Based",
            direction="Above (Short Position)",
            tightness="Tight"
        )
        
        assert result["stop_type"] == "ATR-Based"
        assert result["direction"] == "Above (Short Position)"
        assert result["tightness"] == "Tight"
    
    def test_single_element_arrays(self, response_builder):
        """Test with single element arrays"""
        data = {
            "stops": [100.0],
            "timestamps": ["2024-01-01"]
        }
        result = response_builder.build_stop_loss(data, "TEST")
        
        assert result["recommended_stop_price"] == 100.0
        assert result["calculation_timestamp"] == "2024-01-01"


# ============================================
# Tests for build_chart_events_dataframe()
# ============================================

class TestBuildChartEventsDataframe:
    """Test build_chart_events_dataframe() method"""
    
    def test_valid_data_happy_path(self, response_builder, valid_chart_events_data):
        """Test with valid data - happy path"""
        result = response_builder.build_chart_events_dataframe(valid_chart_events_data, "AAPL")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "ticker" in result.columns
        assert "is_active" in result.columns
        assert result["ticker"].iloc[0] == "AAPL"
        assert result["is_active"].iloc[0] == True
    
    def test_missing_events_key(self, response_builder):
        """Test with missing events key - edge case"""
        result = response_builder.build_chart_events_dataframe({}, "TEST")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_none_input_data(self, response_builder):
        """Test with None input data - edge case"""
        result = response_builder.build_chart_events_dataframe(None, "TEST")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_empty_events_array(self, response_builder):
        """Test with empty events array - edge case"""
        result = response_builder.build_chart_events_dataframe({"events": []}, "TEST")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_is_active_false(self, response_builder, valid_chart_events_data):
        """Test with is_active=False parameter"""
        result = response_builder.build_chart_events_dataframe(
            valid_chart_events_data,
            "AAPL",
            is_active=False
        )
        
        assert len(result) == 2
        assert result["is_active"].iloc[0] == False
    
    def test_nested_column_flattening(self, response_builder):
        """Test that nested columns are properly flattened"""
        data = {
            "events": [
                {
                    "id": 1,
                    "dates": {"start": "2024-01-01", "end": "2024-01-02"},
                    "endPrices": {"open": 145.0, "close": 155.0},
                    "eventType": {"id": 1, "name": "breakout"}
                }
            ]
        }
        result = response_builder.build_chart_events_dataframe(data, "TEST")
        
        assert len(result) == 1
        # Check that flattening occurred (should have date_ prefixed columns)
        assert any("date_" in col for col in result.columns) or "dates" not in result.columns
    
    def test_malformed_events_structure(self, response_builder):
        """Test with malformed events structure - malformed data"""
        malformed_data = {
            "events": [
                {"id": 1},  # Missing expected fields
                {}  # Empty event
            ]
        }
        result = response_builder.build_chart_events_dataframe(malformed_data, "TEST")
        
        # Should handle gracefully, may return empty or filtered DataFrame
        assert isinstance(result, pd.DataFrame)


# ============================================
# Tests for build_technical_summaries_dataframe()
# ============================================

class TestBuildTechnicalSummariesDataframe:
    """Test build_technical_summaries_dataframe() method"""
    
    def test_valid_data_happy_path(self, response_builder, valid_technical_summaries_data):
        """Test with valid data - happy path"""
        result = response_builder.build_technical_summaries_dataframe(valid_technical_summaries_data)
        
        assert isinstance(result, pd.DataFrame)
        # 2 instruments * 6 categories = 12 rows
        assert len(result) == 12
        
        # Check required columns
        assert "symbol" in result.columns
        assert "name" in result.columns
        assert "exchange" in result.columns
        assert "category" in result.columns
        
        # Check that all categories are present
        categories = ['intermediate', 'intradayIntermediate', 'intradayLong', 
                     'intradayShort', 'long', 'short']
        assert set(result["category"].unique()) == set(categories)
        
        # Check instrument symbols
        assert "AAPL" in result["symbol"].values
        assert "TSLA" in result["symbol"].values
    
    def test_missing_scores_key(self, response_builder):
        """Test with missing scores key - edge case"""
        result = response_builder.build_technical_summaries_dataframe({})
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_none_input_data(self, response_builder):
        """Test with None input data - edge case"""
        result = response_builder.build_technical_summaries_dataframe(None)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_empty_scores_array(self, response_builder):
        """Test with empty scores array - edge case"""
        result = response_builder.build_technical_summaries_dataframe({"scores": []})
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_single_instrument(self, response_builder):
        """Test with single instrument"""
        data = {
            "scores": [
                {
                    "instrument": {
                        "symbol": "AAPL",
                        "name": "Apple Inc",
                        "exchange": "NASDAQ"
                    },
                    "intermediate": {"score": 7.5},
                    "intradayIntermediate": {"score": 6.5},
                    "intradayLong": {"score": 8.0},
                    "intradayShort": {"score": 5.0},
                    "long": {"score": 8.5},
                    "short": {"score": 4.5}
                }
            ]
        }
        result = response_builder.build_technical_summaries_dataframe(data)
        
        assert len(result) == 6  # 6 categories for 1 instrument
        assert result["symbol"].iloc[0] == "AAPL"
    
    def test_missing_instrument_fields(self, response_builder):
        """Test with missing instrument fields - malformed data"""
        malformed_data = {
            "scores": [
                {
                    "instrument": {"symbol": "TEST"},  # Missing other fields
                    "intermediate": {"score": 7.5},
                    "intradayIntermediate": {"score": 6.5},
                    "intradayLong": {"score": 8.0},
                    "intradayShort": {"score": 5.0},
                    "long": {"score": 8.5},
                    "short": {"score": 4.5}
                }
            ]
        }
        result = response_builder.build_technical_summaries_dataframe(malformed_data)
        
        assert len(result) == 6
        assert result["symbol"].iloc[0] == "TEST"
        assert result["name"].iloc[0] == "N/A"
    
    def test_missing_category_data(self, response_builder):
        """Test with missing category data - malformed data"""
        malformed_data = {
            "scores": [
                {
                    "instrument": {"symbol": "TEST"},
                    "intermediate": {"score": 7.5},
                    # Missing other categories
                }
            ]
        }
        result = response_builder.build_technical_summaries_dataframe(malformed_data)
        
        # Should still create 6 rows, with empty dicts for missing categories
        assert len(result) == 6
        assert result["symbol"].iloc[0] == "TEST"


# ============================================
# Tests for build_quantamental_timeseries_dataframe()
# ============================================

class TestBuildQuantamentalTimeseriesDataframe:
    """Test build_quantamental_timeseries_dataframe() method"""
    
    def test_valid_data_happy_path(self, response_builder, valid_quantamental_timeseries_data):
        """Test with valid data - happy path"""
        result = response_builder.build_quantamental_timeseries_dataframe(valid_quantamental_timeseries_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        
        # Check all required columns are present
        assert "timestamp" in result.columns
        assert "quantamental_score" in result.columns
        assert "growth_score" in result.columns
        assert "income_score" in result.columns
        assert "momentum_score" in result.columns
        assert "quality_score" in result.columns
        assert "valuation_score" in result.columns
        
        # Check values
        assert result["quantamental_score"].iloc[0] == 75
        assert result["growth_score"].iloc[0] == 70
        assert result["quality_score"].iloc[2] == 92
    
    def test_list_input_extracts_first(self, response_builder, valid_quantamental_timeseries_data):
        """Test with list input (extracts first item) - edge case"""
        list_data = [valid_quantamental_timeseries_data]
        result = response_builder.build_quantamental_timeseries_dataframe(list_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "quantamental_score" in result.columns
    
    def test_empty_data(self, response_builder):
        """Test with empty dictionary - edge case"""
        result = response_builder.build_quantamental_timeseries_dataframe({})
        
        assert isinstance(result, pd.DataFrame)
        # Empty DataFrame should have columns but no rows
        assert len(result) == 0
    
    def test_none_input_data(self, response_builder):
        """Test with None input data - edge case"""
        result = response_builder.build_quantamental_timeseries_dataframe(None)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_missing_score_columns(self, response_builder):
        """Test with missing some score columns - malformed data (should raise ValueError)"""
        partial_data = {
            "timestamps": ["2024-01-01", "2024-01-02"],
            "quantamental": [75, 78],
            "growth": [70, 72]
            # Missing income, momentum, quality, valuation - will cause ValueError
        }
        with pytest.raises(ValueError):
            response_builder.build_quantamental_timeseries_dataframe(partial_data)
    
    def test_mismatched_array_lengths(self, response_builder):
        """Test with mismatched array lengths - malformed data (should raise ValueError)"""
        malformed_data = {
            "timestamps": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "quantamental": [75, 78],  # Only 2 values instead of 3
            "growth": [70, 72, 74],
            "income": [65],  # Only 1 value
            "momentum": [80, 82, 85],
            "quality": [90, 91, 92],
            "valuation": [60, 62, 64]
        }
        # Pandas DataFrame requires all arrays to be same length
        with pytest.raises(ValueError):
            response_builder.build_quantamental_timeseries_dataframe(malformed_data)
    
    def test_single_data_point(self, response_builder):
        """Test with single data point"""
        data = {
            "timestamps": ["2024-01-01"],
            "quantamental": [75],
            "growth": [70],
            "income": [65],
            "momentum": [80],
            "quality": [90],
            "valuation": [60]
        }
        result = response_builder.build_quantamental_timeseries_dataframe(data)
        
        assert len(result) == 1
        assert result["quantamental_score"].iloc[0] == 75
    
    def test_empty_arrays(self, response_builder):
        """Test with empty arrays"""
        data = {
            "timestamps": [],
            "quantamental": [],
            "growth": [],
            "income": [],
            "momentum": [],
            "quality": [],
            "valuation": []
        }
        result = response_builder.build_quantamental_timeseries_dataframe(data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        # Columns should still be present
        assert "quantamental_score" in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
