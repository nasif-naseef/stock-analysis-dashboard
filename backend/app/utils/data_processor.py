"""
Data Processor Utilities

This module contains classes for data processing and transformation including:
- ResponseBuilder for parsing and validating API responses
- DataFrameOptimizer for memory optimization (if needed)
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from app.utils.helpers import (
    safe_get, safe_float, safe_int, get_utc_now
)
from app.models.stock_data import SentimentType, RatingType, TimeframeType

logger = logging.getLogger(__name__)


def determine_sentiment(score: Optional[float]) -> Optional[SentimentType]:
    """
    Determine sentiment type from a numeric score.
    
    Args:
        score: Sentiment score (-1 to 1 or 0 to 100)
        
    Returns:
        SentimentType enum value
    """
    if score is None:
        return None
    
    # Handle 0-100 scale
    if score > 1:
        score = (score - 50) / 50  # Convert to -1 to 1
    
    if score > 0.2:
        return SentimentType.BULLISH
    elif score < -0.2:
        return SentimentType.BEARISH
    else:
        return SentimentType.NEUTRAL


def determine_rating(
    buy_count: int,
    hold_count: int,
    sell_count: int,
    score: Optional[float] = None
) -> Optional[RatingType]:
    """
    Determine consensus rating from analyst counts.
    
    Args:
        buy_count: Number of buy/strong buy ratings
        hold_count: Number of hold ratings
        sell_count: Number of sell/strong sell ratings
        score: Optional consensus score (1-5 scale)
        
    Returns:
        RatingType enum value
    """
    if score is not None:
        if score >= 4.5:
            return RatingType.STRONG_BUY
        elif score >= 3.5:
            return RatingType.BUY
        elif score >= 2.5:
            return RatingType.HOLD
        elif score >= 1.5:
            return RatingType.SELL
        else:
            return RatingType.STRONG_SELL
    
    total = buy_count + hold_count + sell_count
    if total == 0:
        return None
    
    if buy_count > hold_count and buy_count > sell_count:
        if buy_count > total * 0.7:
            return RatingType.STRONG_BUY
        return RatingType.BUY
    elif sell_count > hold_count:
        if sell_count > total * 0.7:
            return RatingType.STRONG_SELL
        return RatingType.SELL
    else:
        return RatingType.HOLD


class ResponseBuilder:
    """
    Builder class for parsing API responses matching notebook structure.
    
    All methods match the exact JSON paths from the Jupyter notebook (Final.ipynb).
    Legacy methods with different field names have been removed.
    """

    def build_analyst_consensus(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build analyst consensus data matching notebook API structure.
        
        Extracts from: analystConsensus, analystPriceTarget
        
        Args:
            raw_data: Raw API response from TipRanks
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed analyst consensus fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            ac = raw_data.get('analystConsensus', {}) or {}
            apt = raw_data.get('analystPriceTarget', {}) or {}
            
            return {
                "ticker": ticker,
                "total_ratings": safe_int(ac.get('numberOfAnalystRatings')),
                "buy_ratings": safe_int(ac.get('buy')),
                "hold_ratings": safe_int(ac.get('hold')),
                "sell_ratings": safe_int(ac.get('sell')),
                "consensus_recommendation": ac.get('consensus'),
                "consensus_rating_score": safe_float(ac.get('consensusRating')),
                "price_target_high": safe_float(apt.get('high')),
                "price_target_low": safe_float(apt.get('low')),
                "price_target_average": safe_float(apt.get('average')),
            }
        except Exception as e:
            logger.error(f"Error building analyst consensus: {e}")
            raise

    def build_news_sentiment(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build news sentiment data matching notebook API structure.
        
        Extracts from: newsSentimentScore.stock, newsSentimentScore.sector
        
        Args:
            raw_data: Raw API response from TipRanks
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed news sentiment fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            sentiment_data = raw_data.get('newsSentimentScore', {}) or {}
            stock_data = sentiment_data.get('stock', {}) or {}
            sector_data = sentiment_data.get('sector', {}) or {}
            
            return {
                "ticker": ticker,
                "stock_bullish_score": safe_float(stock_data.get('bullishPercent')),
                "stock_bearish_score": safe_float(stock_data.get('bearishPercent')),
                "sector_bullish_score": safe_float(sector_data.get('bullishPercent')),
                "sector_bearish_score": safe_float(sector_data.get('bearishPercent')),
            }
        except Exception as e:
            logger.error(f"Error building news sentiment: {e}")
            raise

    def build_hedge_fund(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build hedge fund data matching notebook API structure.
        
        Extracts from: overview.hedgeFundData
        
        Args:
            raw_data: Raw API response from TipRanks
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed hedge fund fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            hedge_fund_data = raw_data.get('overview', {}).get('hedgeFundData', {}) or {}
            
            return {
                "ticker": ticker,
                "sentiment": safe_float(hedge_fund_data.get('sentiment')),
                "trend_action": safe_int(hedge_fund_data.get('trendAction')),
                "trend_value": safe_int(hedge_fund_data.get('trendValue')),
            }
        except Exception as e:
            logger.error(f"Error building hedge fund: {e}")
            raise

    def build_insider_score(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build insider score data matching notebook API structure.
        
        Extracts from: overview.insidrConfidenceSignal
        
        Args:
            raw_data: Raw API response from TipRanks
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed insider score fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            insider_data = raw_data.get('overview', {}).get('insidrConfidenceSignal', {}) or {}
            
            return {
                "ticker": ticker,
                "stock_score": safe_float(insider_data.get('stockScore')),
                "sector_score": safe_float(insider_data.get('sectorScore')),
                "score": safe_float(insider_data.get('score')),
            }
        except Exception as e:
            logger.error(f"Error building insider score: {e}")
            raise

    def build_crowd_stats(
        self,
        raw_data: Dict[str, Any],
        ticker: str,
        stats_type: str = 'all'
    ) -> Dict[str, Any]:
        """
        Build crowd statistics matching notebook API structure.
        
        Extracts from: generalStats{statsType.capitalize()}
        
        Args:
            raw_data: Raw API response from TipRanks
            ticker: Stock ticker symbol
            stats_type: Type of stats ('all', 'individual', 'institution')
            
        Returns:
            Dictionary with parsed crowd stats fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            key = f'generalStats{stats_type.capitalize()}'
            stats_data = raw_data.get(key, {}) or {}
            
            return {
                "ticker": ticker,
                "portfolio_holding": safe_int(stats_data.get('portfoliosHolding', 0)) or 0,
                "amount_of_portfolios": safe_int(stats_data.get('amountOfPortfolios', 0)) or 0,
                "amount_of_public_portfolios": safe_int(stats_data.get('amountOfPublicPortfolios', 0)) or 0,
                "percent_allocated": safe_float(stats_data.get('percentAllocated', 0.0)) or 0.0,
                "based_on_portfolios": safe_int(stats_data.get('basedOnPortfolios', 0)) or 0,
                "percent_over_last_7d": safe_float(stats_data.get('percentOverLast7Days', 0.0)) or 0.0,
                "percent_over_last_30d": safe_float(stats_data.get('percentOverLast30Days', 0.0)) or 0.0,
                "score": safe_float(stats_data.get('score', 0.0)) or 0.0,
                "individual_sector_average": safe_float(stats_data.get('individualSectorAverage', 0.0)) or 0.0,
                "frequency": safe_float(stats_data.get('frequency', 0.0)) or 0.0,
            }
        except Exception as e:
            logger.error(f"Error building crowd stats: {e}")
            raise

    def build_blogger_sentiment(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build blogger sentiment matching notebook API structure.
        
        Extracts from: bloggerSentiment
        
        Args:
            raw_data: Raw API response from TipRanks
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed blogger sentiment fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            blogger_data = raw_data.get('bloggerSentiment', {}) or {}
            
            return {
                "ticker": ticker,
                "bearish": safe_int(blogger_data.get('bearish', 0)) or 0,
                "neutral": safe_int(blogger_data.get('neutral', 0)) or 0,
                "bullish": safe_int(blogger_data.get('bullish', 0)) or 0,
                "bearish_count": safe_int(blogger_data.get('bearishCount', 0)) or 0,
                "neutral_count": safe_int(blogger_data.get('neutralCount', 0)) or 0,
                "bullish_count": safe_int(blogger_data.get('bullishCount', 0)) or 0,
                "score": safe_float(blogger_data.get('score', 0.0)) or 0.0,
                "avg": safe_float(blogger_data.get('avg', 0.0)) or 0.0,
            }
        except Exception as e:
            logger.error(f"Error building blogger sentiment: {e}")
            raise

    def build_quantamental(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build quantamental scores matching notebook API structure.
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed quantamental fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            raw_data = raw_data or {}
            
            return {
                "ticker": ticker,
                "overall": safe_int(raw_data.get('quantamental')),
                "growth": safe_int(raw_data.get('growth')),
                "value": safe_int(raw_data.get('valuation')),
                "income": safe_int(raw_data.get('income')),
                "quality": safe_int(raw_data.get('quality')),
                "momentum": safe_int(raw_data.get('momentum')),
            }
        except Exception as e:
            logger.error(f"Error building quantamental: {e}")
            raise

    def build_analyst_consensus_history(
        self,
        raw_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Build analyst consensus history from API response.
        
        Extracts from: analystConsensusHistory
        
        Args:
            raw_data: Raw API response
            
        Returns:
            List of dictionaries with historical consensus data
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            history = raw_data.get('analystConsensusHistory', []) or []
            return history
        except Exception as e:
            logger.error(f"Error building analyst consensus history: {e}")
            raise

    def build_target_price(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build target price data matching notebook API structure.
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed target price fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            raw_data = raw_data or {}
            
            return {
                "ticker": ticker,
                "close_price": safe_float(raw_data.get('closePrice')),
                "target_price": safe_float(raw_data.get('targetPrice')),
                "target_date": raw_data.get('targetDate'),
                "last_updated": raw_data.get('lastUpdated'),
            }
        except Exception as e:
            logger.error(f"Error building target price: {e}")
            raise

    def build_article_distribution(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build article distribution data matching notebook API structure.
        
        Extracts from: topics using pandas DataFrame for summing columns
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed article distribution fields
        """
        try:
            import pandas as pd
            
            topics = raw_data.get('topics', []) or []
            if not topics:
                return {
                    "ticker": ticker,
                    "total_articles": 0,
                    "news_count": 0,
                    "news_percentage": 0,
                    "social_count": 0,
                    "social_percentage": 0,
                    "web_count": 0,
                    "web_percentage": 0,
                }

            topics_df = pd.DataFrame(topics)
            news_count = int(topics_df['news'].sum()) if 'news' in topics_df.columns else 0
            social_count = int(topics_df['social'].sum()) if 'social' in topics_df.columns else 0
            web_count = int(topics_df['web'].sum()) if 'web' in topics_df.columns else 0
            total_count = int(topics_df['total'].sum()) if 'total' in topics_df.columns else 0

            return {
                "ticker": ticker,
                "total_articles": total_count,
                "news_count": news_count,
                "news_percentage": (news_count / total_count * 100) if total_count > 0 else 0,
                "social_count": social_count,
                "social_percentage": (social_count / total_count * 100) if total_count > 0 else 0,
                "web_count": web_count,
                "web_percentage": (web_count / total_count * 100) if total_count > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error building article distribution: {e}")
            raise

    def build_blogger_article_distribution(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build blogger article distribution data matching notebook API structure.
        
        Extracts from: bloggerArticleDistribution (list of dicts with sentiment and counts)
        
        Args:
            raw_data: Raw API response from TipRanks bloggers endpoint
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed blogger article distribution fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            distribution = raw_data.get('bloggerArticleDistribution', []) or []
            
            # Process the distribution data using DataFrameOptimizer
            df = DataFrameOptimizer.process_batch(distribution)
            
            # Calculate totals
            total_articles = 0
            bullish_count = 0
            neutral_count = 0
            bearish_count = 0
            
            if not df.empty and 'sentiment' in df.columns and 'count' in df.columns:
                for _, row in df.iterrows():
                    sentiment = str(row['sentiment']).lower()
                    count = int(row.get('count', 0)) if row.get('count') else 0
                    total_articles += count
                    
                    if 'bullish' in sentiment or sentiment == '1':
                        bullish_count = count
                    elif 'neutral' in sentiment or sentiment == '0':
                        neutral_count = count
                    elif 'bearish' in sentiment or sentiment == '-1':
                        bearish_count = count
            
            return {
                "ticker": ticker,
                "total_articles": total_articles,
                "bullish_count": bullish_count,
                "bullish_percentage": (bullish_count / total_articles * 100) if total_articles > 0 else 0,
                "neutral_count": neutral_count,
                "neutral_percentage": (neutral_count / total_articles * 100) if total_articles > 0 else 0,
                "bearish_count": bearish_count,
                "bearish_percentage": (bearish_count / total_articles * 100) if total_articles > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error building blogger article distribution: {e}")
            raise

    def build_article_sentiment(
        self,
        sentiment_responses: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build article sentiment data matching notebook API structure.
        
        Handles sentiment, subjectivity, confidence fields from separate response arrays
        
        Args:
            sentiment_responses: Dict containing 'sentiment', 'subjectivity', 'confidence' arrays
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed article sentiment fields
        """
        try:
            sentiment_id = sentiment_label = sentiment_value = None
            subjectivity_id = subjectivity_label = subjectivity_value = None
            confidence_id = confidence_name = None

            if sentiment_responses.get('sentiment') and len(sentiment_responses['sentiment']) > 0:
                sentiment_data = sentiment_responses['sentiment'][0].get('sentiment', {}) or {}
                if sentiment_data:
                    sentiment_id = sentiment_data.get('id')
                    sentiment_label = sentiment_data.get('label')
                    sentiment_value = sentiment_data.get('value')

            if sentiment_responses.get('subjectivity') and len(sentiment_responses['subjectivity']) > 0:
                subjectivity_data = sentiment_responses['subjectivity'][0].get('subjectivity', {}) or {}
                if subjectivity_data:
                    subjectivity_id = subjectivity_data.get('id')
                    subjectivity_label = subjectivity_data.get('label')
                    subjectivity_value = subjectivity_data.get('value')

            if sentiment_responses.get('confidence') and len(sentiment_responses['confidence']) > 0:
                confidence_data = sentiment_responses['confidence'][0].get('confidence', {}) or {}
                if confidence_data:
                    confidence_id = confidence_data.get('id')
                    confidence_name = confidence_data.get('name')

            return {
                "ticker": ticker,
                "sentiment_id": sentiment_id,
                "sentiment_label": sentiment_label,
                "sentiment_value": sentiment_value,
                "subjectivity_id": subjectivity_id,
                "subjectivity_label": subjectivity_label,
                "subjectivity_value": subjectivity_value,
                "confidence_id": confidence_id,
                "confidence_name": confidence_name,
            }
        except Exception as e:
            logger.error(f"Error building article sentiment: {e}")
            raise

    def build_support_resistance(
        self,
        raw_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build support/resistance data matching notebook API structure.
        
        Extracts from: instrument, support, resistance data
        
        Args:
            raw_item: Raw API response item
            
        Returns:
            Dictionary with parsed support/resistance fields
        """
        try:
            raw_item = raw_item or {}
            
            instrument = raw_item.get('instrument', {}) or {}
            support_data = raw_item.get('support', {}) or {}
            resistance_data = raw_item.get('resistance', {}) or {}
            
            return {
                "symbol": instrument.get('symbol', 'N/A'),
                "date": raw_item.get('date', 'N/A'),
                "exchange": instrument.get('exchange', 'N/A'),
                "support_10": safe_float(support_data.get('support10')),
                "resistance_10": safe_float(resistance_data.get('resistance10')),
                "support_20": safe_float(support_data.get('support20')),
                "resistance_20": safe_float(resistance_data.get('resistance20')),
                "support_40": safe_float(support_data.get('support40')),
                "resistance_40": safe_float(resistance_data.get('resistance40')),
                "support_100": safe_float(support_data.get('support100')),
                "resistance_100": safe_float(resistance_data.get('resistance100')),
                "support_250": safe_float(support_data.get('support250')),
                "resistance_250": safe_float(resistance_data.get('resistance250')),
                "support_500": safe_float(support_data.get('support500')),
                "resistance_500": safe_float(resistance_data.get('resistance500')),
            }
        except Exception as e:
            logger.error(f"Error building support resistance: {e}")
            raise

    def build_stop_loss(
        self,
        raw_data: Dict[str, Any],
        ticker: str,
        stop_type: str = 'Volatility-Based',
        direction: str = 'Below (Long Position)',
        tightness: str = 'Medium'
    ) -> Dict[str, Any]:
        """
        Build stop loss data matching notebook API structure.
        
        Extracts from: stops, timestamps arrays - uses first element [0]
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            stop_type: Type of stop loss
            direction: Direction of stop
            tightness: Tightness level
            
        Returns:
            Dictionary with parsed stop loss fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            raw_data = raw_data or {}
            
            stops = raw_data.get('stops', [])
            timestamps = raw_data.get('timestamps', [])
            
            recommended_stop = None
            calculation_timestamp = None
            
            if stops and len(stops) > 0:
                recommended_stop = safe_float(stops[0])
            if timestamps and len(timestamps) > 0:
                calculation_timestamp = timestamps[0]
            
            return {
                "ticker": ticker,
                "recommended_stop_price": recommended_stop,
                "calculation_timestamp": calculation_timestamp,
                "stop_type": stop_type,
                "direction": direction,
                "tightness": tightness,
            }
        except Exception as e:
            logger.error(f"Error building stop loss: {e}")
            raise

    def build_chart_events_dataframe(
        self,
        raw_data: Dict[str, Any],
        ticker: str,
        is_active: bool = True
    ) -> Any:
        """
        Build chart events DataFrame matching notebook API structure.
        
        Checks for 'events' key, flattens nested columns
        
        Args:
            raw_data: Raw API response dict with 'events' key
            ticker: Stock ticker symbol
            is_active: Whether these are active events
            
        Returns:
            pandas DataFrame with flattened chart event data
        """
        try:
            import pandas as pd
            
            if not raw_data or 'events' not in raw_data:
                return pd.DataFrame()

            events_raw = raw_data['events']
            if not events_raw:
                return pd.DataFrame()

            events_df = DataFrameOptimizer.process_batch(events_raw)

            # Flatten nested columns
            if 'dates' in events_df.columns:
                events_df = DataFrameOptimizer.flatten_nested_columns(events_df, 'dates', 'date_')
            if 'endPrices' in events_df.columns:
                events_df = DataFrameOptimizer.flatten_nested_columns(events_df, 'endPrices', 'endPrice_')
            if 'eventType' in events_df.columns:
                events_df = DataFrameOptimizer.flatten_nested_columns(events_df, 'eventType', 'eventType_')
            if 'targetPrice' in events_df.columns:
                events_df = DataFrameOptimizer.flatten_nested_columns(events_df, 'targetPrice', 'targetPrice_')

            if not events_df.empty:
                events_df['ticker'] = ticker
                events_df['is_active'] = is_active
                events_df = DataFrameOptimizer.optimize_memory(events_df)

            return events_df
        except ImportError:
            logger.warning("pandas not available for chart events dataframe")
            return []
        except Exception as e:
            logger.error(f"Error building chart events dataframe: {e}")
            raise

    def build_technical_summaries_dataframe(
        self,
        raw_data: Dict[str, Any]
    ) -> Any:
        """
        Build technical summaries DataFrame matching notebook API structure.
        
        Extracts from scores with multiple categories per instrument
        
        Args:
            raw_data: Raw API response
            
        Returns:
            pandas DataFrame with technical summary data
        """
        try:
            import pandas as pd
            
            if not raw_data or 'scores' not in raw_data:
                return pd.DataFrame()

            scores = raw_data['scores']
            rows = []

            categories = ['intermediate', 'intradayIntermediate', 'intradayLong', 'intradayShort', 'long', 'short']

            for item in scores:
                inst = item.get('instrument', {})

                for cat in categories:
                    block = item.get(cat, {})

                    row = {
                        'symbol': inst.get('symbol', 'N/A'),
                        'name': inst.get('name', 'N/A'),
                        'exchange': inst.get('exchange', 'N/A'),
                        'isin': inst.get('isin', 'N/A'),
                        'instrumentId': inst.get('instrumentId', 'N/A'),
                        'category': cat,
                    }

                    row.update(block)
                    rows.append(row)

            if rows:
                df = pd.DataFrame(rows)
                df = DataFrameOptimizer.optimize_memory(df)
                return df

            return pd.DataFrame()
        except ImportError:
            logger.warning("pandas not available for technical summaries dataframe")
            return []
        except Exception as e:
            logger.error(f"Error building technical summaries dataframe: {e}")
            raise

    def build_quantamental_timeseries_dataframe(
        self,
        raw_data: Dict[str, Any]
    ) -> Any:
        """
        Build quantamental timeseries DataFrame matching notebook API structure.
        
        Returns DataFrame with timestamps and all score columns
        
        Args:
            raw_data: Raw API response
            
        Returns:
            pandas DataFrame with timeseries data
        """
        try:
            import pandas as pd
            
            timeseries_data = raw_data[0] if isinstance(raw_data, list) and len(raw_data) > 0 else raw_data or {}

            df = pd.DataFrame({
                'timestamp': timeseries_data.get('timestamps', []),
                'quantamental_score': timeseries_data.get('quantamental', []),
                'growth_score': timeseries_data.get('growth', []),
                'income_score': timeseries_data.get('income', []),
                'momentum_score': timeseries_data.get('momentum', []),
                'quality_score': timeseries_data.get('quality', []),
                'valuation_score': timeseries_data.get('valuation', [])
            })

            if len(df) > 0:
                df = DataFrameOptimizer.optimize_memory(df)

            return df
        except ImportError:
            logger.warning("pandas not available for quantamental timeseries dataframe")
            return []
        except Exception as e:
            logger.error(f"Error building quantamental timeseries dataframe: {e}")
            raise


class DataFrameOptimizer:
    """
    Utility class for optimizing pandas DataFrame memory usage.
    
    This class provides methods to reduce memory footprint of DataFrames
    by downcasting numeric types and optimizing object columns.
    """
    
    @staticmethod
    def optimize_numeric_columns(df: Any) -> Any:
        """
        Downcast numeric columns to use less memory.
        
        Args:
            df: pandas DataFrame to optimize
            
        Returns:
            Optimized DataFrame
        """
        try:
            import pandas as pd
            import numpy as np
            
            for col in df.select_dtypes(include=['int64']).columns:
                df[col] = pd.to_numeric(df[col], downcast='integer')
            
            for col in df.select_dtypes(include=['float64']).columns:
                df[col] = pd.to_numeric(df[col], downcast='float')
            
            return df
        except ImportError:
            logger.warning("pandas not available for DataFrame optimization")
            return df
    
    @staticmethod
    def optimize_object_columns(df: Any) -> Any:
        """
        Convert object columns with low cardinality to category type.
        
        Args:
            df: pandas DataFrame to optimize
            
        Returns:
            Optimized DataFrame
        """
        try:
            import pandas as pd
            
            # Check if DataFrame is empty
            if len(df) == 0:
                return df
            
            for col in df.select_dtypes(include=['object']).columns:
                if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
                    df[col] = df[col].astype('category')
            
            return df
        except ImportError:
            logger.warning("pandas not available for DataFrame optimization")
            return df
    
    @staticmethod
    def get_memory_usage(df: Any) -> Dict[str, Any]:
        """
        Get memory usage statistics for a DataFrame.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dictionary with memory statistics
        """
        try:
            return {
                "total_bytes": df.memory_usage(deep=True).sum(),
                "per_column": df.memory_usage(deep=True).to_dict()
            }
        except (ImportError, AttributeError):
            return {"error": "Unable to calculate memory usage"}

    @staticmethod
    def optimize_memory(df: Any) -> Any:
        """
        Reduce DataFrame memory usage by downcasting numeric types.
        
        Comprehensive memory optimization that combines numeric and object 
        column optimization.
        
        Args:
            df: pandas DataFrame to optimize
            
        Returns:
            Optimized DataFrame
        """
        try:
            import pandas as pd
            import numpy as np
            
            # Optimize integer columns
            for col in df.select_dtypes(include=['int64', 'int32']).columns:
                col_min = df[col].min()
                col_max = df[col].max()
                
                if col_min >= 0:
                    if col_max < np.iinfo(np.uint8).max:
                        df[col] = df[col].astype(np.uint8)
                    elif col_max < np.iinfo(np.uint16).max:
                        df[col] = df[col].astype(np.uint16)
                    elif col_max < np.iinfo(np.uint32).max:
                        df[col] = df[col].astype(np.uint32)
                else:
                    if col_min > np.iinfo(np.int8).min and col_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif col_min > np.iinfo(np.int16).min and col_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif col_min > np.iinfo(np.int32).min and col_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
            
            # Optimize float columns
            for col in df.select_dtypes(include=['float64']).columns:
                df[col] = pd.to_numeric(df[col], downcast='float')
            
            return df
        except ImportError:
            logger.warning("pandas not available for DataFrame optimization")
            return df

    @staticmethod
    def flatten_nested_columns(df: Any, column_name: str, prefix: str = '') -> Any:
        """
        Flatten nested column using json_normalize.
        
        Args:
            df: pandas DataFrame with nested columns
            column_name: Name of the column to flatten
            prefix: Prefix to add to flattened column names
            
        Returns:
            DataFrame with flattened columns
        """
        try:
            import pandas as pd
            
            if column_name not in df.columns:
                return df
            
            # Get the nested column data
            nested_data = df[column_name].tolist()
            
            # Normalize the nested data
            flattened = pd.json_normalize(nested_data)
            
            # Add prefix to column names if provided
            if prefix:
                flattened.columns = [f"{prefix}_{col}" for col in flattened.columns]
            
            # Drop the original nested column and join with flattened data
            df = df.drop(columns=[column_name])
            df = pd.concat([df.reset_index(drop=True), flattened.reset_index(drop=True)], axis=1)
            
            return df
        except ImportError:
            logger.warning("pandas not available for DataFrame flattening")
            return df
        except Exception as e:
            logger.warning(f"Error flattening nested columns: {e}")
            return df

    @staticmethod
    def process_batch(data_list: List[Dict], optimize_memory: bool = True) -> Any:
        """
        Batch process list of dictionaries into DataFrame.
        
        Args:
            data_list: List of dictionaries to convert
            optimize_memory: Whether to optimize memory after conversion
            
        Returns:
            pandas DataFrame
        """
        try:
            import pandas as pd
            
            if not data_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list)
            
            if optimize_memory:
                df = DataFrameOptimizer.optimize_memory(df)
            
            return df
        except ImportError:
            logger.warning("pandas not available for batch processing")
            return data_list
