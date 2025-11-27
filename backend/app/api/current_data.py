"""
Current Data API Router

This module contains endpoints for fetching current (latest) stock data.
"""
import logging
from typing import Optional

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
    TargetPrice,
)
from app.schemas.stock_schemas import (
    AnalystRatingResponse,
    NewsSentimentResponse,
    QuantamentalScoreResponse,
    HedgeFundDataResponse,
    CrowdStatisticsResponse,
    BloggerSentimentResponse,
    TechnicalIndicatorResponse,
    TargetPriceResponse,
    TimeframeType,
)
from app.utils.helpers import normalize_ticker, is_valid_ticker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Current Data"])


def _validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker"""
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail=f"Invalid ticker format: {ticker}")
    return ticker


@router.get(
    "/analyst-ratings/{ticker}",
    response_model=AnalystRatingResponse,
    summary="Get latest analyst ratings",
    description="Get the most recent analyst ratings for a specific ticker"
)
async def get_analyst_ratings(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get the latest analyst ratings for a ticker"""
    ticker = _validate_ticker(ticker)
    
    data = db.query(AnalystRating).filter(
        AnalystRating.ticker == ticker
    ).order_by(desc(AnalystRating.timestamp)).first()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No analyst ratings found for ticker {ticker}"
        )
    
    return data


@router.get(
    "/news-sentiment/{ticker}",
    response_model=NewsSentimentResponse,
    summary="Get latest news sentiment",
    description="Get the most recent news sentiment analysis for a specific ticker"
)
async def get_news_sentiment(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get the latest news sentiment for a ticker"""
    ticker = _validate_ticker(ticker)
    
    data = db.query(NewsSentiment).filter(
        NewsSentiment.ticker == ticker
    ).order_by(desc(NewsSentiment.timestamp)).first()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No news sentiment found for ticker {ticker}"
        )
    
    return data


@router.get(
    "/quantamental-scores/{ticker}",
    response_model=QuantamentalScoreResponse,
    summary="Get latest quantamental scores",
    description="Get the most recent quantamental analysis scores for a specific ticker"
)
async def get_quantamental_scores(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get the latest quantamental scores for a ticker"""
    ticker = _validate_ticker(ticker)
    
    data = db.query(QuantamentalScore).filter(
        QuantamentalScore.ticker == ticker
    ).order_by(desc(QuantamentalScore.timestamp)).first()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No quantamental scores found for ticker {ticker}"
        )
    
    return data


@router.get(
    "/hedge-fund-data/{ticker}",
    response_model=HedgeFundDataResponse,
    summary="Get latest hedge fund data",
    description="Get the most recent hedge fund activity data for a specific ticker"
)
async def get_hedge_fund_data(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get the latest hedge fund data for a ticker"""
    ticker = _validate_ticker(ticker)
    
    data = db.query(HedgeFundData).filter(
        HedgeFundData.ticker == ticker
    ).order_by(desc(HedgeFundData.timestamp)).first()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No hedge fund data found for ticker {ticker}"
        )
    
    return data


@router.get(
    "/crowd-statistics/{ticker}",
    response_model=CrowdStatisticsResponse,
    summary="Get latest crowd statistics",
    description="Get the most recent crowd sentiment statistics for a specific ticker"
)
async def get_crowd_statistics(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get the latest crowd statistics for a ticker"""
    ticker = _validate_ticker(ticker)
    
    data = db.query(CrowdStatistics).filter(
        CrowdStatistics.ticker == ticker
    ).order_by(desc(CrowdStatistics.timestamp)).first()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No crowd statistics found for ticker {ticker}"
        )
    
    return data


@router.get(
    "/blogger-sentiment/{ticker}",
    response_model=BloggerSentimentResponse,
    summary="Get latest blogger sentiment",
    description="Get the most recent blogger sentiment for a specific ticker"
)
async def get_blogger_sentiment(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get the latest blogger sentiment for a ticker"""
    ticker = _validate_ticker(ticker)
    
    data = db.query(BloggerSentiment).filter(
        BloggerSentiment.ticker == ticker
    ).order_by(desc(BloggerSentiment.timestamp)).first()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No blogger sentiment found for ticker {ticker}"
        )
    
    return data


@router.get(
    "/technical-indicators/{ticker}",
    response_model=TechnicalIndicatorResponse,
    summary="Get latest technical indicators",
    description="Get the most recent technical indicators for a specific ticker"
)
async def get_technical_indicators(
    ticker: str,
    timeframe: Optional[TimeframeType] = Query(
        default=None,
        description="Filter by timeframe (e.g., 1h, 1d, 1w)"
    ),
    db: Session = Depends(get_db)
):
    """Get the latest technical indicators for a ticker"""
    ticker = _validate_ticker(ticker)
    
    query = db.query(TechnicalIndicator).filter(TechnicalIndicator.ticker == ticker)
    
    if timeframe:
        query = query.filter(TechnicalIndicator.timeframe == timeframe)
    
    data = query.order_by(desc(TechnicalIndicator.timestamp)).first()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No technical indicators found for ticker {ticker}"
        )
    
    return data


@router.get(
    "/target-prices/{ticker}",
    response_model=TargetPriceResponse,
    summary="Get latest target price",
    description="Get the most recent analyst target price for a specific ticker"
)
async def get_target_price(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get the latest target price for a ticker"""
    ticker = _validate_ticker(ticker)
    
    data = db.query(TargetPrice).filter(
        TargetPrice.ticker == ticker
    ).order_by(desc(TargetPrice.timestamp)).first()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No target prices found for ticker {ticker}"
        )
    
    return data
