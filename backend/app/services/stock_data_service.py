"""
Stock Data Service

This module provides a comprehensive service layer for fetching and processing
stock data from various APIs. It matches the structure and methods from the
Jupyter notebook (Final.ipynb) for consistency.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from app.config import settings
from app.utils.api_client import APIClient
from app.utils.data_processor import ResponseBuilder, DataFrameOptimizer
from app.utils.helpers import normalize_ticker, is_valid_ticker

logger = logging.getLogger(__name__)


class StockDataService:
    """
    Comprehensive service for fetching stock data from TipRanks and Trading Central APIs.
    
    This service provides methods that match the notebook API structures exactly,
    making it easy to build responses that match the expected frontend format.
    
    Features:
    - All methods support both single ticker and all-tickers modes
    - Consistent error handling and logging
    - Built-in response parsing using ResponseBuilder
    """
    
    def __init__(self):
        """Initialize the stock data service"""
        self.api_client = APIClient(
            timeout=settings.API_TIMEOUT,
            max_retries=settings.MAX_RETRIES,
            cache_ttl=settings.CACHE_TTL_SECONDS,
            rate_limit=settings.API_RATE_LIMIT
        )
        self.response_builder = ResponseBuilder()
        self.df_optimizer = DataFrameOptimizer()
    
    def _get_ticker_list(self, ticker: Optional[str] = None) -> List[str]:
        """Get list of tickers to process"""
        if ticker:
            return [normalize_ticker(ticker)]
        return settings.ticker_list
    
    # ============================================
    # Analyst Methods
    # ============================================
    
    def get_analyst_consensus(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get analyst consensus data matching notebook API structure.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with analyst consensus data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_analyst_ratings(t)
                if raw_data:
                    results[t] = self.response_builder.build_analyst_consensus(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching analyst consensus for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_analyst_consensus_history(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get analyst consensus history data.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with analyst consensus history data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_analyst_ratings(t)
                if raw_data:
                    history = self.response_builder.build_analyst_consensus_history(raw_data)
                    results[t] = {"ticker": t, "history": history}
                else:
                    results[t] = {"ticker": t, "history": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching analyst consensus history for {t}: {e}")
                results[t] = {"ticker": t, "history": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_analyst_ratings(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get analyst ratings data (original format for database storage).
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with analyst ratings data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_analyst_ratings(t)
                if raw_data:
                    results[t] = self.response_builder.build_analyst_consensus(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching analyst ratings for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    # ============================================
    # News Methods
    # ============================================
    
    def get_news_sentiment(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get news sentiment data matching notebook API structure.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with news sentiment data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_news(t)
                if raw_data:
                    results[t] = self.response_builder.build_news_sentiment(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching news sentiment for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_news_articles(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get news articles for a ticker.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with news articles data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_news(t)
                if raw_data:
                    articles = raw_data.get('news', []) if isinstance(raw_data, dict) else []
                    results[t] = {"ticker": t, "articles": articles}
                else:
                    results[t] = {"ticker": t, "articles": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching news articles for {t}: {e}")
                results[t] = {"ticker": t, "articles": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    # ============================================
    # eToro/Hedge Fund Methods
    # ============================================
    
    def get_hedge_fund_confidence(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get hedge fund confidence data matching notebook API structure.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with hedge fund confidence data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_etoro_data(t)
                if raw_data:
                    results[t] = self.response_builder.build_hedge_fund(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching hedge fund confidence for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_insider_score(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get insider score data matching notebook API structure.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with insider score data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_etoro_data(t)
                if raw_data:
                    results[t] = self.response_builder.build_insider_score(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching insider score for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_historical_hedge_fund_data(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get historical hedge fund data.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with historical hedge fund data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_etoro_data(t)
                if raw_data:
                    results[t] = self.response_builder.build_hedge_fund(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching historical hedge fund data for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_corporate_insider_transactions_data(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get corporate insider transactions data.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with corporate insider transactions data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_etoro_data(t)
                if raw_data:
                    transactions = []
                    if isinstance(raw_data, dict):
                        transactions = raw_data.get('insiderTransactions', []) or []
                    results[t] = {"ticker": t, "transactions": transactions}
                else:
                    results[t] = {"ticker": t, "transactions": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching corporate insider transactions for {t}: {e}")
                results[t] = {"ticker": t, "transactions": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_etoro_experts_data(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get eToro experts data for a ticker.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with eToro experts data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_etoro_data(t)
                if raw_data:
                    experts = []
                    if isinstance(raw_data, dict):
                        experts = raw_data.get('experts', []) or []
                    results[t] = {"ticker": t, "experts": experts}
                else:
                    results[t] = {"ticker": t, "experts": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching eToro experts data for {t}: {e}")
                results[t] = {"ticker": t, "experts": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_etoro_top_experts_data(self) -> Dict[str, Any]:
        """
        Get top eToro experts data (not ticker-specific).
        
        Returns:
            Dictionary with top eToro experts data
        """
        try:
            # This endpoint typically doesn't require a ticker
            # Using the first configured ticker as a proxy
            tickers = settings.ticker_list
            if not tickers:
                return {"experts": [], "error": "No tickers configured"}
            
            raw_data = self.api_client.fetch_tipranks_etoro_data(tickers[0])
            if raw_data and isinstance(raw_data, dict):
                return {"experts": raw_data.get('topExperts', [])}
            return {"experts": [], "error": "No data received"}
        except Exception as e:
            logger.error(f"Error fetching top eToro experts data: {e}")
            return {"experts": [], "error": str(e)}
    
    # ============================================
    # Crowd Methods
    # ============================================
    
    def get_crowd_stats(self, ticker: Optional[str] = None, stats_type: str = 'all') -> Dict[str, Any]:
        """
        Get crowd statistics matching notebook API structure.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            stats_type: Type of stats ('all', 'individual', 'institution')
            
        Returns:
            Dictionary with crowd statistics data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_crowd_data(t)
                if raw_data:
                    results[t] = self.response_builder.build_crowd_stats(raw_data, t, stats_type)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching crowd stats for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_crowd_also_bought_data(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get crowd "also bought" data.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with crowd also bought data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_crowd_data(t)
                if raw_data:
                    also_bought = []
                    if isinstance(raw_data, dict):
                        also_bought = raw_data.get('alsoBought', []) or []
                    results[t] = {"ticker": t, "also_bought": also_bought}
                else:
                    results[t] = {"ticker": t, "also_bought": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching crowd also bought data for {t}: {e}")
                results[t] = {"ticker": t, "also_bought": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    # ============================================
    # Blogger Methods
    # ============================================
    
    def get_blogger_sentiment(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get blogger sentiment matching notebook API structure.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with blogger sentiment data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_bloggers(t)
                if raw_data:
                    results[t] = self.response_builder.build_blogger_sentiment(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching blogger sentiment for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_blogger_article_distribution(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get blogger article distribution data.
        
        Uses TipRanks bloggers endpoint and extracts bloggerArticleDistribution.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with blogger article distribution data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_bloggers(t)
                if raw_data:
                    results[t] = self.response_builder.build_blogger_article_distribution(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching blogger article distribution for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_bloggers(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get bloggers data for a ticker.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with bloggers data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                raw_data = self.api_client.fetch_tipranks_bloggers(t)
                if raw_data:
                    bloggers = []
                    if isinstance(raw_data, dict):
                        bloggers = raw_data.get('bloggers', []) or []
                    results[t] = {"ticker": t, "bloggers": bloggers}
                else:
                    results[t] = {"ticker": t, "bloggers": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching bloggers for {t}: {e}")
                results[t] = {"ticker": t, "bloggers": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    # ============================================
    # Quantamental Methods
    # ============================================
    
    def get_quantamental_scores(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get quantamental scores matching notebook API structure.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with quantamental scores data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                tc_id = ticker_config.get("tr_v4_id")
                
                if not tc_id:
                    results[t] = {"ticker": t, "error": "No Trading Central ID configured"}
                    continue
                
                raw_data = self.api_client.fetch_tc_quantamental(tc_id)
                if raw_data:
                    results[t] = self.response_builder.build_quantamental(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching quantamental scores for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_quantamental_timeseries(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get quantamental timeseries data from Trading Central API.
        
        Uses the quantamental/v4/timeseries endpoint with date range parameters.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with quantamental timeseries data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                exchange = ticker_config.get("exchange", "NASDAQ")
                
                # Build ticker_id in format: symbol:exchange (e.g., "AAPL:NASDAQ")
                ticker_id = f"{t}:{exchange}"
                
                # Calculate date range (5 years by default)
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=settings.HISTORICAL_DAYS)).strftime("%Y-%m-%d")
                
                raw_data = self.api_client.fetch_tc_quantamental_timeseries(
                    ticker_id,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if raw_data:
                    timeseries = self.response_builder.build_quantamental_timeseries_dataframe(raw_data)
                    results[t] = {"ticker": t, "timeseries": timeseries}
                else:
                    results[t] = {"ticker": t, "timeseries": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching quantamental timeseries for {t}: {e}")
                results[t] = {"ticker": t, "timeseries": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    # ============================================
    # Article Methods
    # ============================================
    
    def get_article_distribution(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get article distribution data from Trading Central API.
        
        Uses Trading Central article analytics endpoint to get article distribution by source.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with article distribution data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                entity_id = ticker_config.get("tr_v4_id")
                
                if not entity_id:
                    results[t] = {"ticker": t, "error": "No Trading Central entity ID configured"}
                    continue
                
                raw_data = self.api_client.fetch_tc_article_analytics(entity_id)
                if raw_data:
                    results[t] = self.response_builder.build_article_distribution(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching article distribution for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_article_sentiment(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get article sentiment data from Trading Central API.
        
        Fetches sentiment, subjectivity, and confidence data in parallel from 3 endpoints.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with article sentiment data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                entity_id = ticker_config.get("tr_v4_id")
                
                if not entity_id:
                    results[t] = {"ticker": t, "error": "No Trading Central entity ID configured"}
                    continue
                
                raw_data = self.api_client.fetch_tc_article_sentiment_full(entity_id)
                if raw_data:
                    results[t] = self.response_builder.build_article_sentiment(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching article sentiment for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_sentiment_history(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get sentiment history data from Trading Central API.
        
        Uses the sentiment timeseries endpoint to get historical sentiment data.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with sentiment history data (dates and sentiment_score arrays)
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                entity_id = ticker_config.get("tr_v4_id")
                
                if not entity_id:
                    results[t] = {"ticker": t, "dates": [], "sentiment_score": [], "error": "No Trading Central entity ID configured"}
                    continue
                
                raw_data = self.api_client.fetch_tc_sentiment_timeseries(entity_id)
                if raw_data:
                    # Extract dates and sentiment from response
                    dates = raw_data.get('dates', []) if isinstance(raw_data, dict) else []
                    sentiment = raw_data.get('sentiment', []) if isinstance(raw_data, dict) else []
                    results[t] = {
                        "ticker": t,
                        "dates": dates,
                        "sentiment_score": sentiment
                    }
                else:
                    results[t] = {"ticker": t, "dates": [], "sentiment_score": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching sentiment history for {t}: {e}")
                results[t] = {"ticker": t, "dates": [], "sentiment_score": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_article_topics(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get article topics data from Trading Central API.
        
        Uses Trading Central article analytics endpoint to get topics distribution.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with article topics data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                entity_id = ticker_config.get("tr_v4_id")
                
                if not entity_id:
                    results[t] = {"ticker": t, "topics": [], "error": "No Trading Central entity ID configured"}
                    continue
                
                raw_data = self.api_client.fetch_tc_article_analytics(entity_id)
                if raw_data:
                    topics = []
                    if isinstance(raw_data, dict):
                        topics = raw_data.get('topics', []) or []
                    # Process topics using DataFrameOptimizer
                    topics_processed = self.df_optimizer.process_batch(topics)
                    # Return DataFrame or list based on type
                    try:
                        import pandas as pd
                        if isinstance(topics_processed, pd.DataFrame):
                            results[t] = {"ticker": t, "topics": topics_processed}
                        else:
                            results[t] = {"ticker": t, "topics": topics}
                    except ImportError:
                        results[t] = {"ticker": t, "topics": topics}
                else:
                    results[t] = {"ticker": t, "topics": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching article topics for {t}: {e}")
                results[t] = {"ticker": t, "topics": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    # ============================================
    # Technical Methods
    # ============================================
    
    def get_support_resistance(self, ticker: Optional[str] = None, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get support/resistance levels data.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            date: Optional date string for historical data.
            
        Returns:
            Dictionary with support/resistance data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                tc_id = ticker_config.get("tr_v3_id")
                
                if not tc_id:
                    results[t] = {"ticker": t, "error": "No Trading Central ID configured"}
                    continue
                
                raw_data = self.api_client.fetch_tc_support_resistance(tc_id)
                if raw_data:
                    if isinstance(raw_data, list):
                        raw_data = raw_data[0] if raw_data else {}
                    results[t] = self.response_builder.build_support_resistance(raw_data)
                else:
                    results[t] = {"symbol": t, "date": "", "exchange": "", "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching support/resistance for {t}: {e}")
                results[t] = {"symbol": t, "date": "", "exchange": "", "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_stop_loss(
        self,
        ticker: Optional[str] = None,
        stop_type: str = 'Volatility-Based',
        direction: str = 'Below (Long Position)',
        tightness: str = 'Medium',
        priceperiod: str = 'daily',
        comprehensive: bool = False
    ) -> Dict[str, Any]:
        """
        Get stop loss recommendations.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            stop_type: Type of stop loss calculation.
            direction: Direction of stop (long/short).
            tightness: Tightness level.
            priceperiod: Price period (daily, weekly, etc.)
            comprehensive: Whether to get comprehensive stop loss data.
            
        Returns:
            Dictionary with stop loss data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                tc_id = ticker_config.get("tr_v3_id")
                
                if not tc_id:
                    results[t] = {"ticker": t, "error": "No Trading Central ID configured"}
                    continue
                
                raw_data = self.api_client.fetch_tc_stop_timeseries(tc_id)
                if raw_data:
                    results[t] = self.response_builder.build_stop_loss(
                        raw_data, t, stop_type, direction, tightness
                    )
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching stop loss for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_chart_events(self, ticker: Optional[str] = None, active: bool = True, priceperiod: str = 'daily') -> Dict[str, Any]:
        """
        Get chart events data.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            active: Whether to get active events only.
            priceperiod: Price period (daily, weekly, etc.)
            
        Returns:
            Dictionary with chart events data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                tc_id = ticker_config.get("tr_v3_id")
                
                if not tc_id:
                    results[t] = {"ticker": t, "events": [], "error": "No Trading Central ID configured"}
                    continue
                
                raw_data = self.api_client.fetch_tc_instrument_events(tc_id)
                if raw_data:
                    events = self.response_builder.build_chart_events_dataframe(raw_data, t, active)
                    results[t] = {"ticker": t, "events": events, "is_active": active}
                else:
                    results[t] = {"ticker": t, "events": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching chart events for {t}: {e}")
                results[t] = {"ticker": t, "events": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_chart_events_combined(self, ticker: Optional[str] = None, priceperiod: str = 'daily') -> Dict[str, Any]:
        """
        Get combined chart events (active and historical).
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            priceperiod: Price period (daily, weekly, etc.)
            
        Returns:
            Dictionary with combined chart events data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            active_events = self.get_chart_events(t, active=True, priceperiod=priceperiod)
            historical_events = self.get_chart_events(t, active=False, priceperiod=priceperiod)
            
            results[t] = {
                "ticker": t,
                "active_events": active_events.get("events", []) if isinstance(active_events, dict) else [],
                "historical_events": historical_events.get("events", []) if isinstance(historical_events, dict) else [],
            }
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_technical_summaries(self, ticker: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get technical summaries data.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            category: Optional category filter.
            
        Returns:
            Dictionary with technical summaries data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                tc_id = ticker_config.get("tr_v3_id")
                
                if not tc_id:
                    results[t] = {"ticker": t, "summaries": [], "error": "No Trading Central ID configured"}
                    continue
                
                raw_data = self.api_client.fetch_tc_technical_summaries(tc_id)
                if raw_data:
                    summaries = self.response_builder.build_technical_summaries_dataframe(raw_data)
                    if category:
                        summaries = [s for s in summaries if s.get('category') == category]
                    results[t] = {"ticker": t, "summaries": summaries}
                else:
                    results[t] = {"ticker": t, "summaries": [], "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching technical summaries for {t}: {e}")
                results[t] = {"ticker": t, "summaries": [], "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_target_prices(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get target prices matching notebook API structure.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with target prices data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            try:
                ticker_config = settings.TICKER_CONFIGS.get(t, {})
                tc_id = ticker_config.get("tr_v4_id")
                
                if not tc_id:
                    results[t] = {"ticker": t, "error": "No Trading Central ID configured"}
                    continue
                
                raw_data = self.api_client.fetch_tc_target_prices(tc_id)
                if raw_data:
                    results[t] = self.response_builder.build_target_price(raw_data, t)
                else:
                    results[t] = {"ticker": t, "error": "No data received"}
            except Exception as e:
                logger.error(f"Error fetching target prices for {t}: {e}")
                results[t] = {"ticker": t, "error": str(e)}
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def get_stock_overview(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive stock overview combining multiple data sources.
        
        Args:
            ticker: Optional ticker. If None, fetches for all configured tickers.
            
        Returns:
            Dictionary with comprehensive stock overview data
        """
        tickers = self._get_ticker_list(ticker)
        results = {}
        
        for t in tickers:
            overview = {
                "ticker": t,
                "analyst_consensus": self.get_analyst_consensus(t),
                "news_sentiment": self.get_news_sentiment(t),
                "hedge_fund": self.get_hedge_fund_confidence(t),
                "insider_score": self.get_insider_score(t),
                "crowd_stats": self.get_crowd_stats(t),
                "blogger_sentiment": self.get_blogger_sentiment(t),
                "quantamental": self.get_quantamental_scores(t),
                "target_price": self.get_target_prices(t),
            }
            results[t] = overview
        
        return results if len(tickers) > 1 else results.get(tickers[0], {})
    
    def close(self) -> None:
        """Clean up resources"""
        self.api_client.close()


# Create singleton instance
stock_data_service = StockDataService()
