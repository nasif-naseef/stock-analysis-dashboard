"""
Tests for PR 2/4: Data Extraction Fixes for Blogger Sentiment and Crowd Statistics

This module tests the fixed data extraction logic for:
1. Blogger sentiment string-to-number conversion
2. Crowd statistics bullish/bearish percentage derivation
3. Neutral percentage calculation
"""
import pytest
from app.utils.data_processor import ResponseBuilder
from app.utils.response_builders import ResponseBuilder as StaticResponseBuilder


class TestBloggerSentimentDataExtraction:
    """Tests for blogger sentiment data extraction with string-to-number conversion"""
    
    def test_blogger_sentiment_string_percentage_conversion(self):
        """Test conversion of string percentages to floats"""
        raw_data = {
            'bloggerSentiment': {
                'bearish': '19',
                'bullish': '64',
                'neutral': '17',
                'bearishCount': 12,
                'bullishCount': 43,
                'neutralCount': 12,
                'score': 1,
                'avg': 0.7
            }
        }
        
        builder = ResponseBuilder()
        result = builder.build_blogger_sentiment(raw_data, 'AAPL')
        
        # Verify string to float conversion
        assert result['bullish_percent'] == 64.0, "Should convert string '64' to float 64.0"
        assert result['bearish_percent'] == 19.0, "Should convert string '19' to float 19.0"
        assert result['neutral_percent'] == 17.0, "Should convert string '17' to float 17.0"
        
        # Verify counts are preserved
        assert result['bullish_count'] == 43
        assert result['bearish_count'] == 12
        assert result['neutral_count'] == 12
        
        # Verify score and avg
        assert result['score'] == 1
        assert result['avg'] == 0.7
    
    def test_blogger_sentiment_numeric_percentages(self):
        """Test handling of numeric percentages (not strings)"""
        raw_data = {
            'bloggerSentiment': {
                'bearish': 25,
                'bullish': 70,
                'neutral': 5,
                'bearishCount': 15,
                'bullishCount': 50,
                'neutralCount': 5,
                'score': 1,
                'avg': 0.8
            }
        }
        
        builder = ResponseBuilder()
        result = builder.build_blogger_sentiment(raw_data, 'AAPL')
        
        # Verify numeric values are still converted to floats
        assert result['bullish_percent'] == 70.0
        assert result['bearish_percent'] == 25.0
        assert result['neutral_percent'] == 5.0
    
    def test_blogger_sentiment_neutral_calculation(self):
        """Test neutral percentage calculation when not provided"""
        raw_data = {
            'bloggerSentiment': {
                'bearish': '19',
                'bullish': '64',
                # neutral is missing
                'bearishCount': 12,
                'bullishCount': 43,
                'neutralCount': 12,
                'score': 1,
                'avg': 0.7
            }
        }
        
        builder = ResponseBuilder()
        result = builder.build_blogger_sentiment(raw_data, 'AAPL')
        
        # Should calculate neutral as 100 - 64 - 19 = 17
        assert result['neutral_percent'] == 17.0, "Should calculate neutral as 100 - bullish - bearish"
    
    def test_blogger_sentiment_missing_data(self):
        """Test handling of missing or None values"""
        raw_data = {
            'bloggerSentiment': {
                'bearishCount': 0,
                'bullishCount': 0,
                'neutralCount': 0,
            }
        }
        
        builder = ResponseBuilder()
        result = builder.build_blogger_sentiment(raw_data, 'AAPL')
        
        # Should handle missing percentages gracefully
        assert result['bullish_percent'] is None
        assert result['bearish_percent'] is None
        assert result['neutral_percent'] is None
    
    def test_blogger_sentiment_static_builder(self):
        """Test static ResponseBuilder produces same results"""
        raw_data = {
            'bloggerSentiment': {
                'bearish': '19',
                'bullish': '64',
                'neutral': '17',
                'bearishCount': 12,
                'bullishCount': 43,
                'neutralCount': 12,
                'score': 1,
                'avg': 0.7
            }
        }
        
        result = StaticResponseBuilder.build_blogger_sentiment(raw_data, 'AAPL')
        
        # Verify string to float conversion
        assert result['bullish_percent'] == 64.0
        assert result['bearish_percent'] == 19.0
        assert result['neutral_percent'] == 17.0


