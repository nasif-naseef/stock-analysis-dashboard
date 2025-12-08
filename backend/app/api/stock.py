"""
Stock Data API Routes

This module contains API endpoints for all stock data types:
- Analyst consensus and ratings
- News sentiment
- Hedge fund data
- Insider scores
- Crowd statistics
- Blogger sentiment
- Quantamental scores
- Target prices
- Article distribution and sentiment
- Support/resistance levels
- Stop loss recommendations
- Chart events
- Technical summaries
"""
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Path

from app.services.stock_data_service import stock_data_service
from app.utils.helpers import normalize_ticker, is_valid_ticker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stock", tags=["Stock Data"])


def _validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker"""
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail=f"Invalid ticker format: {ticker}")
    return ticker


# ============================================
# Analyst Endpoints
# ============================================

@router.get(
    "/analyst/consensus/{ticker}",
    summary="Get analyst consensus",
    description="Get analyst consensus data including buy/hold/sell ratings and price targets"
)
async def get_analyst_consensus(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get analyst consensus for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_analyst_consensus(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


@router.get(
    "/analyst/history/{ticker}",
    summary="Get historical analyst consensus",
    description="Get historical analyst consensus data over time"
)
async def get_analyst_consensus_history(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get historical analyst consensus for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_analyst_consensus_history(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


@router.get(
    "/analyst/ratings/{ticker}",
    summary="Get individual analyst ratings",
    description="Get individual analyst ratings data"
)
async def get_analyst_ratings(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get individual analyst ratings for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_analyst_ratings(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# News Endpoints
# ============================================

@router.get(
    "/news/sentiment/{ticker}",
    summary="Get news sentiment",
    description="Get news sentiment scores for stock and sector"
)
async def get_news_sentiment(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get news sentiment for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_news_sentiment(ticker)
    
    # Ensure we have data - extract from raw_data if scores are null
    if result and "error" not in result:
        if result.get("stock_bullish_score") is None and result.get("raw_data"):
            raw = result.get("raw_data", {})
            sentiment_score = raw.get("newsSentimentScore", {})
            stock = sentiment_score.get("stock", {})
            sector = sentiment_score.get("sector", {})
            
            result["stock_bullish_score"] = stock.get("bullishPercent")
            result["stock_bearish_score"] = stock.get("bearishPercent")
            result["sector_bullish_score"] = sector.get("bullishPercent")
            result["sector_bearish_score"] = sector.get("bearishPercent")
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


@router.get(
    "/news/articles/{ticker}",
    summary="Get news articles",
    description="Get news articles for a ticker"
)
async def get_news_articles(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get news articles for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_news_articles(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Hedge Fund Endpoints
# ============================================

@router.get(
    "/hedge-fund/{ticker}",
    summary="Get hedge fund data",
    description="Get hedge fund sentiment and trend data"
)
async def get_hedge_fund_data(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get hedge fund data for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_hedge_fund_confidence(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Insider Score Endpoints
# ============================================

@router.get(
    "/insider-score/{ticker}",
    summary="Get insider score",
    description="Get insider confidence score data"
)
async def get_insider_score(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get insider score for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_insider_score(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Crowd Statistics Endpoints
# ============================================

@router.get(
    "/crowd/stats/{ticker}",
    summary="Get crowd statistics",
    description="Get crowd wisdom statistics"
)
async def get_crowd_stats(
    ticker: str = Path(..., description="Stock ticker symbol"),
    stats_type: str = Query(default="all", description="Stats type: all, individual, institution")
):
    """Get crowd statistics for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_crowd_stats(ticker, stats_type)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Blogger Sentiment Endpoints
# ============================================

