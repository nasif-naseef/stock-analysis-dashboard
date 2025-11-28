"""
Pydantic Schemas for Stock Analysis Data

This module contains all Pydantic models for API request/response validation
and data serialization for stock analysis data.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from enum import Enum

# Type variable for generic paginated response
T = TypeVar("T")


class SentimentType(str, Enum):
    """Enum for sentiment classification"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class RatingType(str, Enum):
    """Enum for analyst rating types"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class TimeframeType(str, Enum):
    """Enum for technical indicator timeframes"""
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    FOUR_HOURS = "4h"
    SIX_HOURS = "6h"
    TWELVE_HOURS = "12h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


# ============================================
# Base Schemas
# ============================================

class StockDataBase(BaseModel):
    """Base schema with common fields"""
    ticker: str = Field(..., max_length=10, description="Stock ticker symbol")
    timestamp: Optional[datetime] = Field(default=None, description="Data timestamp")
    source: Optional[str] = Field(default=None, max_length=100, description="Data source")
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Raw API response")


# ============================================
# Analyst Rating Schemas
# ============================================

class AnalystRatingBase(StockDataBase):
    """Base schema for analyst ratings"""
    strong_buy_count: int = Field(default=0, ge=0)
    buy_count: int = Field(default=0, ge=0)
    hold_count: int = Field(default=0, ge=0)
    sell_count: int = Field(default=0, ge=0)
    strong_sell_count: int = Field(default=0, ge=0)
    total_analysts: int = Field(default=0, ge=0)
    consensus_rating: Optional[RatingType] = None
    consensus_score: Optional[float] = None
    avg_price_target: Optional[float] = None
    high_price_target: Optional[float] = None
    low_price_target: Optional[float] = None
    current_price: Optional[float] = None
    upside_potential: Optional[float] = None


class AnalystRatingCreate(AnalystRatingBase):
    """Schema for creating analyst rating records"""
    pass


class AnalystRatingUpdate(BaseModel):
    """Schema for updating analyst rating records"""
    strong_buy_count: Optional[int] = Field(default=None, ge=0)
    buy_count: Optional[int] = Field(default=None, ge=0)
    hold_count: Optional[int] = Field(default=None, ge=0)
    sell_count: Optional[int] = Field(default=None, ge=0)
    strong_sell_count: Optional[int] = Field(default=None, ge=0)
    total_analysts: Optional[int] = Field(default=None, ge=0)
    consensus_rating: Optional[RatingType] = None
    consensus_score: Optional[float] = None
    avg_price_target: Optional[float] = None
    high_price_target: Optional[float] = None
    low_price_target: Optional[float] = None
    current_price: Optional[float] = None
    upside_potential: Optional[float] = None


class AnalystRatingResponse(AnalystRatingBase):
    """Schema for analyst rating API response"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================
# News Sentiment Schemas
# ============================================

class NewsSentimentBase(StockDataBase):
    """Base schema for news sentiment"""
    sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1)
    buzz_score: Optional[float] = None
    news_score: Optional[float] = None
    total_articles: int = Field(default=0, ge=0)
    positive_articles: int = Field(default=0, ge=0)
    negative_articles: int = Field(default=0, ge=0)
    neutral_articles: int = Field(default=0, ge=0)
    sector_sentiment: Optional[float] = None
    sector_avg: Optional[float] = None


class NewsSentimentCreate(NewsSentimentBase):
    """Schema for creating news sentiment records"""
    pass


class NewsSentimentUpdate(BaseModel):
    """Schema for updating news sentiment records"""
    sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1)
    buzz_score: Optional[float] = None
    news_score: Optional[float] = None
    total_articles: Optional[int] = Field(default=None, ge=0)
    positive_articles: Optional[int] = Field(default=None, ge=0)
    negative_articles: Optional[int] = Field(default=None, ge=0)
    neutral_articles: Optional[int] = Field(default=None, ge=0)


class NewsSentimentResponse(NewsSentimentBase):
    """Schema for news sentiment API response"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================
# Quantamental Score Schemas
# ============================================

class QuantamentalScoreBase(StockDataBase):
    """Base schema for quantamental scores"""
    overall_score: Optional[float] = Field(default=None, ge=0, le=100)
    quality_score: Optional[float] = None
    value_score: Optional[float] = None
    growth_score: Optional[float] = None
    momentum_score: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    profit_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    return_on_equity: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    sector_rank: Optional[int] = None
    industry_rank: Optional[int] = None
    overall_rank: Optional[int] = None


class QuantamentalScoreCreate(QuantamentalScoreBase):
    """Schema for creating quantamental score records"""
    pass


class QuantamentalScoreUpdate(BaseModel):
    """Schema for updating quantamental score records"""
    overall_score: Optional[float] = Field(default=None, ge=0, le=100)
    quality_score: Optional[float] = None
    value_score: Optional[float] = None
    growth_score: Optional[float] = None
    momentum_score: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    profit_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    return_on_equity: Optional[float] = None


class QuantamentalScoreResponse(QuantamentalScoreBase):
    """Schema for quantamental score API response"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================
