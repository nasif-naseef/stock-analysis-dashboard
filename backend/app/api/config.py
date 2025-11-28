"""
Configuration API Router

This module contains endpoints for managing ticker and API key configurations.
Includes CRUD operations for tickers and API keys with proper security masking.
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.config_service import config_service
from app.schemas.config_schemas import (
    TickerConfigurationCreate,
    TickerConfigurationUpdate,
    TickerConfigurationResponse,
    TickerConfigurationListResponse,
    APIConfigurationCreate,
    APIConfigurationUpdate,
    APIConfigurationResponse,
    APIConfigurationListResponse,
    ConfigurationStatusResponse,
    mask_api_key,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["Configuration"])


# ============================================
# Ticker Configuration Endpoints
# ============================================

@router.get(
    "/tickers",
    response_model=TickerConfigurationListResponse,
    summary="Get all ticker configurations",
    description="Get all configured tickers with their settings"
)
async def get_all_tickers(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
) -> TickerConfigurationListResponse:
    """
    Get all ticker configurations.
    
    - **include_inactive**: Include inactive tickers in the response
    """
    tickers = config_service.get_all_tickers(db, include_inactive=include_inactive)
    return TickerConfigurationListResponse(
        total=len(tickers),
        tickers=[TickerConfigurationResponse.model_validate(t) for t in tickers]
    )


@router.get(
    "/tickers/{ticker}",
    response_model=TickerConfigurationResponse,
    summary="Get a specific ticker configuration",
    description="Get configuration for a specific ticker symbol"
)
async def get_ticker(
    ticker: str,
    db: Session = Depends(get_db)
) -> TickerConfigurationResponse:
    """
    Get a specific ticker configuration by symbol.
    
    - **ticker**: Stock ticker symbol (e.g., AAPL, TSLA)
    """
    ticker = ticker.strip().upper()
    db_ticker = config_service.get_ticker(db, ticker)
    if not db_ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker {ticker} not found"
        )
    return TickerConfigurationResponse.model_validate(db_ticker)


@router.post(
    "/tickers",
    response_model=TickerConfigurationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ticker configuration",
    description="Add a new ticker to the configuration"
)
async def create_ticker(
    ticker_data: TickerConfigurationCreate,
    db: Session = Depends(get_db)
) -> TickerConfigurationResponse:
    """
    Create a new ticker configuration.
    
    - **ticker**: Stock ticker symbol (required)
    - **exchange**: Stock exchange (default: NASDAQ)
    - **tr_v4_id**: Trading Central V4 API identifier
    - **tr_v3_id**: Trading Central V3 API identifier
    - **is_active**: Whether the ticker is active (default: true)
    - **description**: Optional description
    """
    # Check if ticker already exists
    existing = config_service.get_ticker(db, ticker_data.ticker)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ticker {ticker_data.ticker} already exists"
        )
    
    try:
        ticker = config_service.create_ticker(db, ticker_data)
        return TickerConfigurationResponse.model_validate(ticker)
    except Exception as e:
        logger.error(f"Error creating ticker {ticker_data.ticker}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ticker: {str(e)}"
        )


@router.put(
    "/tickers/{ticker}",
    response_model=TickerConfigurationResponse,
    summary="Update a ticker configuration",
    description="Update an existing ticker configuration"
)
async def update_ticker(
    ticker: str,
    ticker_data: TickerConfigurationUpdate,
    db: Session = Depends(get_db)
) -> TickerConfigurationResponse:
    """
    Update an existing ticker configuration.
    
    - **ticker**: Stock ticker symbol to update
    - Only provided fields will be updated
    """
    ticker = ticker.strip().upper()
    updated = config_service.update_ticker(db, ticker, ticker_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker {ticker} not found"
        )
    return TickerConfigurationResponse.model_validate(updated)


@router.delete(
    "/tickers/{ticker}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a ticker configuration",
    description="Remove a ticker from the configuration"
)
async def delete_ticker(
    ticker: str,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a ticker configuration.
    
    - **ticker**: Stock ticker symbol to delete
    """
    ticker = ticker.strip().upper()
    deleted = config_service.delete_ticker(db, ticker)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker {ticker} not found"
        )


# ============================================
# API Key Configuration Endpoints
# ============================================

