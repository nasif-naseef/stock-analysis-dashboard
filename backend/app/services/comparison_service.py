"""
Comparison Service

This module provides comparison functionality for stock data including:
- Absolute changes between periods
- Percentage changes
- Trend directions
- Multi-period comparisons
- Multi-ticker comparisons
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.stock_data import (
    AnalystRating,
    NewsSentiment,
    QuantamentalScore,
    HedgeFundData,
    CrowdStatistics,
    BloggerSentiment,
    TechnicalIndicator,
)
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class TrendDirection(str, Enum):
    """Enum for trend direction"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    UNKNOWN = "unknown"


# Mapping of data types to their models and key metrics
DATA_TYPE_CONFIG = {
    "analyst_ratings": {
        "model": AnalystRating,
        "metrics": ["consensus_score", "avg_price_target", "upside_potential", "total_analysts"],
    },
    "news_sentiment": {
        "model": NewsSentiment,
        "metrics": ["sentiment_score", "buzz_score", "news_score", "total_articles"],
    },
    "quantamental_scores": {
        "model": QuantamentalScore,
        "metrics": ["overall_score", "quality_score", "value_score", "growth_score", "momentum_score"],
    },
    "hedge_fund_data": {
        "model": HedgeFundData,
        "metrics": ["institutional_ownership_pct", "hedge_fund_count", "smart_money_score"],
    },
    "crowd_statistics": {
        "model": CrowdStatistics,
        "metrics": ["sentiment_score", "bullish_percent", "bearish_percent", "mentions_count"],
    },
    "blogger_sentiment": {
        "model": BloggerSentiment,
        "metrics": ["sentiment_score", "bullish_percent", "bearish_percent", "total_articles"],
    },
}


def _parse_period_to_hours(period: str) -> int:
    """
    Parse period string to hours.
    
    Supported formats: 1h, 2h, 4h, 6h, 12h, 1d, 1w, 1M
    
    Args:
        period: Period string (e.g., "1h", "4h", "1d", "1w")
        
    Returns:
        Number of hours
    """
    period = period.lower().strip()
    
    if period.endswith('h'):
        return int(period[:-1])
    elif period.endswith('d'):
        return int(period[:-1]) * 24
    elif period.endswith('w'):
        return int(period[:-1]) * 24 * 7
    elif period.endswith('m'):
        return int(period[:-1]) * 24 * 30  # Approximate month
    else:
        # Default to treating as hours
        return int(period)


def _determine_trend(old_value: Optional[float], new_value: Optional[float], threshold: float = 0.01) -> TrendDirection:
    """
    Determine trend direction based on value change.
    
    Args:
        old_value: Previous value
        new_value: Current value
        threshold: Minimum percentage change to consider as trend (default 1%)
        
    Returns:
        TrendDirection enum value
    """
    if old_value is None or new_value is None:
        return TrendDirection.UNKNOWN
    
    if old_value == 0:
        if new_value > 0:
            return TrendDirection.UP
        elif new_value < 0:
            return TrendDirection.DOWN
        else:
            return TrendDirection.STABLE
    
    pct_change = (new_value - old_value) / abs(old_value)
    
    if pct_change > threshold:
        return TrendDirection.UP
    elif pct_change < -threshold:
        return TrendDirection.DOWN
    else:
        return TrendDirection.STABLE


def _calculate_change(old_value: Optional[float], new_value: Optional[float]) -> Dict[str, Any]:
    """
    Calculate absolute and percentage change between two values.
    
    Args:
        old_value: Previous value
        new_value: Current value
        
    Returns:
        Dictionary with change metrics
    """
    result = {
        "old_value": old_value,
        "new_value": new_value,
        "absolute_change": None,
        "percentage_change": None,
        "trend": TrendDirection.UNKNOWN.value,
    }
    
    if old_value is not None and new_value is not None:
        result["absolute_change"] = round(new_value - old_value, 4)
        
        if old_value != 0:
            result["percentage_change"] = round(((new_value - old_value) / abs(old_value)) * 100, 2)
        
        result["trend"] = _determine_trend(old_value, new_value).value
    
    return result