# Hedge Fund Data Schemas
# ============================================

class HedgeFundDataBase(StockDataBase):
    """Base schema for hedge fund data"""
    institutional_ownership_pct: Optional[float] = None
    hedge_fund_count: int = Field(default=0, ge=0)
    total_shares_held: Optional[float] = None
    market_value_held: Optional[float] = None
    new_positions: int = Field(default=0, ge=0)
    increased_positions: int = Field(default=0, ge=0)
    decreased_positions: int = Field(default=0, ge=0)
    closed_positions: int = Field(default=0, ge=0)
    hedge_fund_sentiment: Optional[SentimentType] = None
    smart_money_score: Optional[float] = Field(default=None, ge=0, le=100)
    top_holders: Optional[List[Dict[str, Any]]] = None
    shares_change_qoq: Optional[float] = None
    ownership_change_qoq: Optional[float] = None


class HedgeFundDataCreate(HedgeFundDataBase):
    """Schema for creating hedge fund data records"""
    pass


class HedgeFundDataUpdate(BaseModel):
    """Schema for updating hedge fund data records"""
    institutional_ownership_pct: Optional[float] = None
    hedge_fund_count: Optional[int] = Field(default=None, ge=0)
    total_shares_held: Optional[float] = None
    market_value_held: Optional[float] = None
    new_positions: Optional[int] = Field(default=None, ge=0)
    increased_positions: Optional[int] = Field(default=None, ge=0)
    decreased_positions: Optional[int] = Field(default=None, ge=0)
    closed_positions: Optional[int] = Field(default=None, ge=0)
    hedge_fund_sentiment: Optional[SentimentType] = None
    smart_money_score: Optional[float] = Field(default=None, ge=0, le=100)


class HedgeFundDataResponse(HedgeFundDataBase):
    """Schema for hedge fund data API response"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================
# Crowd Statistics Schemas
# ============================================

class CrowdStatisticsBase(StockDataBase):
    """Base schema for crowd statistics"""
    crowd_sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1)
    mentions_count: int = Field(default=0, ge=0)
    mentions_change: Optional[float] = None
    impressions: int = Field(default=0, ge=0)
    engagement_rate: Optional[float] = None
    bullish_percent: Optional[float] = Field(default=None, ge=0, le=100)
    bearish_percent: Optional[float] = Field(default=None, ge=0, le=100)
    neutral_percent: Optional[float] = Field(default=None, ge=0, le=100)
    trending_score: Optional[float] = None
    rank_day: Optional[int] = None
    rank_week: Optional[int] = None
    total_posts: int = Field(default=0, ge=0)
    unique_users: int = Field(default=0, ge=0)
    avg_sentiment_post: Optional[float] = None


class CrowdStatisticsCreate(CrowdStatisticsBase):
    """Schema for creating crowd statistics records"""
    pass


class CrowdStatisticsUpdate(BaseModel):
    """Schema for updating crowd statistics records"""
    crowd_sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1)
    mentions_count: Optional[int] = Field(default=None, ge=0)
    mentions_change: Optional[float] = None
    impressions: Optional[int] = Field(default=None, ge=0)
    engagement_rate: Optional[float] = None
    bullish_percent: Optional[float] = Field(default=None, ge=0, le=100)
    bearish_percent: Optional[float] = Field(default=None, ge=0, le=100)
    neutral_percent: Optional[float] = Field(default=None, ge=0, le=100)


class CrowdStatisticsResponse(CrowdStatisticsBase):
    """Schema for crowd statistics API response"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================
# Blogger Sentiment Schemas
# ============================================

class BloggerSentimentBase(StockDataBase):
    """Base schema for blogger sentiment"""
    blogger_sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1)
    total_articles: int = Field(default=0, ge=0)
    bullish_articles: int = Field(default=0, ge=0)
    bearish_articles: int = Field(default=0, ge=0)
    neutral_articles: int = Field(default=0, ge=0)
    bullish_percent: Optional[float] = Field(default=None, ge=0, le=100)
    bearish_percent: Optional[float] = Field(default=None, ge=0, le=100)
    avg_blogger_accuracy: Optional[float] = None
    top_blogger_opinion: Optional[str] = None
    sentiment_change_1d: Optional[float] = None
    sentiment_change_1w: Optional[float] = None
    sentiment_change_1m: Optional[float] = None


