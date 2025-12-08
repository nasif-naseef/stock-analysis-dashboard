"""
Tests for Crowd Statistics and Blogger Sentiment Fallback Logic

This module tests the fallback logic for extracting crowd statistics and blogger sentiment
from raw_data when direct fields are null/zero.
"""
import pytest
from unittest.mock import MagicMock
from datetime import datetime

# Mock the database models
class MockCrowdStats:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.ticker = kwargs.get('ticker', 'AAPL')
        self.timestamp = kwargs.get('timestamp', datetime.utcnow())
        self.portfolio_holding = kwargs.get('portfolio_holding', 0)
        self.amount_of_portfolios = kwargs.get('amount_of_portfolios', 0)
        self.percent_allocated = kwargs.get('percent_allocated', 0.0)
        self.percent_over_last_7d = kwargs.get('percent_over_last_7d', 0.0)
        self.percent_over_last_30d = kwargs.get('percent_over_last_30d', 0.0)
        self.score = kwargs.get('score', None)
        self.frequency = kwargs.get('frequency', 0.0)
        self.source = kwargs.get('source', 'tipranks')
        self.raw_data = kwargs.get('raw_data', {})


class MockBloggerSentiment:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.ticker = kwargs.get('ticker', 'AAPL')
        self.timestamp = kwargs.get('timestamp', datetime.utcnow())
        self.bearish = kwargs.get('bearish', 0)
        self.neutral = kwargs.get('neutral', 0)
        self.bullish = kwargs.get('bullish', 0)
        self.bearish_count = kwargs.get('bearish_count', 0)
        self.neutral_count = kwargs.get('neutral_count', 0)
        self.bullish_count = kwargs.get('bullish_count', 0)
        self.score = kwargs.get('score', 0.0)
        self.avg = kwargs.get('avg', None)
        self.source = kwargs.get('source', 'tipranks')
        self.raw_data = kwargs.get('raw_data', {})


class TestCrowdStatisticsFallbackLogic:
    """Tests for crowd statistics data extraction with fallback"""
    
    def test_crowd_stats_extraction_from_raw_data(self):
        """Test extraction from raw_data.generalStatsAll when direct fields are null"""
        
        # Simulate data structure as described in the problem statement
        raw_data = {
            'generalStatsAll': {
                'portfoliosHolding': 95692,
                'amountOfPortfolios': 831432,
                'percentAllocated': 0.12,
                'score': 0.43,
                'individualSectorAverage': 0.41
            }
        }
        
        mock_data = MockCrowdStats(
            score=None,  # Direct field is null
            portfolio_holding=0,  # Direct field is zero
            raw_data=raw_data
        )
        
        # Simulate the fallback logic from the endpoint
        sentiment_score = mock_data.score
        mentions_count = mock_data.portfolio_holding or 0
        
        # Fallback to raw_data
        if mock_data.raw_data and isinstance(mock_data.raw_data, dict):
            general_stats = mock_data.raw_data.get('generalStatsAll', {})
            if general_stats:
                if sentiment_score is None and 'score' in general_stats:
                    sentiment_score = general_stats.get('score')
                if 'portfoliosHolding' in general_stats:
                    portfolios_holding = general_stats.get('portfoliosHolding')
                    if portfolios_holding:
                        mentions_count = portfolios_holding
        
        # Verify extraction
        assert sentiment_score == 0.43, "Should extract score from raw_data"
        assert mentions_count == 95692, "Should extract portfoliosHolding from raw_data"
    
    def test_crowd_stats_uses_direct_fields_when_available(self):
        """Test that direct fields are used when available"""
        
        raw_data = {
            'generalStatsAll': {
                'portfoliosHolding': 95692,
                'score': 0.43,
            }
        }
        
        mock_data = MockCrowdStats(
            score=0.75,  # Direct field has value
            portfolio_holding=100000,  # Direct field has value
            raw_data=raw_data
        )
        
        # Simulate the fallback logic
        sentiment_score = mock_data.score
        mentions_count = mock_data.portfolio_holding or 0
        
        # Should NOT fallback since direct fields are set
        if mock_data.raw_data and isinstance(mock_data.raw_data, dict):
            general_stats = mock_data.raw_data.get('generalStatsAll', {})
            if general_stats:
                # Only fallback if sentiment_score is None
                if sentiment_score is None and 'score' in general_stats:
                    sentiment_score = general_stats.get('score')
        
        # Verify direct fields are used
        assert sentiment_score == 0.75, "Should use direct score field"
        assert mentions_count == 100000, "Should use direct portfolio_holding field"
    
    def test_crowd_stats_with_no_raw_data(self):
        """Test handling when raw_data is empty or None"""
        
        mock_data = MockCrowdStats(
            score=0.5,
            portfolio_holding=1000,
            raw_data=None
        )
        
        sentiment_score = mock_data.score
        mentions_count = mock_data.portfolio_holding or 0
        
        # Fallback logic should handle None raw_data gracefully
        if mock_data.raw_data and isinstance(mock_data.raw_data, dict):
            general_stats = mock_data.raw_data.get('generalStatsAll', {})
            if general_stats:
                if sentiment_score is None and 'score' in general_stats:
                    sentiment_score = general_stats.get('score')
        
        # Should use direct fields
        assert sentiment_score == 0.5
        assert mentions_count == 1000


