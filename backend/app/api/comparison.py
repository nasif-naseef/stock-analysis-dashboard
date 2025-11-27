"""
Comparison API Router

This module contains endpoints for comparing stock data across periods and tickers.
"""
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.comparison_service import comparison_service, DATA_TYPE_CONFIG
from app.schemas.api_schemas import (
    DataType,
    ComparisonQuery,
    MultiTickerComparisonQuery,
)
from app.utils.helpers import normalize_ticker, is_valid_ticker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/compare", tags=["Comparison"])


def _validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker"""
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail=f"Invalid ticker format: {ticker}")
    return ticker


def _parse_periods(periods_str: str) -> List[str]:
    """Parse comma-separated periods string"""
    return [p.strip() for p in periods_str.split(',') if p.strip()]


def _parse_tickers(tickers_str: str) -> List[str]:
    """Parse comma-separated tickers string"""
    return [t.strip().upper() for t in tickers_str.split(',') if t.strip()]


@router.get(
    "/{ticker}",
    summary="Compare data across periods",
    description="Compare stock data for a ticker across multiple time periods"
)
async def compare_periods(
    ticker: str,
    periods: str = Query(
        default="1h,4h,1d,1w",
        description="Comma-separated list of periods (e.g., 1h,4h,1d,1w)"
    ),
    data_type: Optional[DataType] = Query(
        default=None,
        description="Specific data type to compare. If not provided, compares all types."
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Compare data for a ticker across multiple time periods.
    
    - **ticker**: Stock ticker symbol
    - **periods**: Comma-separated periods (e.g., "1h,4h,1d,1w")
    - **data_type**: Optional specific data type to compare
    
    Returns comparison with absolute changes, percentage changes, and trend directions.
    """
    ticker = _validate_ticker(ticker)
    periods_list = _parse_periods(periods)
    
    if not periods_list:
        raise HTTPException(
            status_code=400,
            detail="At least one period must be specified"
        )
    
    # Validate periods format
    valid_suffixes = ('h', 'd', 'w', 'm')
    for period in periods_list:
        if not any(period.lower().endswith(s) for s in valid_suffixes):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid period format: {period}. Use formats like 1h, 4h, 1d, 1w"
            )
    
    if data_type:
        # Compare specific data type
        result = comparison_service.compare_periods(
            db, ticker, data_type.value, periods_list
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    else:
        # Compare all data types
        result = comparison_service.get_all_comparisons(db, ticker, periods_list)
        return result


@router.get(
    "/tickers/multi",
    summary="Compare multiple tickers",
    description="Compare stock data across multiple tickers for a given period"
)
async def compare_tickers(
    tickers: str = Query(
        ...,
        description="Comma-separated list of tickers (e.g., AAPL,TSLA,NVDA)"
    ),
    period: str = Query(
        default="1d",
        description="Period for comparison (e.g., 1h, 4h, 1d, 1w)"
    ),
    data_type: DataType = Query(
        default=DataType.ANALYST_RATINGS,
        description="Data type to compare"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Compare data across multiple tickers for a given period.
    
    - **tickers**: Comma-separated list of tickers (e.g., "AAPL,TSLA,NVDA")
    - **period**: Period for comparison (e.g., "1d")
    - **data_type**: Type of data to compare
    
    Returns comparison showing changes for each ticker.
    """
    tickers_list = _parse_tickers(tickers)
    
    if len(tickers_list) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 tickers are required for comparison"
        )
    
    if len(tickers_list) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 tickers allowed for comparison"
        )
    
    # Validate tickers
    for t in tickers_list:
        if not is_valid_ticker(t):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid ticker format: {t}"
            )
    
    # Validate period format
    valid_suffixes = ('h', 'd', 'w', 'm')
    period = period.strip().lower()
    if not any(period.endswith(s) for s in valid_suffixes):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period format: {period}. Use formats like 1h, 4h, 1d, 1w"
        )
    
    result = comparison_service.compare_tickers(
        db, tickers_list, data_type.value, period
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get(
    "/data-types",
    summary="List available data types",
    description="Get list of data types available for comparison"
)
async def list_comparison_data_types() -> Dict[str, Any]:
    """
    Get list of data types available for comparison.
    
    Returns available data types and their comparable metrics.
    """
    result = {
        "data_types": {}
    }
    
    for data_type, config in DATA_TYPE_CONFIG.items():
        result["data_types"][data_type] = {
            "metrics": config["metrics"]
        }
    
    return result
