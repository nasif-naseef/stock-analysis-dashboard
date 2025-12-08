"""
Tests for Hedge Fund Data Fallback Logic

This module tests the fallback logic for extracting hedge fund data
from raw_data.hedgeFundData when direct fields are null.
"""
import pytest
from app.utils.data_processor import ResponseBuilder


class TestHedgeFundFallbackLogic:
    """Tests for hedge fund data extraction with fallback"""
    
    def test_build_hedge_fund_from_overview_path(self):
        """Test extraction from raw_data.overview.hedgeFundData (primary path)"""
        builder = ResponseBuilder()
        
        raw_data = {
            'overview': {
                'hedgeFundData': {
                    'sentiment': 0.75,
                    'trendAction': 1,
                    'trendValue': 1000000
                }
            }
        }
        
        result = builder.build_hedge_fund(raw_data, 'AAPL')
        
        assert result['ticker'] == 'AAPL'
        assert result['sentiment'] == 0.75
        assert result['trend_action'] == 1
        assert result['trend_value'] == 1000000
    
    def test_build_hedge_fund_from_root_path_fallback(self):
        """Test extraction from raw_data.hedgeFundData (fallback path)"""
        builder = ResponseBuilder()
        
        raw_data = {
            'hedgeFundData': {
                'sentiment': 0.12,
                'trendAction': 3,
                'trendValue': -41010969
            }
        }
        
        result = builder.build_hedge_fund(raw_data, 'AAPL')
        
        assert result['ticker'] == 'AAPL'
        assert result['sentiment'] == 0.12
        assert result['trend_action'] == 3
        assert result['trend_value'] == -41010969
    
    def test_build_hedge_fund_prefers_overview_path(self):
        """Test that overview path is preferred when both exist"""
        builder = ResponseBuilder()
        
        raw_data = {
            'overview': {
                'hedgeFundData': {
                    'sentiment': 0.75,
                    'trendAction': 1,
                    'trendValue': 1000000
                }
            },
            'hedgeFundData': {
                'sentiment': 0.12,
                'trendAction': 3,
                'trendValue': -41010969
            }
        }
        
        result = builder.build_hedge_fund(raw_data, 'AAPL')
        
        # Should use overview path (first one)
        assert result['sentiment'] == 0.75
        assert result['trend_action'] == 1
        assert result['trend_value'] == 1000000
    
    def test_build_hedge_fund_with_empty_overview(self):
        """Test that fallback works when overview.hedgeFundData is empty"""
        builder = ResponseBuilder()
        
        raw_data = {
            'overview': {
                'hedgeFundData': {}
            },
            'hedgeFundData': {
                'sentiment': 0.12,
                'trendAction': 3,
                'trendValue': -41010969
            }
        }
        
        result = builder.build_hedge_fund(raw_data, 'AAPL')
        
        # Should fall back to root path
        assert result['sentiment'] == 0.12
        assert result['trend_action'] == 3
        assert result['trend_value'] == -41010969
    
    def test_build_hedge_fund_with_null_overview(self):
        """Test that fallback works when overview.hedgeFundData is None"""
        builder = ResponseBuilder()
        
        raw_data = {
            'overview': {
                'hedgeFundData': None
            },
            'hedgeFundData': {
                'sentiment': 0.12,
                'trendAction': 3,
                'trendValue': -41010969
            }
        }
        
        result = builder.build_hedge_fund(raw_data, 'AAPL')
        
        # Should fall back to root path
        assert result['sentiment'] == 0.12
        assert result['trend_action'] == 3
        assert result['trend_value'] == -41010969
    
    def test_build_hedge_fund_with_no_data(self):
        """Test handling when no hedge fund data exists"""
        builder = ResponseBuilder()
        
        raw_data = {}
        
        result = builder.build_hedge_fund(raw_data, 'AAPL')
        
        assert result['ticker'] == 'AAPL'
        assert result['sentiment'] is None
        assert result['trend_action'] is None
        assert result['trend_value'] is None
    
    def test_build_hedge_fund_with_partial_data(self):
        """Test handling when only some fields exist"""
        builder = ResponseBuilder()
        
        raw_data = {
            'hedgeFundData': {
                'sentiment': 0.12,
                # trendAction and trendValue missing
            }
        }
        
        result = builder.build_hedge_fund(raw_data, 'AAPL')
        
        assert result['ticker'] == 'AAPL'
        assert result['sentiment'] == 0.12
        assert result['trend_action'] is None
        assert result['trend_value'] is None
    
    def test_build_hedge_fund_with_list_input(self):
        """Test handling when raw_data is a list"""
        builder = ResponseBuilder()
        
        raw_data = [{
            'hedgeFundData': {
                'sentiment': 0.12,
                'trendAction': 3,
                'trendValue': -41010969
            }
        }]
        
        result = builder.build_hedge_fund(raw_data, 'AAPL')
        
        assert result['ticker'] == 'AAPL'
        assert result['sentiment'] == 0.12
        assert result['trend_action'] == 3
        assert result['trend_value'] == -41010969


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
