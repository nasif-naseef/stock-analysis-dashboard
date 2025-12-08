"""
SQLAlchemy Models for Stock Analysis Data

This module contains all database models for storing stock analysis data including:
- Analyst Consensus and History
- News Sentiment
- Hedge Fund Data
- Insider Scores
- Crowd Statistics
- Blogger Sentiment
- Quantamental Scores
- Target Prices
- Article Distribution and Sentiment
- Support/Resistance Levels
- Stop Loss Recommendations
- Chart Events
- Technical Summaries
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
    MODERATE_BUY = "moderate_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    MODERATE_SELL = "moderate_sell"
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


class StopLossType(enum.Enum):
    """Enum for stop loss calculation types"""
    VOLATILITY_BASED = "Volatility-Based"
    CHART_BASED = "Chart-Based"


class StopLossDirection(enum.Enum):
    """Enum for stop loss direction"""
    BELOW_LONG = "Below (Long Position)"
    ABOVE_SHORT = "Above (Short Position)"


class StopLossTightness(enum.Enum):
    """Enum for stop loss tightness"""
    TIGHT = "Tight"
    MEDIUM = "Medium"
    LOOSE = "Loose"


class AnalystRating(Base):
    """
    Model for storing analyst ratings and recommendations (legacy)
    
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


class AnalystConsensus(Base):
    """
    Model for storing analyst consensus data matching notebook API structure.
    
    Fields match the response model exactly:
    - ticker, total_ratings, buy_ratings, hold_ratings, sell_ratings
    - consensus_recommendation, consensus_rating_score
    - price_target_high, price_target_low, price_target_average
    """
    __tablename__ = "analyst_consensus"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Rating counts
    total_ratings = Column(Integer, nullable=True)
    buy_ratings = Column(Integer, nullable=True)
    hold_ratings = Column(Integer, nullable=True)
    sell_ratings = Column(Integer, nullable=True)
    
    # Consensus
    consensus_recommendation = Column(String(50), nullable=True)  # e.g., "Moderate Buy"
    consensus_rating_score = Column(Float, nullable=True)
    
    # Price targets
    price_target_high = Column(Float, nullable=True)
    price_target_low = Column(Float, nullable=True)
    price_target_average = Column(Float, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_analyst_consensus_ticker_timestamp', 'ticker', 'timestamp'),
    )


class HistoricalAnalystConsensus(Base):
    """
    Model for storing historical analyst consensus data.
    
    Fields: date, buy, hold, sell, consensus, priceTarget
    """
    __tablename__ = "historical_analyst_consensus"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Historical data
    date = Column(String(50), nullable=True)
    buy = Column(Integer, nullable=True)
    hold = Column(Integer, nullable=True)
    sell = Column(Integer, nullable=True)
    consensus = Column(String(50), nullable=True)
    price_target = Column(Float, nullable=True)
    
    # Source metadata
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_historical_analyst_consensus_ticker_timestamp', 'ticker', 'timestamp'),
    )


class NewsSentiment(Base):
    """
    Model for storing news sentiment analysis data matching notebook API structure.
    
    Fields: ticker, stock_bullish_score, stock_bearish_score, 
            sector_bullish_score, sector_bearish_score
    """
    __tablename__ = "news_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Stock sentiment scores (from newsSentimentScore.stock)
    stock_bullish_score = Column(Float, nullable=True)
    stock_bearish_score = Column(Float, nullable=True)
    
    # Sector sentiment scores (from newsSentimentScore.sector)
    sector_bullish_score = Column(Float, nullable=True)
    sector_bearish_score = Column(Float, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_news_sentiment_ticker_timestamp', 'ticker', 'timestamp'),
    )


class QuantamentalScore(Base):
    """
    Model for storing quantamental analysis scores matching notebook API structure.
    
    Fields: ticker, overall, growth, value, income, quality, momentum
    """
    __tablename__ = "quantamental_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Notebook API fields
    overall = Column(Integer, nullable=True)
    growth = Column(Integer, nullable=True)
    value = Column(Integer, nullable=True)
    income = Column(Integer, nullable=True)
    quality = Column(Integer, nullable=True)
    momentum = Column(Integer, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_quantamental_scores_ticker_timestamp', 'ticker', 'timestamp'),
    )


