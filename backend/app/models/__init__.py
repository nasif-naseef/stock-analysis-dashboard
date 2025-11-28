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
    # Models
    AnalystRating,
    NewsSentiment,
    QuantamentalScore,
    HedgeFundData,
    CrowdStatistics,
    BloggerSentiment,
    TechnicalIndicator,
    TargetPrice,
    ArticleAnalytics,
    DataCollectionLog,
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
    # Models
    "AnalystRating",
    "NewsSentiment",
    "QuantamentalScore",
    "HedgeFundData",
    "CrowdStatistics",
    "BloggerSentiment",
    "TechnicalIndicator",
    "TargetPrice",
    "ArticleAnalytics",
    "DataCollectionLog",
    # Configuration Models
    "TickerConfiguration",
    "APIConfiguration",
]