class TestCrowdStatisticsDataExtraction:
    """Tests for crowd statistics with derived bullish/bearish percentages"""
    
    def test_crowd_stats_bullish_bearish_derivation(self):
        """Test derivation of bullish/bearish percentages from score"""
        raw_data = {
            'generalStatsAll': {
                'portfoliosHolding': 95692,
                'amountOfPortfolios': 831432,
                'percentAllocated': 0.12,
                'score': 0.43,
                'individualSectorAverage': 0.41
            }
        }
        
        builder = ResponseBuilder()
        result = builder.build_crowd_stats(raw_data, 'AAPL', 'all')
        
        # Score of 0.43 should give:
        # bullish_percent = 43.0 (score * 100)
        # bearish_percent = 57.0 ((1 - score) * 100)
        assert result['bullish_percent'] == 43.0, "Should derive bullish from score"
        assert abs(result['bearish_percent'] - 57.0) < 0.01, "Should derive bearish from 1-score"
        assert result['neutral_percent'] == 0, "TipRanks crowd doesn't have neutral"
        
        # Verify sentiment_score is set
        assert result['sentiment_score'] == 0.43
        
        # Verify crowd sentiment is determined correctly
        # score 0.43 < sector_avg 0.41 + 0.1, so should be neutral or bearish
        assert result['crowd_sentiment'] in ['neutral', 'bearish']
    
    def test_crowd_stats_bullish_sentiment(self):
        """Test bullish sentiment determination"""
        raw_data = {
            'generalStatsAll': {
                'portfoliosHolding': 100000,
                'score': 0.65,
                'individualSectorAverage': 0.50
            }
        }
        
        builder = ResponseBuilder()
        result = builder.build_crowd_stats(raw_data, 'TSLA', 'all')
        
        # Score of 0.65 should give:
        # bullish_percent = 65.0
        # bearish_percent = 35.0
        assert result['bullish_percent'] == 65.0
        assert result['bearish_percent'] == 35.0
        
        # score 0.65 > sector_avg 0.50 + 0.1, so should be bullish
        assert result['crowd_sentiment'] == 'bullish'
    
    def test_crowd_stats_bearish_sentiment(self):
        """Test bearish sentiment determination"""
        raw_data = {
            'generalStatsAll': {
                'portfoliosHolding': 50000,
                'score': 0.30,
                'individualSectorAverage': 0.45
            }
        }
        
        builder = ResponseBuilder()
        result = builder.build_crowd_stats(raw_data, 'NFLX', 'all')
        
        # Score of 0.30 should give:
        # bullish_percent = 30.0
        # bearish_percent = 70.0
        assert result['bullish_percent'] == 30.0
        assert result['bearish_percent'] == 70.0
        
        # score 0.30 < sector_avg 0.45 - 0.1, so should be bearish
        assert result['crowd_sentiment'] == 'bearish'
    
    def test_crowd_stats_no_sector_average(self):
        """Test sentiment determination without sector average"""
        raw_data = {
            'generalStatsAll': {
                'portfoliosHolding': 75000,
                'score': 0.60
            }
        }
        
        builder = ResponseBuilder()
        result = builder.build_crowd_stats(raw_data, 'AMZN', 'all')
        
        # Without sector avg, use absolute thresholds
        # score 0.60 > 0.55, so should be bullish
        assert result['crowd_sentiment'] == 'bullish'
    
    def test_crowd_stats_mentions_count(self):
        """Test mentions_count is populated from portfoliosHolding"""
        raw_data = {
            'generalStatsAll': {
                'portfoliosHolding': 95692,
                'score': 0.50
            }
        }
        
        builder = ResponseBuilder()
        result = builder.build_crowd_stats(raw_data, 'AAPL', 'all')
        
        # mentions_count should be set to portfoliosHolding
        assert result['mentions_count'] == 95692
        assert result['portfolio_holding'] == 95692
    
    def test_crowd_stats_missing_score(self):
        """Test handling when score is missing"""
        raw_data = {
            'generalStatsAll': {
                'portfoliosHolding': 10000,
            }
        }
        
        builder = ResponseBuilder()
        result = builder.build_crowd_stats(raw_data, 'GOOGL', 'all')
        
        # Should handle missing score gracefully
        assert result['bullish_percent'] is None
        assert result['bearish_percent'] is None
        assert result['crowd_sentiment'] is None
    
    def test_crowd_stats_static_builder(self):
        """Test static ResponseBuilder produces same results"""
        raw_data = {
            'generalStatsAll': {
                'portfoliosHolding': 95692,
                'score': 0.43,
                'individualSectorAverage': 0.41
            }
        }
        
        result = StaticResponseBuilder.build_crowd_stats(raw_data, 'AAPL', 'all')
        
        # Verify derived percentages
        assert result['bullish_percent'] == 43.0
        assert abs(result['bearish_percent'] - 57.0) < 0.01


class TestHelperFunctions:
    """Tests for helper functions"""
    
    def test_safe_parse_number_with_string(self):
        """Test safe_parse_number with string input"""
        assert ResponseBuilder.safe_parse_number('64') == 64.0
        assert ResponseBuilder.safe_parse_number('19.5') == 19.5
    
    def test_safe_parse_number_with_number(self):
        """Test safe_parse_number with numeric input"""
        assert ResponseBuilder.safe_parse_number(64) == 64.0
        assert ResponseBuilder.safe_parse_number(19.5) == 19.5
    
    def test_safe_parse_number_with_none(self):
        """Test safe_parse_number with None input"""
        assert ResponseBuilder.safe_parse_number(None) is None
        assert ResponseBuilder.safe_parse_number(None, 0.0) == 0.0
    
    def test_safe_parse_number_with_invalid_string(self):
        """Test safe_parse_number with invalid string"""
        assert ResponseBuilder.safe_parse_number('invalid') is None
        assert ResponseBuilder.safe_parse_number('invalid', 0.0) == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
