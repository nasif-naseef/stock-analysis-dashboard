"""
Historical Data API Router

This module contains endpoints for fetching historical stock data with time filters.
"""
import logging
from datetime import timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.stock_data import (
    AnalystRating,
    NewsSentiment,
    QuantamentalScore,
    HedgeFundData,
    CrowdStatistics,
    BloggerSentiment,
    TechnicalIndicator,
    SentimentType,
    RatingType,
    TimeframeType,
)
from app.schemas.api_schemas import DataType, HistoricalDataResponse
from app.utils.helpers import normalize_ticker, is_valid_ticker, get_utc_now

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/history", tags=["Historical Data"])


# Mapping of data types to their models
DATA_TYPE_MODELS = {
    DataType.ANALYST_RATINGS: AnalystRating,
    DataType.NEWS_SENTIMENT: NewsSentiment,
    DataType.QUANTAMENTAL_SCORES: QuantamentalScore,
    DataType.HEDGE_FUND_DATA: HedgeFundData,
    DataType.CROWD_STATISTICS: CrowdStatistics,
    DataType.BLOGGER_SENTIMENT: BloggerSentiment,
    DataType.TECHNICAL_INDICATORS: TechnicalIndicator,
}


def _validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker"""
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail=f"Invalid ticker format: {ticker}")
    return ticker


def _model_to_dict(obj: Any) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dictionary"""
    if obj is None:
        return {}
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        elif isinstance(value, (SentimentType, RatingType, TimeframeType)):
            value = value.value
        result[column.name] = value
    
    # Remove raw_data to keep response clean (it's usually large)
    result.pop('raw_data', None)
    
    return result


@router.get(
    "/{data_type}/{ticker}",
    response_model=HistoricalDataResponse,
    summary="Get historical data",
    description="Get historical data for a specific data type and ticker with time filters"
)
async def get_historical_data(
    data_type: DataType,
    ticker: str,
    hours_ago: int = Query(
        default=24,
        ge=1,
        le=8760,
        description="Hours in the past to fetch data (max 1 year)"
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db)
):
    """
    Get historical data for a specific data type and ticker.
    
    - **data_type**: Type of data (analyst_ratings, news_sentiment, etc.)
    - **ticker**: Stock ticker symbol
    - **hours_ago**: How many hours in the past to fetch data
    - **limit**: Maximum number of records to return
    """
    ticker = _validate_ticker(ticker)
    
    if data_type not in DATA_TYPE_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported data type: {data_type}"
        )
    
    model = DATA_TYPE_MODELS[data_type]
    now = get_utc_now()
    cutoff_time = now - timedelta(hours=hours_ago)
    
    # Query historical data
    query = db.query(model).filter(
        model.ticker == ticker,
        model.timestamp >= cutoff_time
    ).order_by(desc(model.timestamp)).limit(limit)
    
    results = query.all()
    
    items = [_model_to_dict(item) for item in results]
    
    return HistoricalDataResponse(
        ticker=ticker,
        data_type=data_type.value,
        hours_ago=hours_ago,
        count=len(items),
        items=items
    )


@router.get(
    "/all/{ticker}",
    summary="Get all historical data types",
    description="Get historical data for all data types for a specific ticker"
)
async def get_all_historical_data(
    ticker: str,
    hours_ago: int = Query(
        default=24,
        ge=1,
        le=8760,
        description="Hours in the past to fetch data"
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of records per data type"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get historical data for all data types for a ticker.
    
    Returns data organized by data type with timestamps and counts.
    """
    ticker = _validate_ticker(ticker)
    
    now = get_utc_now()
    cutoff_time = now - timedelta(hours=hours_ago)
    
    result = {
        "ticker": ticker,
        "hours_ago": hours_ago,
        "timestamp": now.isoformat(),
        "data_types": {}
    }
    
    for data_type, model in DATA_TYPE_MODELS.items():
        query = db.query(model).filter(
            model.ticker == ticker,
            model.timestamp >= cutoff_time
        ).order_by(desc(model.timestamp)).limit(limit)
        
        results = query.all()
        items = [_model_to_dict(item) for item in results]
        
        result["data_types"][data_type.value] = {
            "count": len(items),
            "items": items
        }
    
    return result
