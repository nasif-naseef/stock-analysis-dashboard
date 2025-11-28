"""
Data Fetchers

This module contains classes for fetching data from external APIs:
- BaseDataFetcher: Base class with common functionality
- TipRanksDataFetcher: For TipRanks API endpoints
- TradingCentralDataFetcher: For Trading Central API endpoints
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.config import settings
from app.utils.api_client import APIClient

logger = logging.getLogger(__name__)


class BaseDataFetcher:
    """
    Base class for data fetchers with common functionality.
    
    Provides batch fetching and key retrieval methods.
    """
    
    def __init__(self, api_client: Optional[APIClient] = None):
        """
        Initialize the data fetcher.
        
        Args:
            api_client: Optional APIClient instance. If not provided, creates one.
        """
        self.api_client = api_client or APIClient(
            timeout=settings.API_TIMEOUT,
            max_retries=settings.MAX_RETRIES,
            cache_ttl=settings.CACHE_TTL_SECONDS,
            rate_limit=settings.API_RATE_LIMIT
        )
    
    def _fetch_batch(
        self,
        fetch_func,
        tickers: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch data for a batch of tickers.
        
        Args:
            fetch_func: Function to call for each ticker
            tickers: List of tickers to fetch. If None, uses configured tickers.
            **kwargs: Additional arguments to pass to fetch_func
            
        Returns:
            Dictionary mapping tickers to their data
        """
        if tickers is None:
            tickers = settings.ticker_list
        
        results = {}
        for ticker in tickers:
            try:
                results[ticker] = fetch_func(ticker, **kwargs)
            except Exception as e:
                logger.error(f"Error fetching data for {ticker}: {e}")
                results[ticker] = {"ticker": ticker, "error": str(e)}
        
        return results
    
    def _get_key(self, ticker: str, key_type: str = 'tr_v4_id') -> Optional[str]:
        """
        Get the API key/ID for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            key_type: Type of key ('tr_v4_id', 'tr_v3_id')
            
        Returns:
            The API key/ID or None if not found
        """
        config = settings.TICKER_CONFIGS.get(ticker, {})
        return config.get(key_type)
    
    def close(self) -> None:
        """Clean up resources"""
        if self.api_client:
            self.api_client.close()


