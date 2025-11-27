"""
API Schemas for REST API Endpoints

This module contains Pydantic models for API request/response validation
for historical data, comparisons, dashboard, and collection endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ============================================
# Enums
# ============================================

class DataType(str, Enum):
    """Supported data types for historical and comparison queries"""
    ANALYST_RATINGS = "analyst_ratings"
    NEWS_SENTIMENT = "news_sentiment"
    QUANTAMENTAL_SCORES = "quantamental_scores"
    HEDGE_FUND_DATA = "hedge_fund_data"
    CROWD_STATISTICS = "crowd_statistics"
    BLOGGER_SENTIMENT = "blogger_sentiment"
    TECHNICAL_INDICATORS = "technical_indicators"


class TrendDirection(str, Enum):
    """Trend direction enum"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    UNKNOWN = "unknown"


class AlertType(str, Enum):
    """Alert type enum"""
    RATING_CHANGE = "rating_change"
    SENTIMENT_SHIFT = "sentiment_shift"
    PRICE_TARGET_CHANGE = "price_target_change"
    HEDGE_FUND_ACTIVITY = "hedge_fund_activity"
    TRENDING = "trending"
    UNUSUAL_VOLUME = "unusual_volume"


class AlertSeverity(str, Enum):
    """Alert severity enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================
# Request Schemas
# ============================================

class HistoricalDataQuery(BaseModel):
    """Query parameters for historical data endpoint"""
    hours_ago: int = Field(default=24, ge=1, le=8760, description="Hours in the past to fetch data (max 1 year)")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")

    @field_validator('hours_ago')
    @classmethod
    def validate_hours(cls, v: int) -> int:
        if v < 1:
            raise ValueError('hours_ago must be at least 1')
        return v


class ComparisonQuery(BaseModel):
    """Query parameters for comparison endpoint"""
    periods: str = Field(
        default="1h,4h,1d,1w",
        description="Comma-separated list of periods (e.g., 1h,4h,1d,1w)",
        examples=["1h,4h,1d,1w"]
    )
    data_type: Optional[DataType] = Field(
        default=None,
        description="Optional specific data type to compare. If not provided, all types are compared."
    )

    @field_validator('periods')
    @classmethod
    def validate_periods(cls, v: str) -> str:
        periods = [p.strip() for p in v.split(',')]
        valid_suffixes = ('h', 'd', 'w', 'm')
        for period in periods:
            period_lower = period.lower()
            if not any(period_lower.endswith(s) for s in valid_suffixes):
                raise ValueError(f"Invalid period format: {period}. Use formats like 1h, 4h, 1d, 1w")
            # Check if the numeric part is valid
            try:
                int(period_lower[:-1])
            except ValueError:
                raise ValueError(f"Invalid period format: {period}")
        return v


class MultiTickerComparisonQuery(BaseModel):
    """Query parameters for multi-ticker comparison endpoint"""
    tickers: str = Field(
        ...,
        description="Comma-separated list of tickers (e.g., AAPL,TSLA,NVDA)",
        examples=["AAPL,TSLA,NVDA"]
    )
    period: str = Field(
        default="1d",
        description="Period for comparison (e.g., 1h, 4h, 1d, 1w)",
        examples=["1d"]
    )
    data_type: DataType = Field(
        default=DataType.ANALYST_RATINGS,
        description="Data type to compare"
    )

    @field_validator('tickers')
    @classmethod
    def validate_tickers(cls, v: str) -> str:
        tickers = [t.strip().upper() for t in v.split(',')]
        if len(tickers) < 2:
            raise ValueError('At least 2 tickers are required for comparison')
        if len(tickers) > 10:
            raise ValueError('Maximum 10 tickers allowed for comparison')
        return v

    @field_validator('period')
    @classmethod
    def validate_period(cls, v: str) -> str:
        v = v.strip().lower()
        valid_suffixes = ('h', 'd', 'w', 'm')
        if not any(v.endswith(s) for s in valid_suffixes):
            raise ValueError(f"Invalid period format: {v}. Use formats like 1h, 4h, 1d, 1w")
        return v


class CollectTickerRequest(BaseModel):
    """Request body for triggering collection for a specific ticker"""
    ticker: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Stock ticker symbol (optional - if not provided, collects for all tickers)"
    )

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().upper()
            if not v.isalnum():
                raise ValueError('Ticker must be alphanumeric')
        return v


class AlertsQuery(BaseModel):
    """Query parameters for alerts endpoint"""
    hours_ago: int = Field(default=24, ge=1, le=168, description="Hours to look back for alerts (max 1 week)")
    severity: Optional[AlertSeverity] = Field(default=None, description="Filter by alert severity")


# ============================================
# Response Schemas
# ============================================

class ChangeMetrics(BaseModel):
    """Metrics for a single value change"""
    old_value: Optional[float] = None
    new_value: Optional[float] = None
    absolute_change: Optional[float] = None
    percentage_change: Optional[float] = None
    trend: TrendDirection = TrendDirection.UNKNOWN


class PeriodComparison(BaseModel):
    """Comparison data for a single period"""
    period: str
    hours_ago: int
    data_timestamp: Optional[str] = None
    metrics: Dict[str, ChangeMetrics]


class TickerComparisonResponse(BaseModel):
    """Response for single ticker comparison"""
    ticker: str
    data_type: str
    current_timestamp: Optional[str] = None
    periods: Dict[str, PeriodComparison]


class MultiTickerComparisonResponse(BaseModel):
    """Response for multi-ticker comparison"""
    data_type: str
    period: str
    hours_ago: int
    tickers: Dict[str, Dict[str, Any]]


class AlertResponse(BaseModel):
    """Single alert response"""
    ticker: str
    type: AlertType
    severity: AlertSeverity
    timestamp: Optional[str] = None
    message: str
    data: Dict[str, Any]


class AlertsListResponse(BaseModel):
    """Response for alerts list"""
    timestamp: str
    hours_ago: int
    total_alerts: int
    alerts: List[Dict[str, Any]]


class TickerOverview(BaseModel):
    """Overview data for a single ticker"""
    ticker: str
    analyst_rating: Dict[str, Any] = Field(default_factory=dict)
    news_sentiment: Dict[str, Any] = Field(default_factory=dict)
    quantamental_score: Dict[str, Any] = Field(default_factory=dict)
    hedge_fund_data: Dict[str, Any] = Field(default_factory=dict)
    crowd_statistics: Dict[str, Any] = Field(default_factory=dict)
    blogger_sentiment: Dict[str, Any] = Field(default_factory=dict)


class DashboardSummary(BaseModel):
    """Summary statistics for dashboard"""
    bullish_count: int = 0
    bearish_count: int = 0
    neutral_count: int = 0
    avg_sentiment: Optional[float] = None


class DashboardOverviewResponse(BaseModel):
    """Response for dashboard overview"""
    timestamp: str
    total_tickers: int
    tickers: Dict[str, TickerOverview]
    summary: DashboardSummary


class CollectionStatusResponse(BaseModel):
    """Response for collection status"""
    running: bool
    jobs: List[Dict[str, Any]]
    last_collection_time: Optional[str] = None
    last_collection_result: Optional[Dict[str, Any]] = None
    collection_interval_hours: int


class CollectionTriggerResponse(BaseModel):
    """Response for collection trigger"""
    status: str
    message: str
    check_status_at: str


class CollectionResultResponse(BaseModel):
    """Response for collection result"""
    ticker: str
    timestamp: str
    data_types: Dict[str, Dict[str, Any]]
    summary: Dict[str, Any]


class HistoricalDataItem(BaseModel):
    """Single historical data item"""
    id: int
    ticker: str
    timestamp: str
    data: Dict[str, Any]


class HistoricalDataResponse(BaseModel):
    """Response for historical data endpoint"""
    ticker: str
    data_type: str
    hours_ago: int
    count: int
    items: List[Dict[str, Any]]


class CollectionSummaryResponse(BaseModel):
    """Response for collection summary"""
    timestamp: str
    hours_ago: int
    total_collections: int
    successful: int
    failed: int
    success_rate: float
    total_records_collected: int
    latest_collections: Dict[str, Dict[str, Any]]


# ============================================
# Error Responses
# ============================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "Validation Error"
    detail: List[Dict[str, Any]]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
