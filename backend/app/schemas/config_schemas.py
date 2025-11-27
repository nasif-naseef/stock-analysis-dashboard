"""
Pydantic Schemas for Configuration Management

This module contains Pydantic models for API request/response validation
for ticker configuration and API key management endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


# ============================================
# Ticker Configuration Schemas
# ============================================

class TickerConfigurationBase(BaseModel):
    """Base schema for ticker configuration"""
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    exchange: str = Field(default="NASDAQ", max_length=50, description="Stock exchange")
    tr_v4_id: Optional[str] = Field(default=None, max_length=50, description="Trading Central V4 API identifier")
    tr_v3_id: Optional[str] = Field(default=None, max_length=50, description="Trading Central V3 API identifier")
    is_active: bool = Field(default=True, description="Whether the ticker is active for data collection")
    description: Optional[str] = Field(default=None, description="Optional description for the ticker")

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        v = v.strip().upper()
        if not v.isalnum():
            raise ValueError('Ticker must be alphanumeric')
        return v

    @field_validator('exchange')
    @classmethod
    def validate_exchange(cls, v: str) -> str:
        return v.strip().upper()


class TickerConfigurationCreate(TickerConfigurationBase):
    """Schema for creating a new ticker configuration"""
    pass


class TickerConfigurationUpdate(BaseModel):
    """Schema for updating an existing ticker configuration"""
    exchange: Optional[str] = Field(default=None, max_length=50, description="Stock exchange")
    tr_v4_id: Optional[str] = Field(default=None, max_length=50, description="Trading Central V4 API identifier")
    tr_v3_id: Optional[str] = Field(default=None, max_length=50, description="Trading Central V3 API identifier")
    is_active: Optional[bool] = Field(default=None, description="Whether the ticker is active for data collection")
    description: Optional[str] = Field(default=None, description="Optional description for the ticker")

    @field_validator('exchange')
    @classmethod
    def validate_exchange(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip().upper()
        return v


class TickerConfigurationResponse(BaseModel):
    """Schema for ticker configuration response"""
    id: int
    ticker: str
    exchange: str
    tr_v4_id: Optional[str] = None
    tr_v3_id: Optional[str] = None
    is_active: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TickerConfigurationListResponse(BaseModel):
    """Schema for list of ticker configurations"""
    total: int
    tickers: List[TickerConfigurationResponse]


# ============================================
# API Configuration Schemas
# ============================================

class APIConfigurationBase(BaseModel):
    """Base schema for API configuration"""
    service_name: str = Field(..., min_length=1, max_length=100, description="Name of the API service")
    description: Optional[str] = Field(default=None, description="Description of the API service")
    is_active: bool = Field(default=True, description="Whether the API key is active")

    @field_validator('service_name')
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        v = v.strip().lower().replace(' ', '_')
        if not v.replace('_', '').isalnum():
            raise ValueError('Service name must be alphanumeric with underscores only')
        return v


class APIConfigurationCreate(APIConfigurationBase):
    """Schema for creating a new API configuration"""
    api_key: str = Field(..., min_length=1, description="The API key value")


class APIConfigurationUpdate(BaseModel):
    """Schema for updating an existing API configuration"""
    api_key: Optional[str] = Field(default=None, min_length=1, description="The API key value")
    description: Optional[str] = Field(default=None, description="Description of the API service")
    is_active: Optional[bool] = Field(default=None, description="Whether the API key is active")


class APIConfigurationResponse(BaseModel):
    """Schema for API configuration response (with masked API key)"""
    id: int
    service_name: str
    api_key_masked: str = Field(description="Masked API key for security")
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class APIConfigurationListResponse(BaseModel):
    """Schema for list of API configurations"""
    total: int
    api_keys: List[APIConfigurationResponse]


# ============================================
# Configuration Status Schemas
# ============================================

class ConfigurationStatusResponse(BaseModel):
    """Schema for configuration status response"""
    active_tickers: int
    total_tickers: int
    active_api_keys: int
    total_api_keys: int
    last_reload: Optional[datetime] = None


# ============================================
# Helper Functions
# ============================================

def mask_api_key(api_key: str) -> str:
    """
    Mask an API key for secure display.
    
    Shows the first 4 and last 4 characters, with asterisks in between.
    For short keys (< 12 chars), shows first 2 and last 2.
    For very short keys (< 5 chars), shows all asterisks.
    """
    if not api_key:
        return "****"
    
    key_length = len(api_key)
    
    if key_length <= 4:
        # For very short keys, mask entirely
        return "*" * key_length
    elif key_length <= 8:
        # For short keys, show first 2 and last 2
        return f"{api_key[:2]}{'*' * (key_length - 4)}{api_key[-2:]}"
    elif key_length <= 12:
        # For medium keys, show first 3 and last 3
        return f"{api_key[:3]}{'*' * (key_length - 6)}{api_key[-3:]}"
    else:
        # For longer keys, show first 4 and last 4
        return f"{api_key[:4]}{'*' * (key_length - 8)}{api_key[-4:]}"
