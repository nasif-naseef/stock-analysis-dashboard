"""
Database Models Package

This module exports all SQLAlchemy models for the stock analysis application.
"""
from app.database import Base

# Import all models here for Alembic auto-detection
from app.models.stock_data import (
    # Enums
    SentimentType,
    RatingType,
    TimeframeType,
    StopLossType,
    StopLossDirection,
    StopLossTightness,
    # Legacy Models
    AnalystRating,
    CrowdStatistics,
    TechnicalIndicator,
    ArticleAnalytics,
    DataCollectionLog,
    # New Models matching notebook API structure
    AnalystConsensus,
    HistoricalAnalystConsensus,
    NewsSentiment,
    HedgeFundData,
    InsiderScore,
    CrowdStats,
    BloggerSentiment,
    QuantamentalScore,
    TargetPrice,
    ArticleDistribution,
    ArticleSentiment,
    SupportResistance,
    StopLoss,
    ChartEvent,
    TechnicalSummary,
)

from app.models.configuration import (
    TickerConfiguration,
    APIConfiguration,
)

__all__ = [
    # Base
    "Base",
    # Enums
    "SentimentType",
    "RatingType",
    "TimeframeType",
    "StopLossType",
    "StopLossDirection",
    "StopLossTightness",
    # Legacy Models
    "AnalystRating",
    "CrowdStatistics",
    "TechnicalIndicator",
    "ArticleAnalytics",
    "DataCollectionLog",
    # New Models
    "AnalystConsensus",
    "HistoricalAnalystConsensus",
    "NewsSentiment",
    "HedgeFundData",
    "InsiderScore",
    "CrowdStats",
    "BloggerSentiment",
    "QuantamentalScore",
    "TargetPrice",
    "ArticleDistribution",
    "ArticleSentiment",
    "SupportResistance",
    "StopLoss",
    "ChartEvent",
    "TechnicalSummary",
    # Configuration Models
    "TickerConfiguration",
    "APIConfiguration",
]
