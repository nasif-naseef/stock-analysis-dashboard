"""
Tests for Configuration Management

This module contains tests for:
- Ticker configuration CRUD operations
- API key configuration CRUD operations
- API key masking
- Configuration service functionality
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.config_schemas import (
    TickerConfigurationCreate,
    TickerConfigurationUpdate,
    APIConfigurationCreate,
    APIConfigurationUpdate,
    mask_api_key,
)
from app.services.config_service import ConfigService

client = TestClient(app)


# ============================================
# Tests for mask_api_key function
# ============================================

class TestMaskApiKey:
    """Tests for the mask_api_key helper function"""
    
    def test_mask_short_key(self):
        """Test masking a short API key (less than 8 chars)"""
        result = mask_api_key("abc123")
        assert result == "ab**23"
        assert len(result) == 6
    
    def test_mask_medium_key(self):
        """Test masking a medium API key (9-12 chars)"""
        result = mask_api_key("abcdefghij")
        assert result == "abc****hij"
        assert len(result) == 10
    
    def test_mask_long_key(self):
        """Test masking a long API key (more than 12 chars)"""
        result = mask_api_key("abcdefghijklmnopqrst")
        assert result == "abcd************qrst"
        assert len(result) == 20
    
    def test_mask_empty_key(self):
        """Test masking an empty API key"""
        result = mask_api_key("")
        assert result == "****"
    
    def test_mask_very_short_key(self):
        """Test masking a very short API key (4 chars or less)"""
        result = mask_api_key("abcd")
        assert result == "****"
        assert len(result) == 4
        
        result2 = mask_api_key("ab")
        assert result2 == "**"
        assert len(result2) == 2
    
    def test_mask_preserves_length(self):
        """Test that masking preserves the original key length"""
        test_keys = ["12345", "123456789", "12345678901234567890"]
        for key in test_keys:
            result = mask_api_key(key)
            assert len(result) == len(key)


# ============================================
# Tests for Ticker Configuration Schemas
# ============================================

class TestTickerConfigurationSchemas:
    """Tests for ticker configuration Pydantic schemas"""
    
    def test_create_ticker_normalizes_to_uppercase(self):
        """Test that ticker is normalized to uppercase"""
        data = TickerConfigurationCreate(
            ticker="aapl",
            exchange="nasdaq"
        )
        assert data.ticker == "AAPL"
        assert data.exchange == "NASDAQ"
    
    def test_create_ticker_strips_whitespace(self):
        """Test that ticker strips whitespace"""
        data = TickerConfigurationCreate(
            ticker="  TSLA  ",
            exchange=" NASDAQ "
        )
        assert data.ticker == "TSLA"
        assert data.exchange == "NASDAQ"
    
    def test_create_ticker_with_all_fields(self):
        """Test creating ticker with all fields"""
        data = TickerConfigurationCreate(
            ticker="NVDA",
            exchange="NASDAQ",
            tr_v4_id="EQ-0C00000BXN",
            tr_v3_id="US-124689",
            is_active=True,
            description="NVIDIA Corporation"
        )
        assert data.ticker == "NVDA"
        assert data.exchange == "NASDAQ"
        assert data.tr_v4_id == "EQ-0C00000BXN"
        assert data.tr_v3_id == "US-124689"
        assert data.is_active is True
        assert data.description == "NVIDIA Corporation"
    
    def test_create_ticker_invalid_format(self):
        """Test that invalid ticker format raises error"""
        with pytest.raises(ValueError):
            TickerConfigurationCreate(
                ticker="INVALID!@#",
                exchange="NASDAQ"
            )
    
    def test_update_ticker_partial(self):
        """Test partial update with only some fields"""
        data = TickerConfigurationUpdate(
            is_active=False
        )
        assert data.is_active is False
        assert data.exchange is None
        assert data.tr_v4_id is None


# ============================================
# Tests for API Configuration Schemas
# ============================================

class TestAPIConfigurationSchemas:
    """Tests for API configuration Pydantic schemas"""
    
    def test_create_api_config_normalizes_service_name(self):
        """Test that service name is normalized"""
        data = APIConfigurationCreate(
            service_name="Trading Central",
            api_key="test-api-key-123"
        )
        assert data.service_name == "trading_central"
    
    def test_create_api_config_with_all_fields(self):
        """Test creating API config with all fields"""
        data = APIConfigurationCreate(
            service_name="trading_central",
            api_key="test-api-key-12345",
            description="Trading Central API",
            is_active=True
        )
        assert data.service_name == "trading_central"
        assert data.api_key == "test-api-key-12345"
        assert data.description == "Trading Central API"
        assert data.is_active is True
    
    def test_create_api_config_invalid_service_name(self):
        """Test that invalid service name raises error"""
        with pytest.raises(ValueError):
            APIConfigurationCreate(
                service_name="invalid!@#service",
                api_key="test-api-key"
            )
    
    def test_update_api_config_partial(self):
        """Test partial update with only some fields"""
        data = APIConfigurationUpdate(
            api_key="new-api-key"
        )
        assert data.api_key == "new-api-key"
        assert data.is_active is None


# ============================================
# Tests for ConfigService
# ============================================

class TestConfigService:
    """Tests for the ConfigService class"""
    
    def test_config_service_initialization(self):
        """Test ConfigService initializes correctly"""
        service = ConfigService()
        assert service._ticker_cache == {}
        assert service._api_key_cache == {}
        assert service._last_reload is None
    
    def test_get_active_ticker_list_empty(self):
        """Test getting active tickers when cache is empty"""
        service = ConfigService()
        tickers = service.get_active_ticker_list()
        assert tickers == []
    
    def test_get_ticker_config_not_found(self):
        """Test getting ticker config when not in cache"""
        service = ConfigService()
        config = service.get_ticker_config("AAPL")
        assert config is None
    
    def test_get_api_key_not_found(self):
        """Test getting API key when not in cache"""
        service = ConfigService()
        key = service.get_api_key("trading_central")
        assert key is None
    
    def test_mask_api_key_value(self):
        """Test the static mask method"""
        masked = ConfigService.mask_api_key_value("test-api-key-12345")
        # The key "test-api-key-12345" has 18 characters, so it shows first 4 and last 4
        assert "test" in masked[:4]
        assert "2345" in masked[-4:]
        assert "*" in masked
        assert "test-api-key-12345" not in masked


# ============================================
# Tests for API Endpoints (Integration)
# ============================================

class TestConfigAPIEndpoints:
    """Integration tests for configuration API endpoints"""
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_tickers_endpoint_exists(self):
        """Test that GET /api/config/tickers endpoint exists"""
        response = client.get("/api/config/tickers")
        # Should return 200 or 500 (if DB not available), not 404
        assert response.status_code != 404
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_api_keys_endpoint_exists(self):
        """Test that GET /api/config/api-keys endpoint exists"""
        response = client.get("/api/config/api-keys")
        # Should return 200 or 500 (if DB not available), not 404
        assert response.status_code != 404
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_get_config_status_endpoint_exists(self):
        """Test that GET /api/config/status endpoint exists"""
        response = client.get("/api/config/status")
        # Should return 200 or 500 (if DB not available), not 404
        assert response.status_code != 404
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_reload_config_endpoint_exists(self):
        """Test that POST /api/config/reload endpoint exists"""
        response = client.post("/api/config/reload")
        # Should return 200 or 500 (if DB not available), not 404
        assert response.status_code != 404


# ============================================
# Tests for API Response Security
# ============================================

class TestAPIResponseSecurity:
    """Tests to ensure API keys are properly masked in responses"""
    
    def test_api_key_not_exposed_in_response_schema(self):
        """Test that APIConfigurationResponse uses masked key"""
        from app.schemas.config_schemas import APIConfigurationResponse
        
        # Check that the schema has api_key_masked field, not api_key
        fields = APIConfigurationResponse.model_fields
        assert "api_key_masked" in fields
        assert "api_key" not in fields
    
    def test_mask_api_key_hides_sensitive_data(self):
        """Test that masking hides most of the API key"""
        original_key = "super-secret-api-key-12345"
        masked = mask_api_key(original_key)
        
        # Ensure the full key is not in the masked version
        assert original_key not in masked
        
        # Ensure asterisks are present
        assert "*" in masked
        
        # Ensure only partial key is visible
        visible_chars = masked.replace("*", "")
        assert len(visible_chars) < len(original_key) / 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