def _api_config_to_response(api_config) -> APIConfigurationResponse:
    """Convert API configuration to response with masked key"""
    return APIConfigurationResponse(
        id=api_config.id,
        service_name=api_config.service_name,
        api_key_masked=mask_api_key(api_config.api_key),
        description=api_config.description,
        is_active=api_config.is_active,
        created_at=api_config.created_at,
        updated_at=api_config.updated_at,
    )


@router.get(
    "/api-keys",
    response_model=APIConfigurationListResponse,
    summary="Get all API key configurations",
    description="Get all API key configurations (keys are masked for security)"
)
async def get_all_api_keys(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
) -> APIConfigurationListResponse:
    """
    Get all API key configurations.
    
    - **include_inactive**: Include inactive API keys in the response
    - API key values are masked for security
    """
    api_configs = config_service.get_all_api_configs(db, include_inactive=include_inactive)
    return APIConfigurationListResponse(
        total=len(api_configs),
        api_keys=[_api_config_to_response(c) for c in api_configs]
    )


@router.get(
    "/api-keys/{service_name}",
    response_model=APIConfigurationResponse,
    summary="Get a specific API key configuration",
    description="Get configuration for a specific API service (key is masked)"
)
async def get_api_key(
    service_name: str,
    db: Session = Depends(get_db)
) -> APIConfigurationResponse:
    """
    Get a specific API key configuration by service name.
    
    - **service_name**: Name of the API service (e.g., trading_central)
    - API key value is masked for security
    """
    service_name = service_name.strip().lower().replace(' ', '_')
    db_api_config = config_service.get_api_config(db, service_name)
    if not db_api_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API configuration for {service_name} not found"
        )
    return _api_config_to_response(db_api_config)


@router.post(
    "/api-keys",
    response_model=APIConfigurationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new API key configuration",
    description="Add a new API key configuration"
)
async def create_api_key(
    api_data: APIConfigurationCreate,
    db: Session = Depends(get_db)
) -> APIConfigurationResponse:
    """
    Create a new API key configuration.
    
    - **service_name**: Name of the API service (required)
    - **api_key**: The API key value (required)
    - **description**: Optional description
    - **is_active**: Whether the API key is active (default: true)
    """
    # Check if service already exists
    existing = config_service.get_api_config(db, api_data.service_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"API configuration for {api_data.service_name} already exists"
        )
    
    try:
        api_config = config_service.create_api_config(db, api_data)
        return _api_config_to_response(api_config)
    except Exception as e:
        logger.error(f"Error creating API config {api_data.service_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API configuration: {str(e)}"
        )


@router.put(
    "/api-keys/{service_name}",
    response_model=APIConfigurationResponse,
    summary="Update an API key configuration",
    description="Update an existing API key configuration"
)
async def update_api_key(
    service_name: str,
    api_data: APIConfigurationUpdate,
    db: Session = Depends(get_db)
) -> APIConfigurationResponse:
    """
    Update an existing API key configuration.
    
    - **service_name**: Name of the API service to update
    - Only provided fields will be updated
    - API key value is masked in response
    """
    service_name = service_name.strip().lower().replace(' ', '_')
    updated = config_service.update_api_config(db, service_name, api_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API configuration for {service_name} not found"
        )
    return _api_config_to_response(updated)


# ============================================
# Configuration Management Endpoints
# ============================================

@router.get(
    "/status",
    response_model=ConfigurationStatusResponse,
    summary="Get configuration status",
    description="Get current configuration status including counts and last reload time"
)
async def get_config_status(
    db: Session = Depends(get_db)
) -> ConfigurationStatusResponse:
    """
    Get current configuration status.
    
    Returns counts of active/total tickers and API keys, plus last reload time.
    """
    status_data = config_service.get_configuration_status(db)
    return ConfigurationStatusResponse(**status_data)


@router.post(
    "/reload",
    summary="Reload configuration from database",
    description="Reload all configurations from database into runtime cache"
)
async def reload_configuration(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reload all configurations from database.
    
    This refreshes the runtime configuration cache without requiring
    an application restart.
    """
    try:
        result = config_service.reload_configuration(db)
        return result
    except Exception as e:
        logger.error(f"Error reloading configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload configuration: {str(e)}"
        )
