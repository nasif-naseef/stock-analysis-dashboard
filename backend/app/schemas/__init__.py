"""
Pydantic Schemas Package

This module exports all Pydantic schemas for the stock analysis API.
"""
from app.schemas.stock_schemas import (
    # Enums
    SentimentType,
    RatingType,
    TimeframeType,
    # Base
    StockDataBase,
    # Analyst Rating
    AnalystRatingBase,
    AnalystRatingCreate,
    AnalystRatingUpdate,
    AnalystRatingResponse,
    # News Sentiment
    NewsSentimentBase,
    NewsSentimentCreate,
    NewsSentimentUpdate,
    NewsSentimentResponse,
    # Quantamental Score
    QuantamentalScoreBase,
    QuantamentalScoreCreate,
    QuantamentalScoreUpdate,
    QuantamentalScoreResponse,
    # Hedge Fund Data
    HedgeFundDataBase,
    HedgeFundDataCreate,
    HedgeFundDataUpdate,
    HedgeFundDataResponse,
    # Crowd Statistics
    CrowdStatisticsBase,
    CrowdStatisticsCreate,
    CrowdStatisticsUpdate,
    CrowdStatisticsResponse,
    # Blogger Sentiment
    BloggerSentimentBase,
    BloggerSentimentCreate,
    BloggerSentimentUpdate,
    BloggerSentimentResponse,
    # Technical Indicator
    TechnicalIndicatorBase,
    TechnicalIndicatorCreate,
    TechnicalIndicatorUpdate,
    TechnicalIndicatorResponse,
    # Target Price
    TargetPriceBase,
    TargetPriceCreate,
    TargetPriceUpdate,
    TargetPriceResponse,
    # Article Analytics
    ArticleAnalyticsBase,
    ArticleAnalyticsCreate,
    ArticleAnalyticsUpdate,
    ArticleAnalyticsResponse,
    # Data Collection Log
    DataCollectionLogBase,
    DataCollectionLogCreate,
    DataCollectionLogResponse,
    # Query Schemas
    TickerQuery,
    DateRangeQuery,
    StockDataQuery,
    TimeframeQuery,
    # Summary Schemas
    SentimentSummary,
    AnalystConsensusSummary,
    StockOverview,
    PaginatedResponse,
)

__all__ = [
    # Enums
    "SentimentType",
    "RatingType",
    "TimeframeType",
    # Base
    "StockDataBase",
    # Analyst Rating
    "AnalystRatingBase",
    "AnalystRatingCreate",
    "AnalystRatingUpdate",
    "AnalystRatingResponse",
    # News Sentiment
    "NewsSentimentBase",
    "NewsSentimentCreate",
    "NewsSentimentUpdate",
    "NewsSentimentResponse",
    # Quantamental Score
    "QuantamentalScoreBase",
    "QuantamentalScoreCreate",
    "QuantamentalScoreUpdate",
    "QuantamentalScoreResponse",
    # Hedge Fund Data
    "HedgeFundDataBase",
    "HedgeFundDataCreate",
    "HedgeFundDataUpdate",
    "HedgeFundDataResponse",
    # Crowd Statistics
    "CrowdStatisticsBase",
    "CrowdStatisticsCreate",
    "CrowdStatisticsUpdate",
    "CrowdStatisticsResponse",
    # Blogger Sentiment
    "BloggerSentimentBase",
    "BloggerSentimentCreate",
    "BloggerSentimentUpdate",
    "BloggerSentimentResponse",
    # Technical Indicator
    "TechnicalIndicatorBase",
    "TechnicalIndicatorCreate",
    "TechnicalIndicatorUpdate",
    "TechnicalIndicatorResponse",
    # Target Price
    "TargetPriceBase",
    "TargetPriceCreate",
    "TargetPriceUpdate",
    "TargetPriceResponse",
    # Article Analytics
    "ArticleAnalyticsBase",
    "ArticleAnalyticsCreate",
    "ArticleAnalyticsUpdate",
    "ArticleAnalyticsResponse",
    # Data Collection Log
    "DataCollectionLogBase",
    "DataCollectionLogCreate",
    "DataCollectionLogResponse",
    # Query Schemas
    "TickerQuery",
    "DateRangeQuery",
    "StockDataQuery",
    "TimeframeQuery",
    # Summary Schemas
    "SentimentSummary",
    "AnalystConsensusSummary",
    "StockOverview",
    "PaginatedResponse",
]