class ComparisonService:
    """
    Service for comparing stock data across different periods and tickers.
    """
    
    def compare_periods(
        self,
        db: Session,
        ticker: str,
        data_type: str,
        periods: List[str]
    ) -> Dict[str, Any]:
        """
        Compare data for a ticker across multiple periods.
        
        Args:
            db: Database session
            ticker: Stock ticker symbol
            data_type: Type of data to compare (e.g., "analyst_ratings")
            periods: List of period strings (e.g., ["1h", "4h", "1d", "1w"])
            
        Returns:
            Dictionary with comparison results
        """
        ticker = ticker.upper().strip()
        
        if data_type not in DATA_TYPE_CONFIG:
            return {"error": f"Unknown data type: {data_type}"}
        
        config = DATA_TYPE_CONFIG[data_type]
        model = config["model"]
        metrics = config["metrics"]
        
        now = get_utc_now()
        
        # Get current (latest) data
        current_data = db.query(model).filter(
            model.ticker == ticker
        ).order_by(desc(model.timestamp)).first()
        
        if not current_data:
            return {"error": f"No data found for ticker {ticker}"}
        
        result = {
            "ticker": ticker,
            "data_type": data_type,
            "current_timestamp": current_data.timestamp.isoformat() if current_data.timestamp else None,
            "periods": {},
        }
        
        # Compare each period
        for period in periods:
            hours_ago = _parse_period_to_hours(period)
            cutoff_time = now - timedelta(hours=hours_ago)
            
            # Get data from the specified period
            period_data = db.query(model).filter(
                model.ticker == ticker,
                model.timestamp <= cutoff_time
            ).order_by(desc(model.timestamp)).first()
            
            period_result = {
                "period": period,
                "hours_ago": hours_ago,
                "data_timestamp": period_data.timestamp.isoformat() if period_data and period_data.timestamp else None,
                "metrics": {},
            }
            
            # Calculate changes for each metric
            for metric in metrics:
                current_value = getattr(current_data, metric, None)
                period_value = getattr(period_data, metric, None) if period_data else None
                
                period_result["metrics"][metric] = _calculate_change(period_value, current_value)
            
            result["periods"][period] = period_result
        
        return result
    
    def compare_tickers(
        self,
        db: Session,
        tickers: List[str],
        data_type: str,
        period: str = "1d"
    ) -> Dict[str, Any]:
        """
        Compare data across multiple tickers for a given period.
        
        Args:
            db: Database session
            tickers: List of ticker symbols
            data_type: Type of data to compare
            period: Period for comparison (default "1d")
            
        Returns:
            Dictionary with comparison results
        """
        if data_type not in DATA_TYPE_CONFIG:
            return {"error": f"Unknown data type: {data_type}"}
        
        config = DATA_TYPE_CONFIG[data_type]
        model = config["model"]
        metrics = config["metrics"]
        
        now = get_utc_now()
        hours_ago = _parse_period_to_hours(period)
        cutoff_time = now - timedelta(hours=hours_ago)
        
        result = {
            "data_type": data_type,
            "period": period,
            "hours_ago": hours_ago,
            "tickers": {},
        }
        
        for ticker in tickers:
            ticker = ticker.upper().strip()
            
            # Get current data
            current_data = db.query(model).filter(
                model.ticker == ticker
            ).order_by(desc(model.timestamp)).first()
            
            # Get period data
            period_data = db.query(model).filter(
                model.ticker == ticker,
                model.timestamp <= cutoff_time
            ).order_by(desc(model.timestamp)).first()
            
            ticker_result = {
                "current_timestamp": current_data.timestamp.isoformat() if current_data and current_data.timestamp else None,
                "period_timestamp": period_data.timestamp.isoformat() if period_data and period_data.timestamp else None,
                "metrics": {},
            }
            
            for metric in metrics:
                current_value = getattr(current_data, metric, None) if current_data else None
                period_value = getattr(period_data, metric, None) if period_data else None
                
                ticker_result["metrics"][metric] = _calculate_change(period_value, current_value)
            
            result["tickers"][ticker] = ticker_result
        
        return result
    
    def get_all_comparisons(
        self,
        db: Session,
        ticker: str,
        periods: List[str]
    ) -> Dict[str, Any]:
        """
        Get comparisons for all data types for a ticker.
        
        Args:
            db: Database session
            ticker: Stock ticker symbol
            periods: List of periods to compare
            
        Returns:
            Dictionary with all comparison results
        """
        result = {
            "ticker": ticker.upper().strip(),
            "periods": periods,
            "data_types": {},
        }
        
        for data_type in DATA_TYPE_CONFIG.keys():
            comparison = self.compare_periods(db, ticker, data_type, periods)
            if "error" not in comparison:
                result["data_types"][data_type] = comparison
        
        return result


# Create singleton instance
comparison_service = ComparisonService()