class HedgeFundData(Base):
    """
    Model for storing hedge fund activity and holdings data matching notebook API structure.
    
    Fields: ticker, sentiment, trend_action, trend_value
    """
    __tablename__ = "hedge_fund_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Notebook API fields (from overview.hedgeFundData)
    sentiment = Column(Float, nullable=True)
    trend_action = Column(Integer, nullable=True)
    trend_value = Column(Integer, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_hedge_fund_data_ticker_timestamp', 'ticker', 'timestamp'),
    )


class InsiderScore(Base):
    """
    Model for storing insider confidence/score data matching notebook API structure.
    
    Fields: ticker, stock_score, sector_score, score
    """
    __tablename__ = "insider_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Insider score fields (from overview.insidrConfidenceSignal)
    stock_score = Column(Float, nullable=True)
    sector_score = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_insider_scores_ticker_timestamp', 'ticker', 'timestamp'),
    )


class CrowdStatistics(Base):
    """
    Model for storing crowd sentiment and social statistics (legacy).
    """
    __tablename__ = "crowd_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Sentiment metrics
    crowd_sentiment = Column(SQLEnum(SentimentType), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    
    # Social media metrics
    mentions_count = Column(Integer, default=0)
    mentions_change = Column(Float, nullable=True)
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


class CrowdStats(Base):
    """
    Model for storing crowd statistics matching notebook API structure.
    
    Fields: ticker, portfolio_holding, amount_of_portfolios, amount_of_public_portfolios,
            percent_allocated, based_on_portfolios, percent_over_last_7d, percent_over_last_30d,
            score, individual_sector_average, frequency
    """
    __tablename__ = "crowd_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    stats_type = Column(String(20), nullable=True)  # 'all', 'individual', 'institution'
    
    # Notebook API fields (from generalStats{type})
    portfolio_holding = Column(Integer, default=0)
    amount_of_portfolios = Column(Integer, default=0)
    amount_of_public_portfolios = Column(Integer, default=0)
    percent_allocated = Column(Float, default=0.0)
    based_on_portfolios = Column(Integer, default=0)
    percent_over_last_7d = Column(Float, default=0.0)
    percent_over_last_30d = Column(Float, default=0.0)
    score = Column(Float, default=0.0)
    individual_sector_average = Column(Float, default=0.0)
    frequency = Column(Float, default=0.0)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_crowd_stats_ticker_timestamp', 'ticker', 'timestamp'),
    )


