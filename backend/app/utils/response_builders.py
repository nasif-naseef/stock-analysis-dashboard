"""
Response Builders

This module contains the ResponseBuilder class with static methods for
transforming raw API responses into structured data matching the notebook
API response models.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.utils.helpers import safe_float, safe_int, get_utc_now

logger = logging.getLogger(__name__)


class ResponseBuilder:
    """
    Builder class for parsing and transforming API responses into
    structured data matching notebook response models.
    
    All methods are static to allow direct class method calls without instantiation.
    """
    
    @staticmethod
    def safe_parse_number(value, default=None):
        """Safely parse a value that may be string, int, float, or None to a number"""
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        return default
    
    @staticmethod
    def build_analyst_consensus(raw_data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """
        Build analyst consensus data from TipRanks API response.
        
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
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_analyst_consensus_history(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
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
            
            results = []
            for item in history:
                results.append({
                    "date": item.get('date'),
                    "buy": safe_int(item.get('buy')),
                    "hold": safe_int(item.get('hold')),
                    "sell": safe_int(item.get('sell')),
                    "consensus": item.get('consensus'),
                    "priceTarget": safe_float(item.get('priceTarget')),
                })
            
            return results
        except Exception as e:
            logger.error(f"Error building analyst consensus history: {e}")
            return []
    
    @staticmethod
    def build_news_sentiment(raw_data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """
        Build news sentiment data from TipRanks API response.
        
        Extracts from: newsSentimentScore.stock, newsSentimentScore.sector
        Converts decimal values (0-1) to percentage (0-100)
        
        Args:
            raw_data: Raw API response from TipRanks
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed news sentiment fields (percentages 0-100)
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            sentiment_data = raw_data.get('newsSentimentScore', {}) or {}
            stock_data = sentiment_data.get('stock', {}) or {}
            sector_data = sentiment_data.get('sector', {}) or {}
            
            # Extract values and convert from decimal (0-1) to percentage (0-100)
            stock_bullish = safe_float(stock_data.get('bullishPercent'))
            stock_bearish = safe_float(stock_data.get('bearishPercent'))
            sector_bullish = safe_float(sector_data.get('bullishPercent'))
            sector_bearish = safe_float(sector_data.get('bearishPercent'))
            
            # Convert to percentage if values are in decimal format (0-1 range)
            # Check if value is not None and appears to be in decimal format (0.0 to 1.0)
            if stock_bullish is not None and 0 <= stock_bullish <= 1.0:
                stock_bullish = stock_bullish * 100
            if stock_bearish is not None and 0 <= stock_bearish <= 1.0:
                stock_bearish = stock_bearish * 100
            if sector_bullish is not None and 0 <= sector_bullish <= 1.0:
                sector_bullish = sector_bullish * 100
            if sector_bearish is not None and 0 <= sector_bearish <= 1.0:
                sector_bearish = sector_bearish * 100
            
            return {
                "ticker": ticker,
                "stock_bullish_score": stock_bullish,
                "stock_bearish_score": stock_bearish,
                "sector_bullish_score": sector_bullish,
                "sector_bearish_score": sector_bearish,
            }
        except Exception as e:
            logger.error(f"Error building news sentiment: {e}")
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_hedge_fund(raw_data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """
        Build hedge fund data from TipRanks API response.
        
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
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_insider_score(raw_data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """
        Build insider score data from TipRanks API response.
        
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
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_crowd_stats(raw_data: Dict[str, Any], ticker: str, stats_type: str = 'all') -> Dict[str, Any]:
        """
        Build crowd statistics data from raw API response with score-based sentiment.
        
        Extracts from: generalStats{statsType.capitalize()}
        
        Args:
            raw_data: Raw API response from TipRanks
            ticker: Stock ticker symbol
            stats_type: Type of stats ('all', 'individual', 'institution')
            
        Returns:
            Dictionary with parsed crowd stats fields including derived bullish/bearish percentages
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            key = f'generalStats{stats_type.capitalize()}'
            stats_data = raw_data.get(key, {}) or {}
            
            # Extract score (0-1 range)
            score = safe_float(stats_data.get('score'))
            sector_avg = safe_float(stats_data.get('individualSectorAverage'))
            
            # Derive bullish/bearish from score
            # Score > 0.5 indicates bullish, < 0.5 indicates bearish
            bullish_percent = None
            bearish_percent = None
            neutral_percent = None
            
            if score is not None:
                # Convert score to percentage interpretation
                # Score of 0.5 = 50/50, Score of 1.0 = 100% bullish
                bullish_percent = score * 100
                bearish_percent = (1 - score) * 100
                neutral_percent = 0  # TipRanks crowd doesn't have neutral
            
            # Determine sentiment based on score vs sector average
            sentiment = None
            if score is not None:
                if sector_avg is not None:
                    if score > sector_avg + 0.1:
                        sentiment = "bullish"
                    elif score < sector_avg - 0.1:
                        sentiment = "bearish"
                    else:
                        sentiment = "neutral"
                else:
                    if score > 0.55:
                        sentiment = "bullish"
                    elif score < 0.45:
                        sentiment = "bearish"
                    else:
                        sentiment = "neutral"
            
            # Extract other metrics
            portfolios_holding = safe_int(stats_data.get('portfoliosHolding', 0)) or 0
            percent_allocated = safe_float(stats_data.get('percentAllocated'))
            
            return {
                "ticker": ticker,
                "portfolio_holding": portfolios_holding,
                "amount_of_portfolios": safe_int(stats_data.get('amountOfPortfolios', 0)) or 0,
                "amount_of_public_portfolios": safe_int(stats_data.get('amountOfPublicPortfolios', 0)) or 0,
                "percent_allocated": percent_allocated or 0.0,
                "based_on_portfolios": safe_int(stats_data.get('basedOnPortfolios', 0)) or 0,
                "percent_over_last_7d": safe_float(stats_data.get('percentOverLast7Days', 0.0)) or 0.0,
                "percent_over_last_30d": safe_float(stats_data.get('percentOverLast30Days', 0.0)) or 0.0,
                "score": score or 0.0,
                "individual_sector_average": sector_avg or 0.0,
                "frequency": safe_float(stats_data.get('frequency', 0.0)) or 0.0,
                "crowd_sentiment": sentiment,
                "bullish_percent": bullish_percent,
                "bearish_percent": bearish_percent,
                "neutral_percent": neutral_percent,
                "sentiment_score": score,
                "mentions_count": portfolios_holding,
                "impressions": 0,
                "engagement_rate": percent_allocated,
                "trending_score": None,
                "rank_day": None,
                "rank_week": None,
                "total_posts": 0,
                "unique_users": 0,
                "avg_sentiment_post": score,
                "raw_data": raw_data,
            }
        except Exception as e:
            logger.error(f"Error building crowd stats: {e}")
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_blogger_sentiment(raw_data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """
        Build blogger sentiment data from raw API response with string-to-number conversion.
        
        Extracts from: bloggerSentiment
        
        Args:
            raw_data: Raw API response from TipRanks
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed blogger sentiment fields with converted percentages
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            blogger_data = raw_data.get('bloggerSentiment', {}) or {}
            
            # Convert string percentages to floats using safe_parse_number helper
            bullish_percent = ResponseBuilder.safe_parse_number(blogger_data.get('bullish'))
            bearish_percent = ResponseBuilder.safe_parse_number(blogger_data.get('bearish'))
            neutral_percent = ResponseBuilder.safe_parse_number(blogger_data.get('neutral'))
            
            # Get counts (these are already integers from API)
            bullish_count = blogger_data.get('bullishCount', 0) or 0
            bearish_count = blogger_data.get('bearishCount', 0) or 0
            neutral_count = blogger_data.get('neutralCount', 0) or 0
            
            # Calculate neutral_percent if not provided but we have bullish and bearish
            if neutral_percent is None and bullish_percent is not None and bearish_percent is not None:
                neutral_percent = 100.0 - bullish_percent - bearish_percent
                if neutral_percent < 0:
                    neutral_percent = 0
            
            # Get score and avg
            score = blogger_data.get('score')
            avg = blogger_data.get('avg')
            
            return {
                "ticker": ticker,
                "bearish": bearish_percent,
                "neutral": neutral_percent,
                "bullish": bullish_percent,
                "bearish_count": bearish_count,
                "neutral_count": neutral_count,
                "bullish_count": bullish_count,
                "score": score,
                "avg": avg,
                "bullish_percent": bullish_percent,
                "bearish_percent": bearish_percent,
                "neutral_percent": neutral_percent,
                "raw_data": raw_data,
            }
        except Exception as e:
            logger.error(f"Error building blogger sentiment: {e}")
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_quantamental(raw_data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """
        Build quantamental scores from Trading Central API response.
        
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
            
            # Extract scores
            overall = safe_int(raw_data.get('quantamental'))
            growth = safe_int(raw_data.get('growth'))
            value = safe_int(raw_data.get('valuation'))
            income = safe_int(raw_data.get('income'))
            quality = safe_int(raw_data.get('quality'))
            momentum = safe_int(raw_data.get('momentum'))
            
            # Extract labels if available
            overall_label = raw_data.get('quantamentalLabel', {})
            growth_label = raw_data.get('growthLabel', {})
            value_label = raw_data.get('valuationLabel', {})
            income_label = raw_data.get('incomeLabel', {})
            quality_label = raw_data.get('qualityLabel', {})
            momentum_label = raw_data.get('momentumLabel', {})
            
            return {
                "ticker": ticker,
                # Database model fields (for backward compatibility)
                "overall": overall,
                "growth": growth,
                "value": value,
                "income": income,
                "quality": quality,
                "momentum": momentum,
                # Response schema fields
                "overall_score": overall,
                "growth_score": growth,
                "value_score": value,
                "quality_score": quality,
                "momentum_score": momentum,
                # Labels
                "overall_label": overall_label.get('name') if overall_label else None,
                "growth_label": growth_label.get('name') if growth_label else None,
                "value_label": value_label.get('name') if value_label else None,
                "income_label": income_label.get('name') if income_label else None,
                "quality_label": quality_label.get('name') if quality_label else None,
                "momentum_label": momentum_label.get('name') if momentum_label else None,
            }
        except Exception as e:
            logger.error(f"Error building quantamental: {e}")
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_quantamental_timeseries_dataframe(raw_data: Dict[str, Any]) -> Any:
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
            from app.utils.data_processor import DataFrameOptimizer
            
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
    
    @staticmethod
    def build_target_price(raw_data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """
        Build target price data from Trading Central API response.
        
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
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_article_distribution(raw_data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
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
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_article_sentiment(sentiment_responses: Dict[str, Any], ticker: str) -> Dict[str, Any]:
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
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_support_resistance(raw_item: Dict[str, Any]) -> Dict[str, Any]:
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
            return {"symbol": "", "date": "", "exchange": "", "error": str(e)}
    
    @staticmethod
    def build_stop_loss(
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
            return {"ticker": ticker, "error": str(e)}
    
    @staticmethod
    def build_chart_events_dataframe(
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
            from app.utils.data_processor import DataFrameOptimizer
            
            if not raw_data or 'events' not in raw_data:
                return pd.DataFrame()

            events_raw = raw_data['events']
            if not events_raw:
                return pd.DataFrame()

            events_df = DataFrameOptimizer.process_batch(events_raw)

            # Flatten nested columns
            if 'dates' in events_df.columns:
                events_df = DataFrameOptimizer.flatten_nested_columns(events_df, 'dates', 'date')
            if 'endPrices' in events_df.columns:
                events_df = DataFrameOptimizer.flatten_nested_columns(events_df, 'endPrices', 'endPrice')
            if 'eventType' in events_df.columns:
                events_df = DataFrameOptimizer.flatten_nested_columns(events_df, 'eventType', 'eventType')
            if 'targetPrice' in events_df.columns:
                events_df = DataFrameOptimizer.flatten_nested_columns(events_df, 'targetPrice', 'targetPrice')

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
    
    @staticmethod
    def build_technical_summaries_dataframe(raw_data: Dict[str, Any]) -> Any:
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
            from app.utils.data_processor import DataFrameOptimizer
            
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