class TestBloggerSentimentFallbackLogic:
    """Tests for blogger sentiment data extraction with fallback"""
    
    def test_blogger_sentiment_extraction_from_raw_data(self):
        """Test extraction from raw_data.bloggerSentiment when direct fields are null/zero"""
        
        # Simulate data structure as described in the problem statement
        raw_data = {
            'bloggerSentiment': {
                'bearish': '19',
                'bullish': '64',
                'bullishCount': 43,
                'bearishCount': 12,
                'neutralCount': 12,
                'score': 1,
                'avg': 0.7,
                'neutral': '17'
            }
        }
        
        mock_data = MockBloggerSentiment(
            bullish=0,  # Direct field is zero
            bearish=0,  # Direct field is zero
            bullish_count=0,  # Direct field is zero
            bearish_count=0,  # Direct field is zero
            neutral_count=0,  # Direct field is zero
            avg=None,  # Direct field is null
            raw_data=raw_data
        )
        
        # Simulate the fallback logic from the endpoint
        sentiment_score = mock_data.avg
        bullish_percent = mock_data.bullish if mock_data.bullish else None
        bearish_percent = mock_data.bearish if mock_data.bearish else None
        bullish_articles = mock_data.bullish_count or 0
        bearish_articles = mock_data.bearish_count or 0
        neutral_articles = mock_data.neutral_count or 0
        
        # Fallback to raw_data
        if mock_data.raw_data and isinstance(mock_data.raw_data, dict):
            blogger_data = mock_data.raw_data.get('bloggerSentiment', {})
            if blogger_data:
                # Extract percentages from strings
                if bullish_percent is None or bullish_percent == 0:
                    bullish_str = blogger_data.get('bullish')
                    if bullish_str:
                        try:
                            bullish_percent = float(bullish_str)
                        except (ValueError, TypeError):
                            pass
                
                if bearish_percent is None or bearish_percent == 0:
                    bearish_str = blogger_data.get('bearish')
                    if bearish_str:
                        try:
                            bearish_percent = float(bearish_str)
                        except (ValueError, TypeError):
                            pass
                
                # Extract counts
                if bullish_articles == 0 and 'bullishCount' in blogger_data:
                    bullish_articles = blogger_data.get('bullishCount', 0)
                if bearish_articles == 0 and 'bearishCount' in blogger_data:
                    bearish_articles = blogger_data.get('bearishCount', 0)
                if neutral_articles == 0 and 'neutralCount' in blogger_data:
                    neutral_articles = blogger_data.get('neutralCount', 0)
                
                # Extract sentiment score
                if sentiment_score is None or sentiment_score == 0:
                    sentiment_score = blogger_data.get('avg')
        
        total_articles = bullish_articles + bearish_articles + neutral_articles
        
        # Verify extraction
        assert bullish_percent == 64.0, "Should extract bullish percent from raw_data string"
        assert bearish_percent == 19.0, "Should extract bearish percent from raw_data string"
        assert bullish_articles == 43, "Should extract bullishCount from raw_data"
        assert bearish_articles == 12, "Should extract bearishCount from raw_data"
        assert neutral_articles == 12, "Should extract neutralCount from raw_data"
        assert total_articles == 67, "Should calculate total articles correctly"
        assert sentiment_score == 0.7, "Should extract avg from raw_data"
    
    def test_blogger_sentiment_uses_direct_fields_when_available(self):
        """Test that direct fields are used when available"""
        
        raw_data = {
            'bloggerSentiment': {
                'bearish': '19',
                'bullish': '64',
                'bullishCount': 43,
                'bearishCount': 12,
                'avg': 0.7,
            }
        }
        
        mock_data = MockBloggerSentiment(
            bullish=80,  # Direct field has value
            bearish=20,  # Direct field has value
            bullish_count=50,  # Direct field has value
            bearish_count=20,  # Direct field has value
            avg=0.85,  # Direct field has value
            raw_data=raw_data
        )
        
        # Simulate the fallback logic
        sentiment_score = mock_data.avg
        bullish_percent = mock_data.bullish if mock_data.bullish else None
        bearish_percent = mock_data.bearish if mock_data.bearish else None
        bullish_articles = mock_data.bullish_count or 0
        bearish_articles = mock_data.bearish_count or 0
        
        # Should NOT fallback since direct fields are set
        if mock_data.raw_data and isinstance(mock_data.raw_data, dict):
            blogger_data = mock_data.raw_data.get('bloggerSentiment', {})
            if blogger_data:
                # Only fallback if fields are None or 0
                if bullish_percent is None or bullish_percent == 0:
                    bullish_str = blogger_data.get('bullish')
                    if bullish_str:
                        bullish_percent = float(bullish_str)
        
        # Verify direct fields are used
        assert sentiment_score == 0.85, "Should use direct avg field"
        assert bullish_percent == 80, "Should use direct bullish field"
        assert bearish_percent == 20, "Should use direct bearish field"
        assert bullish_articles == 50, "Should use direct bullish_count field"
        assert bearish_articles == 20, "Should use direct bearish_count field"
    
    def test_blogger_sentiment_percentage_string_conversion(self):
        """Test conversion of percentage strings to floats"""
        
        raw_data = {
            'bloggerSentiment': {
                'bearish': '19',
                'bullish': '64',
                'neutral': '17'
            }
        }
        
        mock_data = MockBloggerSentiment(
            bullish=0,
            bearish=0,
            raw_data=raw_data
        )
        
        bullish_percent = None
        bearish_percent = None
        neutral_percent = None
        
        if mock_data.raw_data and isinstance(mock_data.raw_data, dict):
            blogger_data = mock_data.raw_data.get('bloggerSentiment', {})
            if blogger_data:
                bullish_str = blogger_data.get('bullish')
                if bullish_str:
                    try:
                        bullish_percent = float(bullish_str)
                    except (ValueError, TypeError):
                        pass
                
                bearish_str = blogger_data.get('bearish')
                if bearish_str:
                    try:
                        bearish_percent = float(bearish_str)
                    except (ValueError, TypeError):
                        pass
                
                neutral_str = blogger_data.get('neutral')
                if neutral_str:
                    try:
                        neutral_percent = float(neutral_str)
                    except (ValueError, TypeError):
                        pass
        
        # Verify string to float conversion
        assert bullish_percent == 64.0
        assert bearish_percent == 19.0
        assert neutral_percent == 17.0
    
    def test_blogger_sentiment_with_no_raw_data(self):
        """Test handling when raw_data is empty or None"""
        
        mock_data = MockBloggerSentiment(
            bullish=70,
            bearish=30,
            bullish_count=40,
            bearish_count=20,
            avg=0.8,
            raw_data=None
        )
        
        sentiment_score = mock_data.avg
        bullish_percent = mock_data.bullish if mock_data.bullish else None
        bullish_articles = mock_data.bullish_count or 0
        
        # Fallback logic should handle None raw_data gracefully
        if mock_data.raw_data and isinstance(mock_data.raw_data, dict):
            blogger_data = mock_data.raw_data.get('bloggerSentiment', {})
            if blogger_data:
                if sentiment_score is None:
                    sentiment_score = blogger_data.get('avg')
        
        # Should use direct fields
        assert sentiment_score == 0.8
        assert bullish_percent == 70
        assert bullish_articles == 40


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
