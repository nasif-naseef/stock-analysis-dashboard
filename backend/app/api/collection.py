"""
Collection API Router

This module contains endpoints for managing data collection.
"""
import logging
import random
from typing import Dict, Any
from datetime import datetime

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
from app.utils.helpers import normalize_ticker, is_valid_ticker, get_utc_now
from app.models.stock_data import (
    AnalystRating,
    NewsSentiment,
    QuantamentalScore,
    HedgeFundData,
    CrowdStatistics,
    BloggerSentiment,
    TechnicalIndicator,
    TargetPrice,
    DataCollectionLog,
    SentimentType,
    RatingType,
    TimeframeType,
)

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


@router.post(
    "/seed-demo-data",
    summary="Seed demo data for testing",
    description="Insert sample data into all tables for testing purposes when external APIs are unavailable"
)
async def seed_demo_data(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Seed demo data for testing purposes.
    
    This endpoint inserts sample data for all configured tickers to help test
    the dashboard when external APIs are unavailable.
    
    Returns summary of data seeded.
    """
    results = {
        "analyst_ratings": 0,
        "news_sentiment": 0,
        "quantamental_scores": 0,
        "hedge_fund_data": 0,
        "crowd_statistics": 0,
        "blogger_sentiment": 0,
        "technical_indicators": 0,
        "target_prices": 0,
        "collection_logs": 0,
        "errors": []
    }
    
    timestamp = get_utc_now()
    tickers = settings.ticker_list
    
    # Sample price data per ticker for realism
    price_data = {
        "AAPL": {"price": 175.50, "target": 195.00},
        "TSLA": {"price": 245.30, "target": 280.00},
        "NVDA": {"price": 485.60, "target": 550.00},
        "GOOGL": {"price": 138.75, "target": 155.00},
        "MSFT": {"price": 378.20, "target": 420.00},
    }
    
    # Pre-defined choice lists for better performance
    rating_choices = [RatingType.BUY, RatingType.STRONG_BUY, RatingType.HOLD]
    sentiment_choices = [SentimentType.BULLISH, SentimentType.NEUTRAL]
    
    try:
        for ticker in tickers:
            ticker_price = price_data.get(ticker, {"price": 100.0, "target": 120.0})
            
            # Seed Analyst Rating
            analyst_rating = AnalystRating(
                ticker=ticker,
                timestamp=timestamp,
                strong_buy_count=random.randint(5, 15),
                buy_count=random.randint(8, 20),
                hold_count=random.randint(3, 10),
                sell_count=random.randint(0, 5),
                strong_sell_count=random.randint(0, 2),
                total_analysts=random.randint(20, 40),
                consensus_rating=random.choice(rating_choices),
                consensus_score=round(random.uniform(3.5, 4.5), 2),
                avg_price_target=ticker_price["target"],
                high_price_target=ticker_price["target"] * 1.15,
                low_price_target=ticker_price["target"] * 0.85,
                current_price=ticker_price["price"],
                upside_potential=round((ticker_price["target"] / ticker_price["price"] - 1) * 100, 2),
                source="demo_data"
            )
            db.add(analyst_rating)
            results["analyst_ratings"] += 1
            
            # Seed News Sentiment
            news_sentiment = NewsSentiment(
                ticker=ticker,
                timestamp=timestamp,
                sentiment=random.choice(sentiment_choices),
                sentiment_score=round(random.uniform(0.1, 0.7), 4),
                buzz_score=round(random.uniform(0.5, 0.9), 4),
                news_score=round(random.uniform(0.4, 0.8), 4),
                total_articles=random.randint(20, 80),
                positive_articles=random.randint(10, 40),
                negative_articles=random.randint(5, 20),
                neutral_articles=random.randint(5, 20),
                sector_sentiment=round(random.uniform(0.2, 0.6), 4),
                sector_avg=round(random.uniform(0.3, 0.5), 4),
                source="demo_data"
            )
            db.add(news_sentiment)
            results["news_sentiment"] += 1
            
            # Seed Quantamental Score
            quantamental = QuantamentalScore(
                ticker=ticker,
                timestamp=timestamp,
                overall_score=round(random.uniform(55, 85), 2),
                quality_score=round(random.uniform(50, 90), 2),
                value_score=round(random.uniform(40, 80), 2),
                growth_score=round(random.uniform(50, 85), 2),
                momentum_score=round(random.uniform(45, 80), 2),
                revenue_growth=round(random.uniform(0.05, 0.25), 4),
                earnings_growth=round(random.uniform(0.08, 0.30), 4),
                profit_margin=round(random.uniform(0.10, 0.35), 4),
                debt_to_equity=round(random.uniform(0.3, 1.5), 4),
                return_on_equity=round(random.uniform(0.15, 0.40), 4),
                pe_ratio=round(random.uniform(15, 35), 2),
                pb_ratio=round(random.uniform(2, 10), 2),
                source="demo_data"
            )
            db.add(quantamental)
            results["quantamental_scores"] += 1
            
            # Seed Hedge Fund Data
            hedge_fund = HedgeFundData(
                ticker=ticker,
                timestamp=timestamp,
                institutional_ownership_pct=round(random.uniform(60, 85), 2),
                hedge_fund_count=random.randint(50, 200),
                total_shares_held=random.randint(500000000, 2000000000),
                market_value_held=random.randint(50000000000, 200000000000),
                new_positions=random.randint(5, 20),
                increased_positions=random.randint(30, 80),
                decreased_positions=random.randint(20, 50),
                closed_positions=random.randint(2, 15),
                hedge_fund_sentiment=random.choice(sentiment_choices),
                smart_money_score=round(random.uniform(55, 85), 2),
                source="demo_data"
            )
            db.add(hedge_fund)
            results["hedge_fund_data"] += 1
            
            # Seed Crowd Statistics
            crowd = CrowdStatistics(
                ticker=ticker,
                timestamp=timestamp,
                crowd_sentiment=random.choice(sentiment_choices),
                sentiment_score=round(random.uniform(0.1, 0.6), 4),
                mentions_count=random.randint(1000, 10000),
                mentions_change=round(random.uniform(-10, 30), 2),
                impressions=random.randint(100000, 1000000),
                engagement_rate=round(random.uniform(0.02, 0.08), 4),
                bullish_percent=round(random.uniform(45, 70), 2),
                bearish_percent=round(random.uniform(20, 40), 2),
                neutral_percent=round(random.uniform(5, 20), 2),
                trending_score=round(random.uniform(0.3, 0.9), 4),
                rank_day=random.randint(1, 50),
                rank_week=random.randint(1, 100),
                source="demo_data"
            )
            db.add(crowd)
            results["crowd_statistics"] += 1
            
            # Seed Blogger Sentiment
            blogger = BloggerSentiment(
                ticker=ticker,
                timestamp=timestamp,
                blogger_sentiment=random.choice(sentiment_choices),
                sentiment_score=round(random.uniform(0.2, 0.7), 4),
                total_articles=random.randint(10, 50),
                bullish_articles=random.randint(5, 30),
                bearish_articles=random.randint(2, 15),
                neutral_articles=random.randint(2, 10),
                bullish_percent=round(random.uniform(50, 75), 2),
                bearish_percent=round(random.uniform(15, 35), 2),
                avg_blogger_accuracy=round(random.uniform(0.5, 0.75), 4),
                source="demo_data"
            )
            db.add(blogger)
            results["blogger_sentiment"] += 1
            
            # Seed Technical Indicator (for 1d timeframe)
            technical = TechnicalIndicator(
                ticker=ticker,
                timestamp=timestamp,
                timeframe=TimeframeType.ONE_DAY,
                open_price=ticker_price["price"] * 0.99,
                high_price=ticker_price["price"] * 1.02,
                low_price=ticker_price["price"] * 0.98,
                close_price=ticker_price["price"],
                volume=random.randint(10000000, 100000000),
                sma_20=ticker_price["price"] * 0.98,
                sma_50=ticker_price["price"] * 0.95,
                sma_200=ticker_price["price"] * 0.90,
                ema_12=ticker_price["price"] * 0.99,
                ema_26=ticker_price["price"] * 0.97,
                rsi_14=round(random.uniform(40, 65), 2),
                macd=round(random.uniform(-2, 3), 4),
                macd_signal=round(random.uniform(-1.5, 2.5), 4),
                macd_histogram=round(random.uniform(-0.5, 0.5), 4),
                adx=round(random.uniform(20, 40), 2),
                atr=round(random.uniform(2, 8), 4),
                bollinger_upper=ticker_price["price"] * 1.05,
                bollinger_middle=ticker_price["price"],
                bollinger_lower=ticker_price["price"] * 0.95,
                support_1=ticker_price["price"] * 0.97,
                support_2=ticker_price["price"] * 0.94,
                resistance_1=ticker_price["price"] * 1.03,
                resistance_2=ticker_price["price"] * 1.06,
                pivot_point=ticker_price["price"],
                overall_signal=random.choice(sentiment_choices),
                source="demo_data"
            )
            db.add(technical)
            results["technical_indicators"] += 1
            
            # Seed Target Price
            target_price = TargetPrice(
                ticker=ticker,
                timestamp=timestamp,
                analyst_name="Demo Analyst",
                analyst_firm="Demo Research",
                target_price=ticker_price["target"],
                previous_target=ticker_price["target"] * 0.95,
                target_change=ticker_price["target"] * 0.05,
                target_change_pct=5.0,
                rating=RatingType.BUY,
                current_price_at_rating=ticker_price["price"],
                upside_to_target=round((ticker_price["target"] / ticker_price["price"] - 1) * 100, 2),
                analyst_accuracy_score=round(random.uniform(0.6, 0.85), 4),
                rating_date=timestamp,
                source="demo_data"
            )
            db.add(target_price)
            results["target_prices"] += 1
            
            # Add collection log
            collection_log = DataCollectionLog(
                timestamp=timestamp,
                ticker=ticker,
                data_type="demo_data",
                success=True,
                records_collected=7,
                duration_seconds=round(random.uniform(0.1, 0.5), 3),
                source="demo_data_endpoint"
            )
            db.add(collection_log)
            results["collection_logs"] += 1
        
        db.commit()
        logger.info(f"Demo data seeded successfully for {len(tickers)} tickers")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding demo data: {e}")
        results["errors"].append(str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to seed demo data: {str(e)}"
        )
    
    return {
        "status": "success",
        "message": f"Demo data seeded for {len(tickers)} tickers",
        "tickers": tickers,
        "results": results
    }