class BloggerSentimentCreate(BloggerSentimentBase):
    """Schema for creating blogger sentiment records"""
    pass


class BloggerSentimentUpdate(BaseModel):
    """Schema for updating blogger sentiment records"""
    blogger_sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1)
    total_articles: Optional[int] = Field(default=None, ge=0)
    bullish_articles: Optional[int] = Field(default=None, ge=0)
    bearish_articles: Optional[int] = Field(default=None, ge=0)
    neutral_articles: Optional[int] = Field(default=None, ge=0)


class BloggerSentimentResponse(BloggerSentimentBase):
    """Schema for blogger sentiment API response"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================
# Technical Indicator Schemas
# ============================================

class TechnicalIndicatorBase(StockDataBase):
    """Base schema for technical indicators"""
    timeframe: TimeframeType
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    rsi_14: Optional[float] = Field(default=None, ge=0, le=100)
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None
    cci: Optional[float] = None
    williams_r: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    adx: Optional[float] = None
    plus_di: Optional[float] = None
    minus_di: Optional[float] = None
    atr: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    support_1: Optional[float] = None
    support_2: Optional[float] = None
    resistance_1: Optional[float] = None
    resistance_2: Optional[float] = None
    pivot_point: Optional[float] = None
    oscillator_signal: Optional[SentimentType] = None
    moving_avg_signal: Optional[SentimentType] = None
    overall_signal: Optional[SentimentType] = None


class TechnicalIndicatorCreate(TechnicalIndicatorBase):
    """Schema for creating technical indicator records"""
    pass


class TechnicalIndicatorUpdate(BaseModel):
    """Schema for updating technical indicator records"""
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[float] = None
    rsi_14: Optional[float] = Field(default=None, ge=0, le=100)
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    overall_signal: Optional[SentimentType] = None


class TechnicalIndicatorResponse(TechnicalIndicatorBase):
    """Schema for technical indicator API response"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================
# Target Price Schemas
# ============================================

class TargetPriceBase(StockDataBase):
    """Base schema for target prices"""
    analyst_name: Optional[str] = Field(default=None, max_length=200)
    analyst_firm: Optional[str] = Field(default=None, max_length=200)
    target_price: Optional[float] = None
    previous_target: Optional[float] = None
    target_change: Optional[float] = None
    target_change_pct: Optional[float] = None
    rating: Optional[RatingType] = None
    previous_rating: Optional[RatingType] = None
    rating_changed: bool = False
    current_price_at_rating: Optional[float] = None
    upside_to_target: Optional[float] = None
    analyst_accuracy_score: Optional[float] = None
    rating_date: Optional[datetime] = None


class TargetPriceCreate(TargetPriceBase):
    """Schema for creating target price records"""
    pass


class TargetPriceUpdate(BaseModel):
    """Schema for updating target price records"""
    target_price: Optional[float] = None
    rating: Optional[RatingType] = None
    rating_changed: Optional[bool] = None
    current_price_at_rating: Optional[float] = None
    upside_to_target: Optional[float] = None


class TargetPriceResponse(TargetPriceBase):
    """Schema for target price API response"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================
# Article Analytics Schemas
# ============================================

class ArticleAnalyticsBase(StockDataBase):
    """Base schema for article analytics"""
    article_id: Optional[str] = Field(default=None, max_length=100)
    article_url: Optional[str] = None
    article_title: Optional[str] = None
    author: Optional[str] = Field(default=None, max_length=200)
    publisher: Optional[str] = Field(default=None, max_length=200)
    publish_date: Optional[datetime] = None
    word_count: Optional[int] = Field(default=None, ge=0)
    category: Optional[str] = Field(default=None, max_length=100)
    sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1)
    relevance_score: Optional[float] = None
    views: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    price_impact: Optional[float] = None
    volume_impact: Optional[float] = None
    tags: Optional[List[str]] = None
    related_tickers: Optional[List[str]] = None


class ArticleAnalyticsCreate(ArticleAnalyticsBase):
    """Schema for creating article analytics records"""
    pass


class ArticleAnalyticsUpdate(BaseModel):
    """Schema for updating article analytics records"""
    sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1)
    relevance_score: Optional[float] = None
    views: Optional[int] = Field(default=None, ge=0)
    shares: Optional[int] = Field(default=None, ge=0)
    comments: Optional[int] = Field(default=None, ge=0)
    likes: Optional[int] = Field(default=None, ge=0)
    price_impact: Optional[float] = None
    volume_impact: Optional[float] = None


class ArticleAnalyticsResponse(ArticleAnalyticsBase):
    """Schema for article analytics API response"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================
