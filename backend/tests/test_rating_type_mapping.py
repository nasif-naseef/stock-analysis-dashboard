"""
Tests for RatingType enum mapping and ResponseValidationError fix

This module tests the new moderate_buy and moderate_sell enum values
and the mapping function for TipRanks consensus strings.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.utils.helpers import map_consensus_to_rating_type
from app.models.stock_data import RatingType as ModelRatingType, AnalystConsensus
from app.schemas.stock_schemas import RatingType as SchemaRatingType


class TestRatingTypeEnum:
    """Test RatingType enum has all required values"""
    
    def test_model_rating_type_has_moderate_values(self):
        """Test that model RatingType enum includes moderate_buy and moderate_sell"""
        assert hasattr(ModelRatingType, 'MODERATE_BUY')
        assert hasattr(ModelRatingType, 'MODERATE_SELL')
        assert ModelRatingType.MODERATE_BUY.value == "moderate_buy"
        assert ModelRatingType.MODERATE_SELL.value == "moderate_sell"
    
    def test_schema_rating_type_has_moderate_values(self):
        """Test that schema RatingType enum includes moderate_buy and moderate_sell"""
        assert hasattr(SchemaRatingType, 'MODERATE_BUY')
        assert hasattr(SchemaRatingType, 'MODERATE_SELL')
        assert SchemaRatingType.MODERATE_BUY.value == "moderate_buy"
        assert SchemaRatingType.MODERATE_SELL.value == "moderate_sell"
    
    def test_all_rating_types_present(self):
        """Test that all expected rating types are present"""
        model_values = [e.value for e in ModelRatingType]
        schema_values = [e.value for e in SchemaRatingType]
        
        expected_values = [
            "strong_buy",
            "moderate_buy",
            "buy",
            "hold",
            "sell",
            "moderate_sell",
            "strong_sell"
        ]
        
        for expected in expected_values:
            assert expected in model_values, f"Missing {expected} in model RatingType"
            assert expected in schema_values, f"Missing {expected} in schema RatingType"


class TestConsensusMapping:
    """Test the map_consensus_to_rating_type helper function"""
    
    def test_map_strong_buy(self):
        """Test mapping 'Strong Buy' consensus"""
        result = map_consensus_to_rating_type("Strong Buy")
        assert result == "strong_buy"
    
    def test_map_moderate_buy(self):
        """Test mapping 'Moderate Buy' consensus"""
        result = map_consensus_to_rating_type("Moderate Buy")
        assert result == "moderate_buy"
    
    def test_map_buy(self):
        """Test mapping 'Buy' consensus"""
        result = map_consensus_to_rating_type("Buy")
        assert result == "buy"
    
    def test_map_hold(self):
        """Test mapping 'Hold' consensus"""
        result = map_consensus_to_rating_type("Hold")
        assert result == "hold"
    
    def test_map_sell(self):
        """Test mapping 'Sell' consensus"""
        result = map_consensus_to_rating_type("Sell")
        assert result == "sell"
    
    def test_map_moderate_sell(self):
        """Test mapping 'Moderate Sell' consensus"""
        result = map_consensus_to_rating_type("Moderate Sell")
        assert result == "moderate_sell"
    
    def test_map_strong_sell(self):
        """Test mapping 'Strong Sell' consensus"""
        result = map_consensus_to_rating_type("Strong Sell")
        assert result == "strong_sell"
    
    def test_map_case_insensitive(self):
        """Test that mapping is case-insensitive"""
        assert map_consensus_to_rating_type("STRONG BUY") == "strong_buy"
        assert map_consensus_to_rating_type("moderate buy") == "moderate_buy"
        assert map_consensus_to_rating_type("MoDeRaTe SeLl") == "moderate_sell"
    
    def test_map_with_whitespace(self):
        """Test that mapping handles extra whitespace"""
        assert map_consensus_to_rating_type("  Strong Buy  ") == "strong_buy"
        assert map_consensus_to_rating_type("Moderate Buy ") == "moderate_buy"
    
    def test_map_none(self):
        """Test that mapping None returns None"""
        result = map_consensus_to_rating_type(None)
        assert result is None
    
    def test_map_empty_string(self):
        """Test that mapping empty string returns None"""
        result = map_consensus_to_rating_type("")
        assert result is None
    
    def test_map_unknown_value(self):
        """Test that unknown consensus values default to 'hold'"""
        result = map_consensus_to_rating_type("Unknown Rating")
        assert result == "hold"
    
    def test_map_neutral(self):
        """Test that 'Neutral' maps to 'hold'"""
        result = map_consensus_to_rating_type("Neutral")
        assert result == "hold"


class TestAnalystRatingsEndpoint:
    """Test the analyst ratings endpoint with moderate ratings"""
    
    def test_get_analyst_ratings_with_moderate_buy(self):
        """Test that endpoint handles Moderate Buy consensus correctly"""
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import get_db
        
        # Create mock AnalystConsensus with "Moderate Buy"
        mock_consensus = MagicMock(spec=AnalystConsensus)
        mock_consensus.id = 1
        mock_consensus.ticker = "AAPL"
        mock_consensus.timestamp = datetime.now()
        mock_consensus.total_ratings = 20
        mock_consensus.buy_ratings = 12
        mock_consensus.hold_ratings = 6
        mock_consensus.sell_ratings = 2
        mock_consensus.consensus_recommendation = "Moderate Buy"
        mock_consensus.consensus_rating_score = 4.1
        mock_consensus.price_target_average = 180.0
        mock_consensus.price_target_high = 200.0
        mock_consensus.price_target_low = 160.0
        mock_consensus.source = "TipRanks"
        mock_consensus.raw_data = {}
        
        # Setup mock DB session
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.first.return_value = mock_consensus
        mock_db.query.return_value = mock_query
        
        # Override the dependency
        def override_get_db():
            return mock_db
        
        app.dependency_overrides[get_db] = override_get_db
        
        try:
            client = TestClient(app)
            # Make request
            response = client.get("/api/analyst-ratings/AAPL")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["consensus_rating"] == "moderate_buy"
            assert data["ticker"] == "AAPL"
            assert data["buy_count"] == 12
        finally:
            # Clean up
            app.dependency_overrides.clear()
    
    def test_get_analyst_ratings_with_moderate_sell(self):
        """Test that endpoint handles Moderate Sell consensus correctly"""
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import get_db
        
        # Create mock AnalystConsensus with "Moderate Sell"
        mock_consensus = MagicMock(spec=AnalystConsensus)
        mock_consensus.id = 1
        mock_consensus.ticker = "TSLA"
        mock_consensus.timestamp = datetime.now()
        mock_consensus.total_ratings = 15
        mock_consensus.buy_ratings = 3
        mock_consensus.hold_ratings = 5
        mock_consensus.sell_ratings = 7
        mock_consensus.consensus_recommendation = "Moderate Sell"
        mock_consensus.consensus_rating_score = 2.2
        mock_consensus.price_target_average = 150.0
        mock_consensus.price_target_high = 180.0
        mock_consensus.price_target_low = 120.0
        mock_consensus.source = "TipRanks"
        mock_consensus.raw_data = {}
        
        # Setup mock DB session
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.first.return_value = mock_consensus
        mock_db.query.return_value = mock_query
        
        # Override the dependency
        def override_get_db():
            return mock_db
        
        app.dependency_overrides[get_db] = override_get_db
        
        try:
            client = TestClient(app)
            # Make request
            response = client.get("/api/analyst-ratings/TSLA")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["consensus_rating"] == "moderate_sell"
            assert data["ticker"] == "TSLA"
            assert data["sell_count"] == 7
        finally:
            # Clean up
            app.dependency_overrides.clear()


class TestDashboardService:
    """Test dashboard service with AnalystConsensus data"""
    
    def test_extract_analyst_summary_from_consensus(self):
        """Test _extract_analyst_summary handles AnalystConsensus correctly"""
        from app.services.dashboard_service import DashboardService
        
        service = DashboardService()
        
        # Create mock AnalystConsensus
        mock_consensus = MagicMock(spec=AnalystConsensus)
        mock_consensus.timestamp = datetime.now()
        mock_consensus.consensus_recommendation = "Moderate Buy"
        mock_consensus.consensus_rating_score = 4.2
        mock_consensus.price_target_average = 175.0
        mock_consensus.total_ratings = 25
        mock_consensus.buy_ratings = 15
        mock_consensus.hold_ratings = 8
        mock_consensus.sell_ratings = 2
        
        # Extract summary
        summary = service._extract_analyst_summary(mock_consensus)
        
        # Verify
        assert summary is not None
        assert summary["consensus_rating"] == "moderate_buy"
        assert summary["consensus_score"] == 4.2
        assert summary["avg_price_target"] == 175.0
        assert summary["total_analysts"] == 25
        assert summary["buy_count"] == 15
        assert summary["hold_count"] == 8
        assert summary["sell_count"] == 2
        assert summary["current_price"] is None  # Not in AnalystConsensus
        assert summary["upside_potential"] is None  # Not in AnalystConsensus


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
