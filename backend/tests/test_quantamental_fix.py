"""
Unit Tests for Quantamental Response Builder Fix

This module tests the fix for the quantamental data mapping issue where
the response builder now correctly maps raw_data fields to both database
model fields and response schema fields.
"""
import pytest
from app.utils.response_builders import ResponseBuilder


class TestQuantamentalResponseBuilder:
    """Test suite for quantamental response builder"""
    
    def test_build_quantamental_with_valid_data(self):
        """Test building quantamental scores with valid Trading Central data"""
        # Sample raw_data from Trading Central API
        raw_data = {
            "quantamental": 58,
            "quantamentalLabel": {"id": "strong", "name": "Strong"},
            "growth": 62,
            "growthLabel": {"id": "strong", "name": "Strong"},
            "valuation": 20,
            "valuationLabel": {"id": "very-weak", "name": "Very Weak"},
            "quality": 95,
            "qualityLabel": {"id": "very-strong", "name": "Very Strong"},
            "momentum": 85,
            "momentumLabel": {"id": "very-strong", "name": "Very Strong"},
            "income": 25,
            "incomeLabel": {"id": "very-weak", "name": "Very Weak"}
        }
        
        result = ResponseBuilder.build_quantamental(raw_data, "AAPL")
        
        # Verify ticker
        assert result["ticker"] == "AAPL"
        
        # Verify database model fields (for backward compatibility)
        assert result["overall"] == 58
        assert result["growth"] == 62
        assert result["value"] == 20
        assert result["quality"] == 95
        assert result["momentum"] == 85
        assert result["income"] == 25
        
        # Verify response schema fields (the fix)
        assert result["overall_score"] == 58
        assert result["growth_score"] == 62
        assert result["value_score"] == 20
        assert result["quality_score"] == 95
        assert result["momentum_score"] == 85
        
        # Verify labels are extracted
        assert result["overall_label"] == "Strong"
        assert result["growth_label"] == "Strong"
        assert result["value_label"] == "Very Weak"
        assert result["quality_label"] == "Very Strong"
        assert result["momentum_label"] == "Very Strong"
        assert result["income_label"] == "Very Weak"
    
    def test_build_quantamental_with_list_input(self):
        """Test building quantamental scores when raw_data is a list"""
        raw_data = [{
            "quantamental": 58,
            "growth": 62,
            "valuation": 20,
            "quality": 95,
            "momentum": 85,
            "income": 25
        }]
        
        result = ResponseBuilder.build_quantamental(raw_data, "AAPL")
        
        # Should extract from first item in list
        assert result["overall_score"] == 58
        assert result["growth_score"] == 62
        assert result["value_score"] == 20
        assert result["quality_score"] == 95
        assert result["momentum_score"] == 85
    
    def test_build_quantamental_with_none_values(self):
        """Test building quantamental scores with None/missing values"""
        raw_data = {
            "quantamental": None,
            "growth": 62,
            # valuation is missing
            "quality": 95,
            "momentum": None,
            "income": 25
        }
        
        result = ResponseBuilder.build_quantamental(raw_data, "AAPL")
        
        # Verify None values are handled correctly
        assert result["overall_score"] is None
        assert result["growth_score"] == 62
        assert result["value_score"] is None
        assert result["quality_score"] == 95
        assert result["momentum_score"] is None
    
    def test_build_quantamental_with_labels_missing(self):
        """Test building quantamental scores when labels are missing"""
        raw_data = {
            "quantamental": 58,
            "growth": 62,
            "valuation": 20,
            "quality": 95,
            "momentum": 85
            # No labels provided
        }
        
        result = ResponseBuilder.build_quantamental(raw_data, "AAPL")
        
        # Scores should be present
        assert result["overall_score"] == 58
        assert result["growth_score"] == 62
        
        # Labels should be None
        assert result["overall_label"] is None
        assert result["growth_label"] is None
        assert result["value_label"] is None
    
    def test_build_quantamental_with_empty_input(self):
        """Test building quantamental scores with empty input"""
        raw_data = {}
        
        result = ResponseBuilder.build_quantamental(raw_data, "AAPL")
        
        # Should handle empty input gracefully
        assert result["ticker"] == "AAPL"
        assert result["overall_score"] is None
        assert result["growth_score"] is None
        assert result["value_score"] is None
        assert result["quality_score"] is None
        assert result["momentum_score"] is None
    
    def test_build_quantamental_with_none_input(self):
        """Test building quantamental scores with None input"""
        raw_data = None
        
        result = ResponseBuilder.build_quantamental(raw_data, "AAPL")
        
        # Should handle None input gracefully
        assert result["ticker"] == "AAPL"
        assert result["overall_score"] is None
        assert result["growth_score"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
