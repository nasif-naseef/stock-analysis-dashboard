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

from app.schemas.api_schemas import (
    # Enums
    DataType,
    TrendDirection,
    AlertType,
    AlertSeverity,
    # Request Schemas
    HistoricalDataQuery,
    ComparisonQuery,
    MultiTickerComparisonQuery,
    CollectTickerRequest,
    AlertsQuery,
    # Response Schemas
    ChangeMetrics,
    PeriodComparison,
    TickerComparisonResponse,
    MultiTickerComparisonResponse,
    AlertResponse,
    AlertsListResponse,
    TickerOverview,
    DashboardSummary,
    DashboardOverviewResponse,
    CollectionStatusResponse,
    CollectionTriggerResponse,
    CollectionResultResponse,
    HistoricalDataItem,
    HistoricalDataResponse,
    CollectionSummaryResponse,
    ErrorResponse,
    ValidationErrorResponse,
)

from app.schemas.config_schemas import (
    # Ticker Configuration
    TickerConfigurationBase,
    TickerConfigurationCreate,
    TickerConfigurationUpdate,
    TickerConfigurationResponse,
    TickerConfigurationListResponse,
    # API Configuration
    APIConfigurationBase,
    APIConfigurationCreate,
    APIConfigurationUpdate,
    APIConfigurationResponse,
    APIConfigurationListResponse,
    # Configuration Status
    ConfigurationStatusResponse,
    # Helper Functions
    mask_api_key,
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
    # API Schemas - Enums
    "DataType",
    "TrendDirection",
    "AlertType",
    "AlertSeverity",
    # API Schemas - Requests
    "HistoricalDataQuery",
    "ComparisonQuery",
    "MultiTickerComparisonQuery",
    "CollectTickerRequest",
    "AlertsQuery",
    # API Schemas - Responses
    "ChangeMetrics",
    "PeriodComparison",
    "TickerComparisonResponse",
    "MultiTickerComparisonResponse",
    "AlertResponse",
    "AlertsListResponse",
    "TickerOverview",
    "DashboardSummary",
    "DashboardOverviewResponse",
    "CollectionStatusResponse",
    "CollectionTriggerResponse",
    "CollectionResultResponse",
    "HistoricalDataItem",
    "HistoricalDataResponse",
    "CollectionSummaryResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    # Config Schemas - Ticker Configuration
    "TickerConfigurationBase",
    "TickerConfigurationCreate",
    "TickerConfigurationUpdate",
    "TickerConfigurationResponse",
    "TickerConfigurationListResponse",
    # Config Schemas - API Configuration
    "APIConfigurationBase",
    "APIConfigurationCreate",
    "APIConfigurationUpdate",
    "APIConfigurationResponse",
    "APIConfigurationListResponse",
    # Config Schemas - Configuration Status
    "ConfigurationStatusResponse",
    # Config Schemas - Helper Functions
    "mask_api_key",
]