# Data Collection Log Schemas
# ============================================

class DataCollectionLogBase(BaseModel):
    """Base schema for data collection logs"""
    ticker: Optional[str] = Field(default=None, max_length=10)
    data_type: str = Field(..., max_length=50)
    success: bool = False
    error_message: Optional[str] = None
    records_collected: int = Field(default=0, ge=0)
    duration_seconds: Optional[float] = None
    source: Optional[str] = Field(default=None, max_length=100)
    api_endpoint: Optional[str] = Field(default=None, max_length=500)


class DataCollectionLogCreate(DataCollectionLogBase):
    """Schema for creating data collection log records"""
    pass


class DataCollectionLogResponse(DataCollectionLogBase):
    """Schema for data collection log API response"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================
# Query/Filter Schemas
# ============================================

class TickerQuery(BaseModel):
    """Schema for querying by ticker"""
    ticker: str = Field(..., max_length=10, description="Stock ticker symbol")


class DateRangeQuery(BaseModel):
    """Schema for querying by date range"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class StockDataQuery(BaseModel):
    """Schema for querying stock data"""
    ticker: str = Field(..., max_length=10, description="Stock ticker symbol")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class TimeframeQuery(BaseModel):
    """Schema for querying by timeframe"""
    ticker: str = Field(..., max_length=10)
    timeframe: TimeframeType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ============================================
# Aggregation/Summary Schemas
# ============================================

class SentimentSummary(BaseModel):
    """Schema for sentiment summary"""
    ticker: str
    period: str
    avg_sentiment_score: Optional[float] = None
    bullish_count: int = 0
    bearish_count: int = 0
    neutral_count: int = 0
    total_data_points: int = 0


class AnalystConsensusSummary(BaseModel):
    """Schema for analyst consensus summary"""
    ticker: str
    consensus_rating: Optional[RatingType] = None
    avg_price_target: Optional[float] = None
    current_price: Optional[float] = None
    upside_potential: Optional[float] = None
    total_analysts: int = 0
    buy_percent: Optional[float] = None
    sell_percent: Optional[float] = None
    hold_percent: Optional[float] = None


