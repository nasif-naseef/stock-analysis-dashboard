"""
Collection API Router

This module contains endpoints for managing data collection.
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.services.data_collection_service import data_collection_service
from app.tasks.scheduler import (
    get_scheduler_status,
    trigger_manual_collection,
)
from app.schemas.api_schemas import CollectionStatusResponse
from app.utils.helpers import normalize_ticker, is_valid_ticker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/collect", tags=["Collection"])


def _validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker"""
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail=f"Invalid ticker format: {ticker}")
    return ticker


@router.get(
    "/status",
    response_model=CollectionStatusResponse,
    summary="Get collection status",
    description="Get current data collection scheduler status and job information"
)
async def get_collection_status():
    """
    Get current data collection scheduler status.

    Returns information about:
    - Scheduler running state
    - Scheduled jobs and their next run times
    - Last collection results
    """
    return get_scheduler_status()


@router.post(
    "/all",
    summary="Trigger collection for all tickers",
    description="Trigger data collection for all configured tickers (runs in background)"
)
async def trigger_all_collection(
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Trigger data collection for all configured tickers.

    The collection runs in the background and returns immediately.
    Use the /status endpoint to check progress.
    """
    background_tasks.add_task(trigger_manual_collection, None)

    return {
        "status": "triggered",
        "message": f"Data collection started for all tickers: {settings.ticker_list}",
        "tickers": settings.ticker_list,
        "check_status_at": "/api/collect/status"
    }


@router.post(
    "/{ticker}",
    summary="Trigger collection for a specific ticker",
    description="Trigger data collection for a specific ticker"
)
async def trigger_ticker_collection(
    ticker: str,
    background: bool = True,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Trigger data collection for a specific ticker.

    - **ticker**: Stock ticker symbol
    - **background**: If True, runs in background. If False, waits for completion.

    Returns collection status or results depending on background parameter.
    """
    ticker = _validate_ticker(ticker)

    # Check if ticker is in configured list
    if ticker not in settings.ticker_list:
        raise HTTPException(
            status_code=400,
            detail=f"Ticker {ticker} is not in configured tickers: {settings.ticker_list}"
        )

    if background:
        # Run in background
        background_tasks.add_task(trigger_manual_collection, ticker)

        return {
            "status": "triggered",
            "message": f"Data collection started for {ticker}",
            "ticker": ticker,
            "check_status_at": "/api/collect/status"
        }
    else:
        # Run synchronously
        try:
            result = data_collection_service.collect_all_data_for_ticker(ticker, db)
            return result
        except Exception as e:
            logger.error(f"Error collecting data for {ticker}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to collect data: {str(e)}"
            )


@router.get(
    "/tickers",
    summary="Get configured tickers",
    description="Get list of configured tickers for data collection"
)
async def get_configured_tickers() -> Dict[str, Any]:
    """
    Get list of configured tickers for data collection.

    Returns the ticker list and their configurations.
    """
    return {
        "tickers": settings.ticker_list,
        "ticker_configs": settings.TICKER_CONFIGS
    }
