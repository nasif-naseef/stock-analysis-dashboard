"""
Dashboard Service

This module provides dashboard aggregation functionality including:
- Overview data aggregation across all tickers
- Alert generation based on significant changes
- Summary statistics
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.config import settings
from app.models.stock_data import (
    AnalystRating,
    NewsSentiment,
    QuantamentalScore,
    HedgeFundData,
    CrowdStatistics,
    BloggerSentiment,
    
    DataCollectionLog,
    SentimentType,
    RatingType,
)
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Enum for alert types"""
    RATING_CHANGE = "rating_change"
    SENTIMENT_SHIFT = "sentiment_shift"
    PRICE_TARGET_CHANGE = "price_target_change"
    HEDGE_FUND_ACTIVITY = "hedge_fund_activity"
    TRENDING = "trending"
    UNUSUAL_VOLUME = "unusual_volume"


class AlertSeverity(str, Enum):
    """Enum for alert severity"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


def _model_to_dict(obj: Any) -> Optional[Dict[str, Any]]:
    """Convert SQLAlchemy model to dictionary"""
    if obj is None:
        return None

    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        elif isinstance(value, (SentimentType, RatingType)):
            value = value.value
        result[column.name] = value

    return result


class DashboardService:
    """
    Service for aggregating dashboard data and generating alerts.
    """

    def get_overview(self, db: Session) -> Dict[str, Any]:
        """
        Get dashboard overview with latest data for all tickers.

        Args:
            db: Database session

        Returns:
            Dictionary with overview data
        """
        tickers = settings.ticker_list
        now = get_utc_now()

        result = {
            "timestamp": now.isoformat(),
            "total_tickers": len(tickers),
            "tickers": {},
            "summary": {
                "bullish_count": 0,
                "bearish_count": 0,
                "neutral_count": 0,
                "avg_sentiment": None,
            },
        }

        sentiment_scores = []

        for ticker in tickers:
            ticker_data = self._get_ticker_overview(db, ticker)
            result["tickers"][ticker] = ticker_data

            # Aggregate sentiment data
            if ticker_data.get("news_sentiment", {}).get("sentiment_score"):
                sentiment_scores.append(ticker_data["news_sentiment"]["sentiment_score"])

            sentiment = ticker_data.get("news_sentiment", {}).get("sentiment")
            if sentiment == "bullish":
                result["summary"]["bullish_count"] += 1
            elif sentiment == "bearish":
                result["summary"]["bearish_count"] += 1
            else:
                result["summary"]["neutral_count"] += 1

        # Calculate average sentiment
        if sentiment_scores:
            result["summary"]["avg_sentiment"] = round(sum(sentiment_scores) / len(sentiment_scores), 4)

        return result

    def _get_ticker_overview(self, db: Session, ticker: str) -> Dict[str, Any]:
        """
        Get overview data for a single ticker.

        Args:
            db: Database session
            ticker: Stock ticker symbol

        Returns:
            Dictionary with ticker overview
        """
        ticker = ticker.upper().strip()

        # Get latest data for each type
        analyst_rating = db.query(AnalystRating).filter(
            AnalystRating.ticker == ticker
        ).order_by(desc(AnalystRating.timestamp)).first()

        news_sentiment = db.query(NewsSentiment).filter(
            NewsSentiment.ticker == ticker
        ).order_by(desc(NewsSentiment.timestamp)).first()

        quantamental = db.query(QuantamentalScore).filter(
            QuantamentalScore.ticker == ticker
        ).order_by(desc(QuantamentalScore.timestamp)).first()

        hedge_fund = db.query(HedgeFundData).filter(
            HedgeFundData.ticker == ticker
        ).order_by(desc(HedgeFundData.timestamp)).first()

        crowd = db.query(CrowdStatistics).filter(
            CrowdStatistics.ticker == ticker
        ).order_by(desc(CrowdStatistics.timestamp)).first()

        blogger = db.query(BloggerSentiment).filter(
            BloggerSentiment.ticker == ticker
        ).order_by(desc(BloggerSentiment.timestamp)).first()

        return {
            "ticker": ticker,
            "analyst_rating": self._extract_analyst_summary(analyst_rating),
            "news_sentiment": self._extract_sentiment_summary(news_sentiment),
            "quantamental_score": self._extract_quantamental_summary(quantamental),
            "hedge_fund_data": self._extract_hedge_fund_summary(hedge_fund),
            "crowd_statistics": self._extract_crowd_summary(crowd),
            "blogger_sentiment": self._extract_blogger_summary(blogger),
        }

    def _extract_analyst_summary(self, data: Optional[AnalystRating]) -> Dict[str, Any]:
        """Extract summary from analyst rating data, with fallback to raw_data"""
        if not data:
            return {}
        
        # Get base values from the model
        consensus_rating = data.consensus_rating.value if data.consensus_rating else None
        consensus_score = data.consensus_score
        avg_price_target = data.avg_price_target
        current_price = data.current_price
        upside_potential = data.upside_potential
        total_analysts = data.total_analysts
        buy_count = data.buy_count
        hold_count = data.hold_count
        sell_count = data.sell_count
        
        # Fallback to raw_data if the parsed fields are null/zero
        if data.raw_data:
            raw = data.raw_data
            analyst_consensus = raw.get("analystConsensus", {}) or {}
            analyst_price_target = raw.get("analystPriceTarget", {}) or {}
            prices = raw.get("prices", [])
            
            # Total analysts fallback
            if not total_analysts:
                total_analysts = analyst_consensus.get("numberOfAnalystRatings", 0) or 0
            
            # Rating counts fallback
            if not buy_count:
                buy_count = analyst_consensus.get("buy", 0) or 0
            if not hold_count:
                hold_count = analyst_consensus.get("hold", 0) or 0
            if not sell_count:
                sell_count = analyst_consensus.get("sell", 0) or 0
            
            # Price targets fallback
            if avg_price_target is None:
                avg_price_target = analyst_price_target.get("average")
            
            # Current price fallback from prices array
            if current_price is None and prices:
                try:
                    current_price = prices[-1].get("p") if prices else None
                except (KeyError, IndexError, TypeError):
                    pass
            
            # Consensus score fallback
            if consensus_score is None:
                consensus_score = analyst_consensus.get("consensusRating")
            
            # Consensus text fallback for the rating
            if consensus_rating is None:
                consensus_text = analyst_consensus.get("consensus", "")
                if consensus_text:
                    # Map consensus text to rating type
                    text_lower = consensus_text.lower()
                    if "strong buy" in text_lower:
                        consensus_rating = "strong_buy"
                    elif "buy" in text_lower:
                        consensus_rating = "buy"
                    elif "sell" in text_lower:
                        consensus_rating = "sell" if "strong" not in text_lower else "strong_sell"
                    else:
                        consensus_rating = "hold"
            
            # Calculate upside potential if missing
            if upside_potential is None and avg_price_target and current_price and current_price > 0:
                upside_potential = ((avg_price_target - current_price) / current_price) * 100

        return {
            "timestamp": data.timestamp.isoformat() if data.timestamp else None,
            "consensus_rating": consensus_rating,
            "consensus_score": consensus_score,
            "avg_price_target": avg_price_target,
            "current_price": current_price,
            "upside_potential": upside_potential,
            "total_analysts": total_analysts,
            "buy_count": buy_count,
            "hold_count": hold_count,
            "sell_count": sell_count,
        }

    def _extract_sentiment_summary(self, data: Optional[NewsSentiment]) -> Dict[str, Any]:
        """Extract summary from news sentiment data"""
        if not data:
            return {}

        # Calculate a sentiment indicator based on bullish/bearish scores
        sentiment = None
        if data.stock_bullish_score is not None and data.stock_bearish_score is not None:
            if data.stock_bullish_score > data.stock_bearish_score:
                sentiment = "bullish"
            elif data.stock_bearish_score > data.stock_bullish_score:
                sentiment = "bearish"
            else:
                sentiment = "neutral"

        return {
            "timestamp": data.timestamp.isoformat() if data.timestamp else None,
            "sentiment": sentiment,
            "stock_bullish_score": data.stock_bullish_score,
            "stock_bearish_score": data.stock_bearish_score,
            "sector_bullish_score": data.sector_bullish_score,
            "sector_bearish_score": data.sector_bearish_score,
        }

    def _extract_quantamental_summary(self, data: Optional[QuantamentalScore]) -> Dict[str, Any]:
        """Extract summary from quantamental score data"""
        if not data:
            return {}

        return {
            "timestamp": data.timestamp.isoformat() if data.timestamp else None,
            "overall_score": data.overall_score,
            "quality_score": data.quality_score,
            "value_score": data.value_score,
            "growth_score": data.growth_score,
            "momentum_score": data.momentum_score,
        }

    def _extract_hedge_fund_summary(self, data: Optional[HedgeFundData]) -> Dict[str, Any]:
        """Extract summary from hedge fund data"""
        if not data:
            return {}

        return {
            "timestamp": data.timestamp.isoformat() if data.timestamp else None,
            "sentiment": data.hedge_fund_sentiment.value if data.hedge_fund_sentiment else None,
            "institutional_ownership_pct": data.institutional_ownership_pct,
            "hedge_fund_count": data.hedge_fund_count,
            "smart_money_score": data.smart_money_score,
        }

    def _extract_crowd_summary(self, data: Optional[CrowdStatistics]) -> Dict[str, Any]:
        """Extract summary from crowd statistics"""
        if not data:
            return {}

        return {
            "timestamp": data.timestamp.isoformat() if data.timestamp else None,
            "sentiment": data.crowd_sentiment.value if data.crowd_sentiment else None,
            "sentiment_score": data.sentiment_score,
            "bullish_percent": data.bullish_percent,
            "bearish_percent": data.bearish_percent,
            "mentions_count": data.mentions_count,
        }

    def _extract_blogger_summary(self, data: Optional[BloggerSentiment]) -> Dict[str, Any]:
        """Extract summary from blogger sentiment"""
        if not data:
            return {}

        return {
            "timestamp": data.timestamp.isoformat() if data.timestamp else None,
            "sentiment": data.blogger_sentiment.value if data.blogger_sentiment else None,
            "sentiment_score": data.sentiment_score,
            "bullish_percent": data.bullish_percent,
            "bearish_percent": data.bearish_percent,
            "total_articles": data.total_articles,
        }

    def get_alerts(
        self,
        db: Session,
        hours_ago: int = 24,
        severity: Optional[AlertSeverity] = None
    ) -> Dict[str, Any]:
        """
        Get alerts based on significant changes in data.

        Args:
            db: Database session
            hours_ago: Time period to check for changes
            severity: Optional filter by severity level

        Returns:
            Dictionary with alerts
        """
        tickers = settings.ticker_list
        now = get_utc_now()
        cutoff_time = now - timedelta(hours=hours_ago)

        alerts = []

        for ticker in tickers:
            ticker_alerts = self._generate_ticker_alerts(db, ticker, cutoff_time)
            alerts.extend(ticker_alerts)

        # Sort by severity (critical first) then by timestamp
        severity_order = {
            AlertSeverity.CRITICAL.value: 0,
            AlertSeverity.HIGH.value: 1,
            AlertSeverity.MEDIUM.value: 2,
            AlertSeverity.LOW.value: 3,
        }
        alerts.sort(key=lambda x: (severity_order.get(x.get("severity", "low"), 3), x.get("timestamp", "")), reverse=True)

        # Filter by severity if specified
        if severity:
            alerts = [a for a in alerts if a.get("severity") == severity.value]

        return {
            "timestamp": now.isoformat(),
            "hours_ago": hours_ago,
            "total_alerts": len(alerts),
            "alerts": alerts,
        }

    def _generate_ticker_alerts(
        self,
        db: Session,
        ticker: str,
        cutoff_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generate alerts for a single ticker.

        Args:
            db: Database session
            ticker: Stock ticker symbol
            cutoff_time: Time threshold for comparison

        Returns:
            List of alert dictionaries
        """
        alerts = []
        ticker = ticker.upper().strip()

        # Check analyst rating changes
        alerts.extend(self._check_analyst_alerts(db, ticker, cutoff_time))

        # Check sentiment shifts
        alerts.extend(self._check_sentiment_alerts(db, ticker, cutoff_time))

        # Check hedge fund activity
        alerts.extend(self._check_hedge_fund_alerts(db, ticker, cutoff_time))

        # Check crowd/trending alerts
        alerts.extend(self._check_crowd_alerts(db, ticker, cutoff_time))

        return alerts

    def _check_analyst_alerts(
        self,
        db: Session,
        ticker: str,
        cutoff_time: datetime
    ) -> List[Dict[str, Any]]:
        """Check for analyst rating alerts"""
        alerts = []

        # Get latest data
        current = db.query(AnalystRating).filter(
            AnalystRating.ticker == ticker
        ).order_by(desc(AnalystRating.timestamp)).first()

        # Get previous data
        previous = db.query(AnalystRating).filter(
            AnalystRating.ticker == ticker,
            AnalystRating.timestamp <= cutoff_time
        ).order_by(desc(AnalystRating.timestamp)).first()

        if current and previous:
            # Check consensus rating change
            if current.consensus_rating != previous.consensus_rating:
                alerts.append({
                    "ticker": ticker,
                    "type": AlertType.RATING_CHANGE.value,
                    "severity": AlertSeverity.HIGH.value,
                    "timestamp": current.timestamp.isoformat() if current.timestamp else None,
                    "message": f"Analyst consensus changed from {previous.consensus_rating.value if previous.consensus_rating else 'N/A'} to {current.consensus_rating.value if current.consensus_rating else 'N/A'}",
                    "data": {
                        "previous": previous.consensus_rating.value if previous.consensus_rating else None,
                        "current": current.consensus_rating.value if current.consensus_rating else None,
                    },
                })

            # Check price target change > 10%
            if current.avg_price_target and previous.avg_price_target and previous.avg_price_target > 0:
                pct_change = ((current.avg_price_target - previous.avg_price_target) / previous.avg_price_target) * 100
                if abs(pct_change) >= 10:
                    alerts.append({
                        "ticker": ticker,
                        "type": AlertType.PRICE_TARGET_CHANGE.value,
                        "severity": AlertSeverity.MEDIUM.value if abs(pct_change) < 20 else AlertSeverity.HIGH.value,
                        "timestamp": current.timestamp.isoformat() if current.timestamp else None,
                        "message": f"Price target changed by {pct_change:.1f}%",
                        "data": {
                            "previous": previous.avg_price_target,
                            "current": current.avg_price_target,
                            "percentage_change": round(pct_change, 2),
                        },
                    })

        return alerts

    def _check_sentiment_alerts(
        self,
        db: Session,
        ticker: str,
        cutoff_time: datetime
    ) -> List[Dict[str, Any]]:
        """Check for sentiment shift alerts"""
        alerts = []

        current = db.query(NewsSentiment).filter(
            NewsSentiment.ticker == ticker
        ).order_by(desc(NewsSentiment.timestamp)).first()

        previous = db.query(NewsSentiment).filter(
            NewsSentiment.ticker == ticker,
            NewsSentiment.timestamp <= cutoff_time
        ).order_by(desc(NewsSentiment.timestamp)).first()

        if current and previous:
            # Check sentiment direction change
            if current.sentiment != previous.sentiment:
                severity = AlertSeverity.MEDIUM.value
                # Higher severity for bullish to bearish or vice versa
                if (current.sentiment == SentimentType.BULLISH and previous.sentiment == SentimentType.BEARISH) or \
                   (current.sentiment == SentimentType.BEARISH and previous.sentiment == SentimentType.BULLISH):
                    severity = AlertSeverity.HIGH.value

                alerts.append({
                    "ticker": ticker,
                    "type": AlertType.SENTIMENT_SHIFT.value,
                    "severity": severity,
                    "timestamp": current.timestamp.isoformat() if current.timestamp else None,
                    "message": f"News sentiment shifted from {previous.sentiment.value if previous.sentiment else 'N/A'} to {current.sentiment.value if current.sentiment else 'N/A'}",
                    "data": {
                        "previous": previous.sentiment.value if previous.sentiment else None,
                        "current": current.sentiment.value if current.sentiment else None,
                    },
                })

        return alerts

    def _check_hedge_fund_alerts(
        self,
        db: Session,
        ticker: str,
        cutoff_time: datetime
    ) -> List[Dict[str, Any]]:
        """Check for hedge fund activity alerts"""
        alerts = []

        current = db.query(HedgeFundData).filter(
            HedgeFundData.ticker == ticker
        ).order_by(desc(HedgeFundData.timestamp)).first()

        previous = db.query(HedgeFundData).filter(
            HedgeFundData.ticker == ticker,
            HedgeFundData.timestamp <= cutoff_time
        ).order_by(desc(HedgeFundData.timestamp)).first()

        if current and previous:
            # Check for significant position changes
            new_positions = (current.new_positions or 0) + (current.increased_positions or 0)
            closed_positions = (current.closed_positions or 0) + (current.decreased_positions or 0)

            if new_positions >= 5 or closed_positions >= 5:
                severity = AlertSeverity.MEDIUM.value
                if new_positions >= 10 or closed_positions >= 10:
                    severity = AlertSeverity.HIGH.value

                activity_type = "accumulation" if new_positions > closed_positions else "distribution"
                alerts.append({
                    "ticker": ticker,
                    "type": AlertType.HEDGE_FUND_ACTIVITY.value,
                    "severity": severity,
                    "timestamp": current.timestamp.isoformat() if current.timestamp else None,
                    "message": f"Significant hedge fund {activity_type} detected",
                    "data": {
                        "new_positions": current.new_positions,
                        "increased_positions": current.increased_positions,
                        "decreased_positions": current.decreased_positions,
                        "closed_positions": current.closed_positions,
                    },
                })

        return alerts

    def _check_crowd_alerts(
        self,
        db: Session,
        ticker: str,
        cutoff_time: datetime
    ) -> List[Dict[str, Any]]:
        """Check for crowd/trending alerts"""
        alerts = []

        current = db.query(CrowdStatistics).filter(
            CrowdStatistics.ticker == ticker
        ).order_by(desc(CrowdStatistics.timestamp)).first()

        if current:
            # Check for trending status
            if current.rank_day and current.rank_day <= 10:
                alerts.append({
                    "ticker": ticker,
                    "type": AlertType.TRENDING.value,
                    "severity": AlertSeverity.LOW.value if current.rank_day > 5 else AlertSeverity.MEDIUM.value,
                    "timestamp": current.timestamp.isoformat() if current.timestamp else None,
                    "message": f"Stock trending at rank #{current.rank_day}",
                    "data": {
                        "rank_day": current.rank_day,
                        "rank_week": current.rank_week,
                        "mentions_count": current.mentions_count,
                    },
                })

        return alerts

    def get_collection_summary(self, db: Session, hours_ago: int = 24) -> Dict[str, Any]:
        """
        Get summary of data collection activity.

        Args:
            db: Database session
            hours_ago: Time period to summarize

        Returns:
            Dictionary with collection summary
        """
        now = get_utc_now()
        cutoff_time = now - timedelta(hours=hours_ago)

        # Get collection stats
        total_logs = db.query(func.count(DataCollectionLog.id)).filter(
            DataCollectionLog.timestamp >= cutoff_time
        ).scalar() or 0

        successful_logs = db.query(func.count(DataCollectionLog.id)).filter(
            DataCollectionLog.timestamp >= cutoff_time,
            DataCollectionLog.success == True
        ).scalar() or 0

        failed_logs = total_logs - successful_logs

        # Get records collected
        total_records = db.query(func.sum(DataCollectionLog.records_collected)).filter(
            DataCollectionLog.timestamp >= cutoff_time,
            DataCollectionLog.success == True
        ).scalar() or 0

        # Get latest collection per data type
        latest_collections = {}
        data_types = ["analyst_ratings", "news_sentiment", "quantamental_scores",
                      "hedge_fund_data", "crowd_statistics", "blogger_sentiment",
                      "technical_indicators", "target_prices"]

        for data_type in data_types:
            latest = db.query(DataCollectionLog).filter(
                DataCollectionLog.data_type == data_type,
                DataCollectionLog.success == True
            ).order_by(desc(DataCollectionLog.timestamp)).first()

            if latest:
                latest_collections[data_type] = {
                    "timestamp": latest.timestamp.isoformat() if latest.timestamp else None,
                    "records": latest.records_collected,
                }

        return {
            "timestamp": now.isoformat(),
            "hours_ago": hours_ago,
            "total_collections": total_logs,
            "successful": successful_logs,
            "failed": failed_logs,
            "success_rate": round((successful_logs / total_logs * 100), 1) if total_logs > 0 else 0,
            "total_records_collected": total_records,
            "latest_collections": latest_collections,
        }


# Create singleton instance
dashboard_service = DashboardService()