class TipRanksDataFetcher(BaseDataFetcher):
    """
    Data fetcher for TipRanks API endpoints.
    
    Provides methods for fetching:
    - Analyst ratings
    - News sentiment
    - Stock overview
    - eToro/hedge fund data
    - Crowd wisdom data
    - Blogger sentiment
    """
    
    def fetch_analyst_ratings(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch analyst ratings from TipRanks.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            return self.api_client.fetch_tipranks_analyst_ratings(ticker)
        except Exception as e:
            logger.error(f"Error fetching analyst ratings for {ticker}: {e}")
            return None
    
    def fetch_news(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch news and sentiment from TipRanks.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            return self.api_client.fetch_tipranks_news(ticker)
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return None
    
    def fetch_stock_overview(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch stock overview from TipRanks.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            return self.api_client.fetch_tipranks_stock_overview(ticker)
        except Exception as e:
            logger.error(f"Error fetching stock overview for {ticker}: {e}")
            return None
    
    def fetch_etoro(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch eToro/hedge fund data from TipRanks.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            return self.api_client.fetch_tipranks_etoro_data(ticker)
        except Exception as e:
            logger.error(f"Error fetching eToro data for {ticker}: {e}")
            return None
    
    def fetch_crowd_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch crowd wisdom data from TipRanks.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            return self.api_client.fetch_tipranks_crowd_data(ticker)
        except Exception as e:
            logger.error(f"Error fetching crowd data for {ticker}: {e}")
            return None
    
    def fetch_blogger_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch blogger sentiment data from TipRanks.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            return self.api_client.fetch_tipranks_bloggers(ticker)
        except Exception as e:
            logger.error(f"Error fetching blogger data for {ticker}: {e}")
            return None
    
    def fetch_all_for_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch all available data for a ticker from TipRanks.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with all data types
        """
        return {
            "ticker": ticker,
            "analyst_ratings": self.fetch_analyst_ratings(ticker),
            "news": self.fetch_news(ticker),
            "stock_overview": self.fetch_stock_overview(ticker),
            "etoro": self.fetch_etoro(ticker),
            "crowd": self.fetch_crowd_data(ticker),
            "blogger": self.fetch_blogger_data(ticker),
        }


class TradingCentralDataFetcher(BaseDataFetcher):
    """
    Data fetcher for Trading Central API endpoints.
    
    Provides methods for fetching:
    - Quantamental scores
    - Target prices
    - Article analytics and sentiment
    - Support/resistance levels
    - Stop loss recommendations
    - Chart events
    - Technical summaries
    """
    
    def fetch_quantamental(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch quantamental scores from Trading Central.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            tc_id = self._get_key(ticker, 'tr_v4_id')
            if not tc_id:
                logger.warning(f"No Trading Central V4 ID for {ticker}")
                return None
            return self.api_client.fetch_tc_quantamental(tc_id)
        except Exception as e:
            logger.error(f"Error fetching quantamental for {ticker}: {e}")
            return None
    
    def fetch_target_prices(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch target prices from Trading Central.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            tc_id = self._get_key(ticker, 'tr_v4_id')
            if not tc_id:
                logger.warning(f"No Trading Central V4 ID for {ticker}")
                return None
            return self.api_client.fetch_tc_target_prices(tc_id)
        except Exception as e:
            logger.error(f"Error fetching target prices for {ticker}: {e}")
            return None
    
    def fetch_quantamental_timeseries(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch quantamental timeseries from Trading Central.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            tc_id = self._get_key(ticker, 'tr_v4_id')
            if not tc_id:
                logger.warning(f"No Trading Central V4 ID for {ticker}")
                return None
            # Use quantamental endpoint with timeseries parameter
            return self.api_client.fetch_tc_quantamental(tc_id)
        except Exception as e:
            logger.error(f"Error fetching quantamental timeseries for {ticker}: {e}")
            return None
    
    def fetch_article_analytics(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch article analytics from Trading Central.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            tc_id = self._get_key(ticker, 'tr_v4_id')
            if not tc_id:
                logger.warning(f"No Trading Central V4 ID for {ticker}")
                return None
            return self.api_client.fetch_tc_article_analytics(tc_id)
        except Exception as e:
            logger.error(f"Error fetching article analytics for {ticker}: {e}")
            return None
    
    def fetch_article_sentiment(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch article sentiment from Trading Central.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            tc_id = self._get_key(ticker, 'tr_v4_id')
            if not tc_id:
                logger.warning(f"No Trading Central V4 ID for {ticker}")
                return None
            return self.api_client.fetch_tc_article_sentiments(tc_id)
        except Exception as e:
            logger.error(f"Error fetching article sentiment for {ticker}: {e}")
            return None
    
    def fetch_sentiment_history(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch sentiment history from Trading Central.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            tc_id = self._get_key(ticker, 'tr_v4_id')
            if not tc_id:
                logger.warning(f"No Trading Central V4 ID for {ticker}")
                return None
            # Sentiment history is part of article sentiments
            return self.api_client.fetch_tc_article_sentiments(tc_id)
        except Exception as e:
            logger.error(f"Error fetching sentiment history for {ticker}: {e}")
            return None
    
    def fetch_support_resistance(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch support/resistance levels from Trading Central.
        
        Args:
            date: Optional date string for historical data
            
        Returns:
            Raw API response or None on error
        """
        try:
            # Support/resistance is typically fetched for specific instruments
            # This returns data for all configured tickers
            results = []
            for ticker in settings.ticker_list:
                tc_id = self._get_key(ticker, 'tr_v3_id')
                if tc_id:
                    data = self.api_client.fetch_tc_support_resistance(tc_id)
                    if data:
                        results.append(data)
            return results if results else None
        except Exception as e:
            logger.error(f"Error fetching support/resistance: {e}")
            return None
    
    def fetch_support_resistance_for_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch support/resistance levels for a specific ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            tc_id = self._get_key(ticker, 'tr_v3_id')
            if not tc_id:
                logger.warning(f"No Trading Central V3 ID for {ticker}")
                return None
            return self.api_client.fetch_tc_support_resistance(tc_id)
        except Exception as e:
            logger.error(f"Error fetching support/resistance for {ticker}: {e}")
            return None
    
    def fetch_stop_loss(
        self,
        ticker: str,
        stop_type: str = 'Volatility-Based',
        direction: str = 'Below (Long Position)',
        tightness: str = 'Medium',
        priceperiod: str = 'daily'
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch stop loss recommendations from Trading Central.
        
        Args:
            ticker: Stock ticker symbol
            stop_type: Type of stop loss calculation
            direction: Direction of stop (long/short)
            tightness: Tightness level
            priceperiod: Price period (daily, weekly, etc.)
            
        Returns:
            Raw API response or None on error
        """
        try:
            tc_id = self._get_key(ticker, 'tr_v3_id')
            if not tc_id:
                logger.warning(f"No Trading Central V3 ID for {ticker}")
                return None
            return self.api_client.fetch_tc_stop_timeseries(tc_id)
        except Exception as e:
            logger.error(f"Error fetching stop loss for {ticker}: {e}")
            return None
    
    def fetch_chart_events(
        self,
        ticker: str,
        active: bool = True,
        priceperiod: str = 'daily'
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch chart events from Trading Central.
        
        Args:
            ticker: Stock ticker symbol
            active: Whether to fetch active events only
            priceperiod: Price period (daily, weekly, etc.)
            
        Returns:
            Raw API response or None on error
        """
        try:
            tc_id = self._get_key(ticker, 'tr_v3_id')
            if not tc_id:
                logger.warning(f"No Trading Central V3 ID for {ticker}")
                return None
            return self.api_client.fetch_tc_instrument_events(tc_id)
        except Exception as e:
            logger.error(f"Error fetching chart events for {ticker}: {e}")
            return None
    
    def fetch_technical_summaries(self) -> Optional[Dict[str, Any]]:
        """
        Fetch technical summaries from Trading Central.
        
        Returns data for all configured tickers.
        
        Returns:
            Raw API response or None on error
        """
        try:
            results = []
            for ticker in settings.ticker_list:
                tc_id = self._get_key(ticker, 'tr_v3_id')
                if tc_id:
                    data = self.api_client.fetch_tc_technical_summaries(tc_id)
                    if data:
                        results.append({"ticker": ticker, "data": data})
            return results if results else None
        except Exception as e:
            logger.error(f"Error fetching technical summaries: {e}")
            return None
    
    def fetch_technical_summaries_for_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch technical summaries for a specific ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Raw API response or None on error
        """
        try:
            tc_id = self._get_key(ticker, 'tr_v3_id')
            if not tc_id:
                logger.warning(f"No Trading Central V3 ID for {ticker}")
                return None
            return self.api_client.fetch_tc_technical_summaries(tc_id)
        except Exception as e:
            logger.error(f"Error fetching technical summaries for {ticker}: {e}")
            return None
    
    def fetch_all_for_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch all available data for a ticker from Trading Central.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with all data types
        """
        return {
            "ticker": ticker,
            "quantamental": self.fetch_quantamental(ticker),
            "target_prices": self.fetch_target_prices(ticker),
            "article_analytics": self.fetch_article_analytics(ticker),
            "article_sentiment": self.fetch_article_sentiment(ticker),
            "support_resistance": self.fetch_support_resistance_for_ticker(ticker),
            "stop_loss": self.fetch_stop_loss(ticker),
            "chart_events": self.fetch_chart_events(ticker),
            "technical_summaries": self.fetch_technical_summaries_for_ticker(ticker),
        }


# Create singleton instances for convenience
tipranks_fetcher = TipRanksDataFetcher()
trading_central_fetcher = TradingCentralDataFetcher()
