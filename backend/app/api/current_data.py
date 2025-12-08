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
    AnalystConsensus,
    NewsSentiment,
    QuantamentalScore,
    HedgeFundData,
    CrowdStatistics,
    CrowdStats,
    BloggerSentiment,
    TechnicalIndicator,
    TargetPrice,
    TimeframeType as ModelTimeframeType,
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
from app.utils.helpers import normalize_ticker, is_valid_ticker, map_consensus_to_rating_type

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
    
    # Try notebook-style table first
    data = db.query(AnalystConsensus).filter(
        AnalystConsensus.ticker == ticker
    ).order_by(desc(AnalystConsensus.timestamp)).first()
    
    if data:
        # Map consensus_recommendation to RatingType enum value
        consensus_rating = map_consensus_to_rating_type(data.consensus_recommendation)
        
        # Transform to expected response format
        return {
            "id": data.id,
            "ticker": data.ticker,
            "timestamp": data.timestamp,
            "strong_buy_count": 0,  # Not available in AnalystConsensus model
            "buy_count": data.buy_ratings or 0,
            "hold_count": data.hold_ratings or 0,
            "sell_count": data.sell_ratings or 0,
            "strong_sell_count": 0,  # Not available in AnalystConsensus model
            "total_analysts": data.total_ratings or 0,
            "consensus_rating": consensus_rating,
            "consensus_score": data.consensus_rating_score,
            "avg_price_target": data.price_target_average,
            "high_price_target": data.price_target_high,
            "low_price_target": data.price_target_low,
            "current_price": None,  # Not in AnalystConsensus model
            "upside_potential": None,  # Not in AnalystConsensus model
            "source": data.source,
            "raw_data": data.raw_data,
        }
    
    # Fall back to legacy table
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

    # Map database model fields to response schema fields
    # Also extract from raw_data as fallback if direct fields are None
    overall_score = data.overall
    growth_score = data.growth
    value_score = data.value
    quality_score = data.quality
    momentum_score = data.momentum
    
    # Fallback to raw_data if direct fields are None
    if overall_score is None and data.raw_data:
        raw_list = data.raw_data if isinstance(data.raw_data, list) else [data.raw_data]
        if raw_list and len(raw_list) > 0:
            raw_item = raw_list[0]
            overall_score = raw_item.get('quantamental')
            growth_score = raw_item.get('growth')
            value_score = raw_item.get('valuation')
            quality_score = raw_item.get('quality')
            momentum_score = raw_item.get('momentum')

    # Default values for fields not available in current model
    UNAVAILABLE_FIELDS = {
        "revenue_growth": None,
        "earnings_growth": None,
        "profit_margin": None,
        "debt_to_equity": None,
        "return_on_equity": None,
        "pe_ratio": None,
        "pb_ratio": None,
        "ps_ratio": None,
        "peg_ratio": None,
        "ev_ebitda": None,
        "sector_rank": None,
        "industry_rank": None,
        "overall_rank": None,
    }

    # Transform to expected response format
    return {
        "id": data.id,
        "ticker": data.ticker,
        "timestamp": data.timestamp,
        "overall_score": overall_score,
        "quality_score": quality_score,
        "value_score": value_score,
        "growth_score": growth_score,
        "momentum_score": momentum_score,
        **UNAVAILABLE_FIELDS,
        "source": data.source,
        "raw_data": data.raw_data,
    }


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
    
    # Try notebook-style table first
    data = db.query(CrowdStats).filter(
        CrowdStats.ticker == ticker
    ).order_by(desc(CrowdStats.timestamp)).first()
    
    if data:
        # Transform to expected response format
        return {
            "id": data.id,
            "ticker": data.ticker,
            "timestamp": data.timestamp,
            "portfolio_holding": data.portfolio_holding,
            "amount_of_portfolios": data.amount_of_portfolios,
            "percent_allocated": data.percent_allocated,
            "percent_over_last_7d": data.percent_over_last_7d,
            "percent_over_last_30d": data.percent_over_last_30d,
            "score": data.score,
            "frequency": data.frequency,
            "source": data.source,
            "raw_data": data.raw_data,
        }
    
    # Fall back to legacy table
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
        # Convert schema TimeframeType to model TimeframeType for SQLAlchemy filtering
        try:
            timeframe_enum = ModelTimeframeType(timeframe.value)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid timeframe: {timeframe}. Valid values: {', '.join([t.value for t in ModelTimeframeType])}"
            )
        query = query.filter(TechnicalIndicator.timeframe == timeframe_enum)

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