class BloggerSentiment(Base):
    """
    Model for storing blogger sentiment matching notebook API structure.
    
    Fields: ticker, bearish, neutral, bullish, bearish_count, neutral_count,
            bullish_count, score, avg
    """
    __tablename__ = "blogger_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Notebook API fields (from bloggerSentiment)
    bearish = Column(Integer, default=0)
    neutral = Column(Integer, default=0)
    bullish = Column(Integer, default=0)
    bearish_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    bullish_count = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    avg = Column(Float, default=0.0)
    
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
    Model for storing target price data matching notebook API structure.
    
    Fields: ticker, close_price, target_price, target_date, last_updated
    """
    __tablename__ = "target_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Notebook API fields
    close_price = Column(Float, nullable=True)
    target_price = Column(Float, nullable=True)
    target_date = Column(String(100), nullable=True)
    last_updated = Column(String(100), nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_target_prices_ticker_timestamp', 'ticker', 'timestamp'),
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


class ArticleDistribution(Base):
    """
    Model for storing article distribution data matching notebook API structure.
    
    Fields: ticker, total_articles, news_count, news_percentage,
            social_count, social_percentage, web_count, web_percentage
    """
    __tablename__ = "article_distribution"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Article counts and percentages
    total_articles = Column(Integer, default=0)
    news_count = Column(Integer, default=0)
    news_percentage = Column(Float, default=0.0)
    social_count = Column(Integer, default=0)
    social_percentage = Column(Float, default=0.0)
    web_count = Column(Integer, default=0)
    web_percentage = Column(Float, default=0.0)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_article_distribution_ticker_timestamp', 'ticker', 'timestamp'),
    )


class ArticleSentiment(Base):
    """
    Model for storing article sentiment data matching notebook API structure.
    
    Fields: ticker, sentiment_id, sentiment_label, sentiment_value,
            subjectivity_id, subjectivity_label, subjectivity_value,
            confidence_id, confidence_name
    """
    __tablename__ = "article_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Sentiment data
    sentiment_id = Column(String(50), nullable=True)
    sentiment_label = Column(String(50), nullable=True)
    sentiment_value = Column(Integer, nullable=True)
    
    # Subjectivity data
    subjectivity_id = Column(String(50), nullable=True)
    subjectivity_label = Column(String(50), nullable=True)
    subjectivity_value = Column(Integer, nullable=True)
    
    # Confidence data
    confidence_id = Column(String(50), nullable=True)
    confidence_name = Column(String(50), nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_article_sentiment_ticker_timestamp', 'ticker', 'timestamp'),
    )


class SupportResistance(Base):
    """
    Model for storing support/resistance levels matching notebook API structure.
    
    Fields: symbol, date, exchange, support_10, resistance_10, support_20, resistance_20,
            support_40, resistance_40, support_100, resistance_100, support_250, resistance_250,
            support_500, resistance_500
    """
    __tablename__ = "support_resistance"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Date and exchange
    date = Column(String(50), nullable=True)
    exchange = Column(String(50), nullable=True)
    
    # Support/Resistance levels for different periods
    support_10 = Column(Float, nullable=True)
    resistance_10 = Column(Float, nullable=True)
    support_20 = Column(Float, nullable=True)
    resistance_20 = Column(Float, nullable=True)
    support_40 = Column(Float, nullable=True)
    resistance_40 = Column(Float, nullable=True)
    support_100 = Column(Float, nullable=True)
    resistance_100 = Column(Float, nullable=True)
    support_250 = Column(Float, nullable=True)
    resistance_250 = Column(Float, nullable=True)
    support_500 = Column(Float, nullable=True)
    resistance_500 = Column(Float, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_support_resistance_symbol_timestamp', 'symbol', 'timestamp'),
    )


class StopLoss(Base):
    """
    Model for storing stop loss recommendations matching notebook API structure.
    
    Fields: ticker, recommended_stop_price, calculation_timestamp,
            stop_type, direction, tightness
    """
    __tablename__ = "stop_loss"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Stop loss data
    recommended_stop_price = Column(Float, nullable=True)
    calculation_timestamp = Column(String(100), nullable=True)
    stop_type = Column(String(50), default='Volatility-Based')
    direction = Column(String(50), default='Below (Long Position)')
    tightness = Column(String(50), default='Medium')
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_stop_loss_ticker_timestamp', 'ticker', 'timestamp'),
    )


class ChartEvent(Base):
    """
    Model for storing chart events matching notebook API structure.
    
    Fields: ticker, event_id, event_type, event_name, price_period,
            start_date, end_date, target_price, start_price, end_price, is_active
    """
    __tablename__ = "chart_events"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Event identification
    event_id = Column(String(100), nullable=True)
    event_type = Column(String(100), nullable=True)
    event_name = Column(String(200), nullable=True)
    price_period = Column(String(50), nullable=True)
    
    # Event dates
    start_date = Column(String(100), nullable=True)
    end_date = Column(String(100), nullable=True)
    
    # Price data
    target_price = Column(Float, nullable=True)
    start_price = Column(Float, nullable=True)
    end_price = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_chart_events_ticker_timestamp', 'ticker', 'timestamp'),
        Index('ix_chart_events_is_active', 'is_active'),
    )


class TechnicalSummary(Base):
    """
    Model for storing technical summaries matching notebook API structure.
    
    Fields: symbol, name, exchange, isin, instrumentId, category,
            recommendation, signalStrength
    """
    __tablename__ = "technical_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Instrument identification
    name = Column(String(200), nullable=True)
    exchange = Column(String(50), nullable=True)
    isin = Column(String(50), nullable=True)
    instrument_id = Column(String(100), nullable=True)
    
    # Technical analysis
    category = Column(String(100), nullable=True)
    recommendation = Column(String(100), nullable=True)
    signal_strength = Column(Float, nullable=True)
    
    # Source metadata
    source = Column(String(100), nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_technical_summaries_symbol_timestamp', 'symbol', 'timestamp'),
    )
