"""
SQLAlchemy Models for Stock Analysis Data

This module contains all database models for storing stock analysis data including:
- Analyst Ratings
- News Sentiment
- Quantamental Scores
- Hedge Fund Data
- Crowd Statistics
- Blogger Sentiment
- Technical Indicators
- Target Prices
- Article Analytics
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean, 
    ForeignKey, Index, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class SentimentType(enum.Enum):
    """Enum for sentiment classification"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class RatingType(enum.Enum):
    """Enum for analyst rating types"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class TimeframeType(enum.Enum):
    """Enum for technical indicator timeframes"""
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    FOUR_HOURS = "4h"
    SIX_HOURS = "6h"
    TWELVE_HOURS = "12h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


class AnalystRating(Base):
    """
    Model for storing analyst ratings and recommendations
    
    Contains aggregated analyst ratings with buy/hold/sell counts
    and average price targets from professional analysts.
    """
    __tablename__ = "analyst_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Rating counts
    strong_buy_count = Column(Integer, default=0)
    buy_count = Column(Integer, default=0)
    hold_count = Column(Integer, default=0)
    sell_count = Column(Integer, default=0)
    strong_sell_count = Column(Integer, default=0)
    total_analysts = Column(Integer, default=0)
    
    # Consensus rating
    consensus_rating = Column(SQLEnum(RatingType), nullable=True)
    consensus_score = Column(Float, nullable=True)  # Numeric score (e.g., 1-5)
    
    # Price targets
    avg_price_target = Column(Float, nullable=True)
    high_price_target = Column(Float, nullable=True)
    low_price_target = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    upside_potential = Column(Float, nullable=True)  # Percentage upside
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)  # Store original API response
    
    __table_args__ = (
        Index('ix_analyst_ratings_ticker_timestamp', 'ticker', 'timestamp'),
    )


class NewsSentiment(Base):
    """
    Model for storing news sentiment analysis data
    
    Captures sentiment scores from news articles related to stocks.
    """
    __tablename__ = "news_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Sentiment metrics
    sentiment = Column(SQLEnum(SentimentType), nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1 to 1 scale
    buzz_score = Column(Float, nullable=True)  # News volume/attention score
    news_score = Column(Float, nullable=True)  # Overall news score
    
    # Article counts
    total_articles = Column(Integer, default=0)
    positive_articles = Column(Integer, default=0)
    negative_articles = Column(Integer, default=0)
    neutral_articles = Column(Integer, default=0)
    
    # Sector comparison
    sector_sentiment = Column(Float, nullable=True)
    sector_avg = Column(Float, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_news_sentiment_ticker_timestamp', 'ticker', 'timestamp'),
    )


class QuantamentalScore(Base):
    """
    Model for storing quantamental analysis scores
    
    Combines quantitative and fundamental analysis metrics
    into composite scores for stock evaluation.
    """
    __tablename__ = "quantamental_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Overall scores
    overall_score = Column(Float, nullable=True)  # 0-100 scale
    quality_score = Column(Float, nullable=True)
    value_score = Column(Float, nullable=True)
    growth_score = Column(Float, nullable=True)
    momentum_score = Column(Float, nullable=True)
    
    # Fundamental metrics
    revenue_growth = Column(Float, nullable=True)
    earnings_growth = Column(Float, nullable=True)
    profit_margin = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    return_on_equity = Column(Float, nullable=True)
    
    # Valuation metrics
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    ps_ratio = Column(Float, nullable=True)
    peg_ratio = Column(Float, nullable=True)
    ev_ebitda = Column(Float, nullable=True)
    
    # Ranking info
    sector_rank = Column(Integer, nullable=True)
    industry_rank = Column(Integer, nullable=True)
    overall_rank = Column(Integer, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_quantamental_scores_ticker_timestamp', 'ticker', 'timestamp'),
    )


class HedgeFundData(Base):
    """
    Model for storing hedge fund activity and holdings data
    
    Tracks institutional ownership, hedge fund positions, and trading activity.
    """
    __tablename__ = "hedge_fund_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Ownership metrics
    institutional_ownership_pct = Column(Float, nullable=True)
    hedge_fund_count = Column(Integer, default=0)
    total_shares_held = Column(Float, nullable=True)
    market_value_held = Column(Float, nullable=True)
    
    # Position changes
    new_positions = Column(Integer, default=0)
    increased_positions = Column(Integer, default=0)
    decreased_positions = Column(Integer, default=0)
    closed_positions = Column(Integer, default=0)
    
    # Sentiment indicators
    hedge_fund_sentiment = Column(SQLEnum(SentimentType), nullable=True)
    smart_money_score = Column(Float, nullable=True)  # 0-100 scale
    
    # Top holders info (JSON for flexibility)
    top_holders = Column(JSON, nullable=True)
    
    # Quarterly changes
    shares_change_qoq = Column(Float, nullable=True)
    ownership_change_qoq = Column(Float, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_hedge_fund_data_ticker_timestamp', 'ticker', 'timestamp'),
    )


class CrowdStatistics(Base):
    """
    Model for storing crowd sentiment and social statistics
    
    Captures retail investor sentiment from social media and forums.
    """
    __tablename__ = "crowd_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Sentiment metrics
    crowd_sentiment = Column(SQLEnum(SentimentType), nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1 to 1 scale
    
    # Social media metrics
    mentions_count = Column(Integer, default=0)
    mentions_change = Column(Float, nullable=True)  # Percentage change
    impressions = Column(Integer, default=0)
    engagement_rate = Column(Float, nullable=True)
    
    # Bullish/Bearish percentages
    bullish_percent = Column(Float, nullable=True)
    bearish_percent = Column(Float, nullable=True)
    neutral_percent = Column(Float, nullable=True)
    
    # Trending indicators
    trending_score = Column(Float, nullable=True)
    rank_day = Column(Integer, nullable=True)
    rank_week = Column(Integer, nullable=True)
    
    # Post/Message stats
    total_posts = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    avg_sentiment_post = Column(Float, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_crowd_statistics_ticker_timestamp', 'ticker', 'timestamp'),
    )


class BloggerSentiment(Base):
    """
    Model for storing blogger and influencer sentiment data
    
    Tracks opinions and sentiment from financial bloggers and influencers.
    """
    __tablename__ = "blogger_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Sentiment metrics
    blogger_sentiment = Column(SQLEnum(SentimentType), nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1 to 1 scale
    
    # Article/Post counts
    total_articles = Column(Integer, default=0)
    bullish_articles = Column(Integer, default=0)
    bearish_articles = Column(Integer, default=0)
    neutral_articles = Column(Integer, default=0)
    
    # Blogger metrics
    bullish_percent = Column(Float, nullable=True)
    bearish_percent = Column(Float, nullable=True)
    
    # Accuracy tracking (if available)
    avg_blogger_accuracy = Column(Float, nullable=True)
    top_blogger_opinion = Column(String(50), nullable=True)
    
    # Historical comparison
    sentiment_change_1d = Column(Float, nullable=True)
    sentiment_change_1w = Column(Float, nullable=True)
    sentiment_change_1m = Column(Float, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_blogger_sentiment_ticker_timestamp', 'ticker', 'timestamp'),
    )


class TechnicalIndicator(Base):
    """
    Model for storing technical analysis indicators
    
    Contains various technical indicators like RSI, MACD, moving averages, etc.
    """
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    timeframe = Column(SQLEnum(TimeframeType), nullable=False, index=True)
    
    # Price data
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    
    # Moving averages
    sma_20 = Column(Float, nullable=True)
    sma_50 = Column(Float, nullable=True)
    sma_200 = Column(Float, nullable=True)
    ema_12 = Column(Float, nullable=True)
    ema_26 = Column(Float, nullable=True)
    
    # Momentum indicators
    rsi_14 = Column(Float, nullable=True)  # Relative Strength Index
    stoch_k = Column(Float, nullable=True)  # Stochastic %K
    stoch_d = Column(Float, nullable=True)  # Stochastic %D
    cci = Column(Float, nullable=True)  # Commodity Channel Index
    williams_r = Column(Float, nullable=True)  # Williams %R
    
    # Trend indicators
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_histogram = Column(Float, nullable=True)
    adx = Column(Float, nullable=True)  # Average Directional Index
    plus_di = Column(Float, nullable=True)  # Positive Directional Indicator
    minus_di = Column(Float, nullable=True)  # Negative Directional Indicator
    
    # Volatility indicators
    atr = Column(Float, nullable=True)  # Average True Range
    bollinger_upper = Column(Float, nullable=True)
    bollinger_middle = Column(Float, nullable=True)
    bollinger_lower = Column(Float, nullable=True)
    
    # Support/Resistance levels
    support_1 = Column(Float, nullable=True)
    support_2 = Column(Float, nullable=True)
    resistance_1 = Column(Float, nullable=True)
    resistance_2 = Column(Float, nullable=True)
    pivot_point = Column(Float, nullable=True)
    
    # Signal summaries
    oscillator_signal = Column(SQLEnum(SentimentType), nullable=True)
    moving_avg_signal = Column(SQLEnum(SentimentType), nullable=True)
    overall_signal = Column(SQLEnum(SentimentType), nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_technical_indicators_ticker_timestamp', 'ticker', 'timestamp'),
        Index('ix_technical_indicators_ticker_timeframe', 'ticker', 'timeframe'),
    )


class TargetPrice(Base):
    """
    Model for storing analyst target price estimates
    
    Individual analyst price targets and recommendations.
    """
    __tablename__ = "target_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Analyst information
    analyst_name = Column(String(200), nullable=True)
    analyst_firm = Column(String(200), nullable=True)
    
    # Target price details
    target_price = Column(Float, nullable=True)
    previous_target = Column(Float, nullable=True)
    target_change = Column(Float, nullable=True)
    target_change_pct = Column(Float, nullable=True)
    
    # Rating information
    rating = Column(SQLEnum(RatingType), nullable=True)
    previous_rating = Column(SQLEnum(RatingType), nullable=True)
    rating_changed = Column(Boolean, default=False)
    
    # Price context
    current_price_at_rating = Column(Float, nullable=True)
    upside_to_target = Column(Float, nullable=True)  # Percentage
    
    # Confidence/accuracy
    analyst_accuracy_score = Column(Float, nullable=True)  # Historical accuracy
    
    # Timing
    rating_date = Column(DateTime, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_target_prices_ticker_timestamp', 'ticker', 'timestamp'),
        Index('ix_target_prices_analyst_firm', 'analyst_firm'),
    )


class ArticleAnalytics(Base):
    """
    Model for storing article-level analytics and metadata
    
    Detailed analytics for individual articles about stocks.
    """
    __tablename__ = "article_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Article identification - index for faster lookups, no unique constraint since nullable
    article_id = Column(String(100), nullable=True, index=True)
    article_url = Column(Text, nullable=True)
    article_title = Column(Text, nullable=True)
    
    # Author/Publisher info
    author = Column(String(200), nullable=True)
    publisher = Column(String(200), nullable=True)
    
    # Content metadata
    publish_date = Column(DateTime, nullable=True)
    word_count = Column(Integer, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Sentiment analysis
    sentiment = Column(SQLEnum(SentimentType), nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1 to 1 scale
    relevance_score = Column(Float, nullable=True)  # How relevant to ticker
    
    # Engagement metrics
    views = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    
    # Impact assessment
    price_impact = Column(Float, nullable=True)  # Price change after article
    volume_impact = Column(Float, nullable=True)  # Volume change after article
    
    # Additional metadata
    tags = Column(JSON, nullable=True)  # List of tags/keywords
    related_tickers = Column(JSON, nullable=True)  # Other mentioned tickers
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_article_analytics_ticker_timestamp', 'ticker', 'timestamp'),
        Index('ix_article_analytics_publish_date', 'publish_date'),
    )


class DataCollectionLog(Base):
    """
    Model for tracking data collection runs
    
    Logs each data collection event for monitoring and debugging.
    """
    __tablename__ = "data_collection_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Collection details
    ticker = Column(String(10), nullable=True, index=True)
    data_type = Column(String(50), nullable=False)  # e.g., 'analyst_rating', 'news_sentiment'
    
    # Status
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # Metrics
    records_collected = Column(Integer, default=0)
    duration_seconds = Column(Float, nullable=True)
    
    # Source information
    source = Column(String(100), nullable=True)
    api_endpoint = Column(String(500), nullable=True)
    
    __table_args__ = (
        Index('ix_data_collection_logs_timestamp_datatype', 'timestamp', 'data_type'),
    )