class StockOverview(BaseModel):
    """Schema for comprehensive stock overview"""
    ticker: str
    last_updated: Optional[datetime] = None
    analyst_rating: Optional[AnalystRatingResponse] = None
    news_sentiment: Optional[NewsSentimentResponse] = None
    quantamental_score: Optional[QuantamentalScoreResponse] = None
    hedge_fund_data: Optional[HedgeFundDataResponse] = None
    crowd_statistics: Optional[CrowdStatisticsResponse] = None
    blogger_sentiment: Optional[BloggerSentimentResponse] = None
    technical_indicators: Optional[List[TechnicalIndicatorResponse]] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema for paginated responses with generic typing"""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int


# ============================================
# Notebook API Response Schemas
# ============================================

class AnalystConsensusResponse(BaseModel):
    """Schema for analyst consensus API response matching notebook structure"""
    ticker: str
    total_ratings: Optional[int] = None
    buy_ratings: Optional[int] = None
    hold_ratings: Optional[int] = None
    sell_ratings: Optional[int] = None
    consensus_recommendation: Optional[str] = None
    consensus_rating_score: Optional[float] = None
    price_target_high: Optional[float] = None
    price_target_low: Optional[float] = None
    price_target_average: Optional[float] = None


class NotebookNewsSentimentResponse(BaseModel):
    """Schema for news sentiment API response matching notebook structure"""
    ticker: str
    stock_bullish_score: Optional[float] = None
    stock_bearish_score: Optional[float] = None
    sector_bullish_score: Optional[float] = None
    sector_bearish_score: Optional[float] = None


class NotebookHedgeFundResponse(BaseModel):
    """Schema for hedge fund API response matching notebook structure"""
    ticker: str
    sentiment: Optional[float] = None
    trend_action: Optional[int] = None
    trend_value: Optional[int] = None


class InsiderScoreResponse(BaseModel):
    """Schema for insider score API response matching notebook structure"""
    ticker: str
    stock_score: Optional[float] = None
    sector_score: Optional[float] = None
    score: Optional[float] = None


class NotebookCrowdStatsResponse(BaseModel):
    """Schema for crowd stats API response matching notebook structure"""
    ticker: str
    portfolio_holding: int = 0
    amount_of_portfolios: int = 0
    amount_of_public_portfolios: int = 0
    percent_allocated: float = 0.0
    based_on_portfolios: int = 0
    percent_over_last_7d: float = 0.0
    percent_over_last_30d: float = 0.0
    score: float = 0.0
    individual_sector_average: float = 0.0
    frequency: float = 0.0


class NotebookBloggerSentimentResponse(BaseModel):
    """Schema for blogger sentiment API response matching notebook structure"""
    ticker: str
    bearish: int = 0
    neutral: int = 0
    bullish: int = 0
    bearish_count: int = 0
    neutral_count: int = 0
    bullish_count: int = 0
    score: float = 0.0
    avg: float = 0.0


class NotebookQuantamentalResponse(BaseModel):
    """Schema for quantamental API response matching notebook structure"""
    ticker: str
    overall: Optional[int] = None
    growth: Optional[int] = None
    value: Optional[int] = None
    income: Optional[int] = None
    quality: Optional[int] = None
    momentum: Optional[int] = None


class NotebookTargetPriceResponse(BaseModel):
    """Schema for target price API response matching notebook structure"""
    ticker: str
    close_price: Optional[float] = None
    target_price: Optional[float] = None
    target_date: Optional[str] = None
    last_updated: Optional[str] = None


class ArticleDistributionResponse(BaseModel):
    """Schema for article distribution API response matching notebook structure"""
    ticker: str
    total_articles: int = 0
    news_count: int = 0
    news_percentage: float = 0.0
    social_count: int = 0
    social_percentage: float = 0.0
    web_count: int = 0
    web_percentage: float = 0.0


class ArticleSentimentResponse(BaseModel):
    """Schema for article sentiment API response matching notebook structure"""
    ticker: str
    sentiment_id: Optional[str] = None
    sentiment_label: Optional[str] = None
    sentiment_value: Optional[int] = None
    subjectivity_id: Optional[str] = None
    subjectivity_label: Optional[str] = None
    subjectivity_value: Optional[int] = None
    confidence_id: Optional[str] = None
    confidence_name: Optional[str] = None


class SupportResistanceResponse(BaseModel):
    """Schema for support/resistance API response matching notebook structure"""
    symbol: str
    date: str
    exchange: str
    support_10: Optional[float] = None
    resistance_10: Optional[float] = None
    support_20: Optional[float] = None
    resistance_20: Optional[float] = None
    support_40: Optional[float] = None
    resistance_40: Optional[float] = None
    support_100: Optional[float] = None
    resistance_100: Optional[float] = None
    support_250: Optional[float] = None
    resistance_250: Optional[float] = None
    support_500: Optional[float] = None
    resistance_500: Optional[float] = None


class StopLossResponse(BaseModel):
    """Schema for stop loss API response matching notebook structure"""
    ticker: str
    recommended_stop_price: Optional[float] = None
    calculation_timestamp: Optional[str] = None
    stop_type: str = 'Volatility-Based'
    direction: str = 'Below (Long Position)'
    tightness: str = 'Medium'


class ChartEventResponse(BaseModel):
    """Schema for chart event API response matching notebook structure"""
    ticker: str
    event_id: Optional[str] = None
    event_type: Optional[str] = None
    event_name: Optional[str] = None
    price_period: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    target_price: Optional[float] = None
    start_price: Optional[float] = None
    end_price: Optional[float] = None
    is_active: bool = True


class TechnicalSummaryResponse(BaseModel):
    """Schema for technical summary API response matching notebook structure"""
    symbol: str
    name: Optional[str] = None
    exchange: Optional[str] = None
    isin: Optional[str] = None
    instrumentId: Optional[str] = None
    category: Optional[str] = None
    recommendation: Optional[str] = None
    signalStrength: Optional[float] = None


class HistoricalAnalystConsensusItem(BaseModel):
    """Schema for individual historical analyst consensus data point"""
    date: Optional[str] = None
    buy: Optional[int] = None
    hold: Optional[int] = None
    sell: Optional[int] = None
    consensus: Optional[str] = None
    priceTarget: Optional[float] = None


class HistoricalAnalystConsensusResponse(BaseModel):
    """Schema for historical analyst consensus API response"""
    ticker: str
    history: List[HistoricalAnalystConsensusItem] = []


class QuantamentalTimeseriesItem(BaseModel):
    """Schema for individual quantamental timeseries data point"""
    timestamp: Optional[str] = None
    score: Optional[float] = None


class QuantamentalTimeseriesResponse(BaseModel):
    """Schema for quantamental timeseries API response"""
    ticker: str
    timeseries: List[QuantamentalTimeseriesItem] = []
