"""
Dashboard API Router

This module contains endpoints for dashboard data aggregation and alerts.
"""
import logging
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.dashboard_service import dashboard_service, AlertSeverity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/overview",
    summary="Get dashboard overview",
    description="Get aggregated overview data for all tickers"
)
async def get_dashboard_overview(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get dashboard overview with latest data for all tickers.

    Returns aggregated data including:
    - Latest data for each ticker
    - Summary statistics (bullish/bearish counts, average sentiment)
    """
    return dashboard_service.get_overview(db)


@router.get(
    "/alerts",
    summary="Get dashboard alerts",
    description="Get alerts based on significant changes in stock data"
)
async def get_dashboard_alerts(
    hours_ago: int = Query(
        default=24,
        ge=1,
        le=168,
        description="Hours to look back for alerts (max 1 week)"
    ),
    severity: Optional[str] = Query(
        default=None,
        description="Filter by alert severity (low, medium, high, critical)"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get alerts based on significant changes in data.

    - **hours_ago**: Time period to check for changes (default 24 hours)
    - **severity**: Optional filter by severity level

    Returns alerts for:
    - Rating changes
    - Sentiment shifts
    - Price target changes
    - Hedge fund activity
    - Trending stocks
    """
    severity_filter = None
    if severity:
        try:
            severity_filter = AlertSeverity(severity.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity: {severity}. Valid values: low, medium, high, critical"
            )

    return dashboard_service.get_alerts(db, hours_ago, severity_filter)


@router.get(
    "/collection-summary",
    summary="Get collection summary",
    description="Get summary of data collection activity"
)
async def get_collection_summary(
    hours_ago: int = Query(
        default=24,
        ge=1,
        le=168,
        description="Hours to summarize (max 1 week)"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get summary of data collection activity.

    Returns:
    - Total collections attempted
    - Success/failure counts
    - Success rate
    - Total records collected
    - Latest collection per data type
    """
    return dashboard_service.get_collection_summary(db, hours_ago)


@router.get(
    "/ticker/{ticker}",
    summary="Get ticker overview",
    description="Get overview data for a specific ticker"
)
async def get_ticker_overview(
    ticker: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get overview data for a specific ticker.

    Returns latest data for all data types for the specified ticker.
    """
    ticker = ticker.upper().strip()

    return dashboard_service._get_ticker_overview(db, ticker)