@router.get(
    "/blogger/sentiment/{ticker}",
    summary="Get blogger sentiment",
    description="Get blogger sentiment data"
)
async def get_blogger_sentiment(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get blogger sentiment for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_blogger_sentiment(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Quantamental Endpoints
# ============================================

@router.get(
    "/quantamental/{ticker}",
    summary="Get quantamental scores",
    description="Get quantamental analysis scores"
)
async def get_quantamental_scores(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get quantamental scores for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_quantamental_scores(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


@router.get(
    "/quantamental/timeseries/{ticker}",
    summary="Get quantamental timeseries",
    description="Get quantamental scores over time"
)
async def get_quantamental_timeseries(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get quantamental timeseries for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_quantamental_timeseries(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Target Price Endpoints
# ============================================

@router.get(
    "/target-prices/{ticker}",
    summary="Get target prices",
    description="Get analyst target price data"
)
async def get_target_prices(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get target prices for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_target_prices(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Article Endpoints
# ============================================

@router.get(
    "/articles/distribution/{ticker}",
    summary="Get article distribution",
    description="Get article distribution across news, social, and web"
)
async def get_article_distribution(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get article distribution for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_article_distribution(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


@router.get(
    "/articles/sentiment/{ticker}",
    summary="Get article sentiment",
    description="Get article sentiment analysis"
)
async def get_article_sentiment(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get article sentiment for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_article_sentiment(ticker)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Support/Resistance Endpoints
# ============================================

@router.get(
    "/support-resistance/{ticker}",
    summary="Get support/resistance levels",
    description="Get support and resistance price levels"
)
async def get_support_resistance(
    ticker: str = Path(..., description="Stock ticker symbol"),
    date: Optional[str] = Query(default=None, description="Date for historical data (YYYY-MM-DD)")
):
    """Get support/resistance levels for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_support_resistance(ticker, date)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Stop Loss Endpoints
# ============================================

@router.get(
    "/stop-loss/{ticker}",
    summary="Get stop loss recommendations",
    description="Get stop loss price recommendations"
)
async def get_stop_loss(
    ticker: str = Path(..., description="Stock ticker symbol"),
    stop_type: str = Query(default="Volatility-Based", description="Stop loss type"),
    direction: str = Query(default="Below (Long Position)", description="Stop direction"),
    tightness: str = Query(default="Medium", description="Stop tightness level"),
    priceperiod: str = Query(default="daily", description="Price period"),
    comprehensive: bool = Query(default=False, description="Include comprehensive data")
):
    """Get stop loss recommendations for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_stop_loss(
        ticker, stop_type, direction, tightness, priceperiod, comprehensive
    )
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Chart Events Endpoints
# ============================================

@router.get(
    "/chart-events/{ticker}",
    summary="Get chart events",
    description="Get technical chart events and patterns"
)
async def get_chart_events(
    ticker: str = Path(..., description="Stock ticker symbol"),
    active: bool = Query(default=True, description="Only active events"),
    priceperiod: str = Query(default="daily", description="Price period")
):
    """Get chart events for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_chart_events(ticker, active, priceperiod)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


@router.get(
    "/chart-events/combined/{ticker}",
    summary="Get combined chart events",
    description="Get both active and historical chart events"
)
async def get_chart_events_combined(
    ticker: str = Path(..., description="Stock ticker symbol"),
    priceperiod: str = Query(default="daily", description="Price period")
):
    """Get combined chart events for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_chart_events_combined(ticker, priceperiod)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Technical Summaries Endpoints
# ============================================

@router.get(
    "/technical-summaries/{ticker}",
    summary="Get technical summaries",
    description="Get technical analysis summaries"
)
async def get_technical_summaries(
    ticker: str = Path(..., description="Stock ticker symbol"),
    category: Optional[str] = Query(default=None, description="Filter by category")
):
    """Get technical summaries for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_technical_summaries(ticker, category)
    
    if result and "error" in result:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return {"status": "success", "data": result}


# ============================================
# Overview Endpoint
# ============================================

@router.get(
    "/overview/{ticker}",
    summary="Get comprehensive stock overview",
    description="Get all available data for a ticker in one request"
)
async def get_stock_overview(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get comprehensive stock overview for a ticker"""
    ticker = _validate_ticker(ticker)
    result = stock_data_service.get_stock_overview(ticker)
    
    return {"status": "success", "data": result}
