"""
Data Collection Service

This module contains the main data collection service that fetches stock data
from TipRanks and Trading Central APIs, processes it, and stores it in the database.
"""
import time
import logging
import functools
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlalchemy.orm import Session

from app.config import settings
from app.models.stock_data import (
    AnalystConsensus,
    NewsSentiment,
    QuantamentalScore,
    HedgeFundData,
    CrowdStats,
    BloggerSentiment,
    TechnicalIndicator,
    TargetPrice,
    DataCollectionLog,
    TimeframeType,
)
from app.utils.api_client import APIClient
from app.utils.data_processor import ResponseBuilder
from app.utils.helpers import get_utc_now, is_valid_ticker, normalize_ticker

logger = logging.getLogger(__name__)


def collection_wrapper(data_type: str, source: str, api_endpoint: str) -> Callable:
    """
    Decorator to handle common collection logic for data collection methods.
    
    This decorator:
    - Normalizes ticker symbol
    - Times the collection operation
    - Handles error logging and rollback
    - Logs collection results to database
    - Returns standardized response format
    
    Args:
        data_type: Type of data being collected (e.g., "analyst_ratings")
        source: Data source name (e.g., "tipranks", "trading_central")
        api_endpoint: API endpoint constant from APIClient
        
    Returns:
        Decorated function with common collection logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, ticker: str, db: Session) -> Dict[str, Any]:
            start_time = time.time()
            ticker = normalize_ticker(ticker)
            
            try:
                result = func(self, ticker, db)
                
                if result.get("status") == "error":
                    duration = time.time() - start_time
                    self._log_collection(
                        db, ticker, data_type, False,
                        result.get("message"), duration, 0,
                        source, api_endpoint
                    )
                    return result
                
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, data_type, True, None, duration,
                    result.get("records", 1), source, api_endpoint
                )
                logger.info(f"Collected {data_type} for {ticker}")
                return result
                
            except Exception as e:
                db.rollback()
                duration = time.time() - start_time
                error_msg = str(e)
                logger.error(f"Error collecting {data_type} for {ticker}: {error_msg}")
                self._log_collection(
                    db, ticker, data_type, False, error_msg, duration, 0,
                    source, api_endpoint
                )
                return {"status": "error", "message": error_msg, "records": 0}
        return wrapper
    return decorator


class DataCollectionService:
    """
    Service for collecting and storing stock data from multiple APIs.
    
    Features:
    - Fetches data from TipRanks and Trading Central APIs
    - Processes and validates API responses
    - Stores data in database using SQLAlchemy models
    - Handles errors and retries
    - Logs all collection activities
    - Returns collection statistics
    """
    
    def __init__(self):
        """Initialize the data collection service"""
        self.api_client = APIClient(
            timeout=settings.API_TIMEOUT,
            max_retries=settings.MAX_RETRIES,
            cache_ttl=settings.CACHE_TTL_SECONDS,
            rate_limit=settings.API_RATE_LIMIT
        )
        self.response_builder = ResponseBuilder()
    
    def _log_collection(
        self,
        db: Session,
        ticker: Optional[str],
        data_type: str,
        success: bool,
        error_message: Optional[str],
        duration_seconds: float,
        records_collected: int,
        source: str = "unknown",
        api_endpoint: Optional[str] = None
    ) -> None:
        """
        Log a collection attempt to the database.
        
        Args:
            db: Database session
            ticker: Stock ticker symbol
            data_type: Type of data collected
            success: Whether collection was successful
            error_message: Error message if failed
            duration_seconds: Duration of collection in seconds
            records_collected: Number of records collected
            source: Data source name
            api_endpoint: API endpoint used
        """
        try:
            log_entry = DataCollectionLog(
                ticker=ticker,
                data_type=data_type,
                success=success,
                error_message=error_message,
                duration_seconds=duration_seconds,
                records_collected=records_collected,
                source=source,
                api_endpoint=api_endpoint
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log collection: {e}")
            db.rollback()
    
    @collection_wrapper("analyst_ratings", "tipranks", APIClient.TIPRANKS_ANALYST_RATINGS)
    def collect_analyst_ratings(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store analyst ratings for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        # Fetch data from TipRanks API
        raw_data = self.api_client.fetch_tipranks_analyst_ratings(ticker)
        
        if not raw_data:
            return {"status": "error", "message": "No data received", "records": 0}
        
        # Parse response using notebook-style method
        parsed_data = self.response_builder.build_analyst_consensus(raw_data, ticker)
        
        # Create database record with notebook-style fields only
        db_record = AnalystConsensus(
            ticker=parsed_data["ticker"],
            timestamp=get_utc_now(),
            total_ratings=parsed_data.get("total_ratings"),
            buy_ratings=parsed_data.get("buy_ratings"),
            hold_ratings=parsed_data.get("hold_ratings"),
            sell_ratings=parsed_data.get("sell_ratings"),
            consensus_recommendation=parsed_data.get("consensus_recommendation"),
            consensus_rating_score=parsed_data.get("consensus_rating_score"),
            price_target_high=parsed_data.get("price_target_high"),
            price_target_low=parsed_data.get("price_target_low"),
            price_target_average=parsed_data.get("price_target_average"),
            source="tipranks",
            raw_data=raw_data
        )
        
        db.add(db_record)
        db.commit()
        
        return {"status": "success", "records": 1}
    
    @collection_wrapper("news_sentiment", "tipranks", APIClient.TIPRANKS_NEWS)
    def collect_news_sentiment(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store news sentiment for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        # Fetch data from TipRanks API
        raw_data = self.api_client.fetch_tipranks_news(ticker)
        
        if not raw_data:
            return {"status": "error", "message": "No data received", "records": 0}
        
        # Parse response using notebook-style method
        parsed_data = self.response_builder.build_news_sentiment(raw_data, ticker)
        
        # Create database record with notebook-style fields only
        db_record = NewsSentiment(
            ticker=parsed_data["ticker"],
            timestamp=get_utc_now(),
            stock_bullish_score=parsed_data.get("stock_bullish_score"),
            stock_bearish_score=parsed_data.get("stock_bearish_score"),
            sector_bullish_score=parsed_data.get("sector_bullish_score"),
            sector_bearish_score=parsed_data.get("sector_bearish_score"),
            source="tipranks",
            raw_data=raw_data
        )
        
        db.add(db_record)
        db.commit()
        
        return {"status": "success", "records": 1}
    
    @collection_wrapper("quantamental_scores", "trading_central", APIClient.TC_QUANTAMENTAL)
    def collect_quantamental_scores(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store quantamental scores for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        # Get Trading Central ID for this ticker
        ticker_config = settings.TICKER_CONFIGS.get(ticker, {})
        tc_id = ticker_config.get("tr_v4_id")
        
        if not tc_id:
            return {"status": "error", "message": "No Trading Central ID configured", "records": 0}
        
        # Fetch data from Trading Central API
        raw_data = self.api_client.fetch_tc_quantamental(tc_id)
        
        if not raw_data:
            return {"status": "error", "message": "No data received", "records": 0}
        
        # Parse response using notebook-style method
        parsed_data = self.response_builder.build_quantamental(raw_data, ticker)
        
        # Create database record with notebook-style fields only
        db_record = QuantamentalScore(
            ticker=parsed_data["ticker"],
            timestamp=get_utc_now(),
            overall=parsed_data.get("overall"),
            growth=parsed_data.get("growth"),
            value=parsed_data.get("value"),
            income=parsed_data.get("income"),
            quality=parsed_data.get("quality"),
            momentum=parsed_data.get("momentum"),
            source="trading_central",
            raw_data=raw_data
        )
        
        db.add(db_record)
        db.commit()
        
        return {"status": "success", "records": 1}
    
    @collection_wrapper("hedge_fund_data", "tipranks", APIClient.TIPRANKS_ETORO_DATA)
    def collect_hedge_fund_data(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store hedge fund data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        # Fetch data from TipRanks eToro API
        raw_data = self.api_client.fetch_tipranks_etoro_data(ticker)
        
        if not raw_data:
            return {"status": "error", "message": "No data received", "records": 0}
        
        # Parse response using notebook-style method
        parsed_data = self.response_builder.build_hedge_fund(raw_data, ticker)
        
        # Create database record with notebook-style fields only
        db_record = HedgeFundData(
            ticker=parsed_data["ticker"],
            timestamp=get_utc_now(),
            sentiment=parsed_data.get("sentiment"),
            trend_action=parsed_data.get("trend_action"),
            trend_value=parsed_data.get("trend_value"),
            source="tipranks",
            raw_data=raw_data
        )
        
        db.add(db_record)
        db.commit()
        
        return {"status": "success", "records": 1}
    
    @collection_wrapper("crowd_statistics", "tipranks", APIClient.TIPRANKS_CROWD_DATA)
    def collect_crowd_data(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store crowd statistics for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        # Fetch data from TipRanks API
        raw_data = self.api_client.fetch_tipranks_crowd_data(ticker)
        
        if not raw_data:
            return {"status": "error", "message": "No data received", "records": 0}
        
        # Parse response using notebook-style method
        parsed_data = self.response_builder.build_crowd_stats(raw_data, ticker)
        
        # Create database record with notebook-style fields only
        db_record = CrowdStats(
            ticker=parsed_data["ticker"],
            timestamp=get_utc_now(),
            stats_type=parsed_data.get("stats_type", "all"),
            portfolio_holding=parsed_data.get("portfolio_holding"),
            amount_of_portfolios=parsed_data.get("amount_of_portfolios"),
            amount_of_public_portfolios=parsed_data.get("amount_of_public_portfolios"),
            percent_allocated=parsed_data.get("percent_allocated"),
            based_on_portfolios=parsed_data.get("based_on_portfolios"),
            percent_over_last_7d=parsed_data.get("percent_over_last_7d"),
            percent_over_last_30d=parsed_data.get("percent_over_last_30d"),
            score=parsed_data.get("score"),
            individual_sector_average=parsed_data.get("individual_sector_average"),
            frequency=parsed_data.get("frequency"),
            source="tipranks",
            raw_data=raw_data
        )
        
        db.add(db_record)
        db.commit()
        
        return {"status": "success", "records": 1}
    
    @collection_wrapper("blogger_sentiment", "tipranks", APIClient.TIPRANKS_BLOGGERS)
    def collect_blogger_sentiment(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store blogger sentiment for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        # Fetch data from TipRanks API
        raw_data = self.api_client.fetch_tipranks_bloggers(ticker)
        
        if not raw_data:
            return {"status": "error", "message": "No data received", "records": 0}
        
        # Parse response using notebook-style method
        parsed_data = self.response_builder.build_blogger_sentiment(raw_data, ticker)
        
        # Create database record with notebook-style fields only
        db_record = BloggerSentiment(
            ticker=parsed_data["ticker"],
            timestamp=get_utc_now(),
            bearish=parsed_data.get("bearish"),
            neutral=parsed_data.get("neutral"),
            bullish=parsed_data.get("bullish"),
            bearish_count=parsed_data.get("bearish_count"),
            neutral_count=parsed_data.get("neutral_count"),
            bullish_count=parsed_data.get("bullish_count"),
            score=parsed_data.get("score"),
            avg=parsed_data.get("avg"),
            source="tipranks",
            raw_data=raw_data
        )
        
        db.add(db_record)
        db.commit()
        
        return {"status": "success", "records": 1}
    
    def collect_technical_indicators(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store technical indicators for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        start_time = time.time()
        ticker = normalize_ticker(ticker)
        
        try:
            # Get Trading Central ID for this ticker
            ticker_config = settings.TICKER_CONFIGS.get(ticker, {})
            tc_id = ticker_config.get("tr_v3_id")
            
            if not tc_id:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "technical_indicators", False,
                    "No Trading Central ID configured", duration, 0,
                    "trading_central", APIClient.TC_TECHNICAL_SUMMARIES
                )
                return {"status": "error", "message": "No Trading Central ID configured", "records": 0}
            
            # Fetch data from Trading Central API
            raw_data = self.api_client.fetch_tc_technical_summaries(tc_id)
            
            if not raw_data:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "technical_indicators", False,
                    "No data received from API", duration, 0,
                    "trading_central", APIClient.TC_TECHNICAL_SUMMARIES
                )
                return {"status": "error", "message": "No data received", "records": 0}
            
            # Parse response using notebook-style method
            # Note: build_technical_summaries_dataframe returns a list of category scores, 
            # not individual indicator values. We'll store the raw data for now.
            summaries = self.response_builder.build_technical_summaries_dataframe(raw_data)
            
            # Create database record with minimal data - technical indicators
            # are not directly available in the notebook-style response
            db_record = TechnicalIndicator(
                ticker=ticker,
                timestamp=get_utc_now(),
                timeframe=TimeframeType.ONE_DAY,
                open_price=None,
                high_price=None,
                low_price=None,
                close_price=None,
                volume=None,
                sma_20=None,
                sma_50=None,
                sma_200=None,
                ema_12=None,
                ema_26=None,
                rsi_14=None,
                stoch_k=None,
                stoch_d=None,
                cci=None,
                williams_r=None,
                macd=None,
                macd_signal=None,
                macd_histogram=None,
                adx=None,
                plus_di=None,
                minus_di=None,
                atr=None,
                bollinger_upper=None,
                bollinger_middle=None,
                bollinger_lower=None,
                support_1=None,
                support_2=None,
                resistance_1=None,
                resistance_2=None,
                pivot_point=None,
                oscillator_signal=None,
                moving_avg_signal=None,
                overall_signal=None,
                source="trading_central",
                raw_data=raw_data
            )
            
            db.add(db_record)
            db.commit()
            
            # Log success
            duration = time.time() - start_time
            self._log_collection(
                db, ticker, "technical_indicators", True, None, duration, 1,
                "trading_central", APIClient.TC_TECHNICAL_SUMMARIES
            )
            
            logger.info(f"Collected technical indicators for {ticker}")
            return {"status": "success", "records": 1}
            
        except Exception as e:
            db.rollback()
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Error collecting technical indicators for {ticker}: {error_msg}")
            self._log_collection(
                db, ticker, "technical_indicators", False, error_msg, duration, 0,
                "trading_central", APIClient.TC_TECHNICAL_SUMMARIES
            )
            return {"status": "error", "message": error_msg, "records": 0}
    
    @collection_wrapper("target_prices", "trading_central", APIClient.TC_TARGET_PRICES)
    def collect_target_prices(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store target prices for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        # Get Trading Central ID for this ticker
        ticker_config = settings.TICKER_CONFIGS.get(ticker, {})
        tc_id = ticker_config.get("tr_v4_id")
        
        if not tc_id:
            return {"status": "error", "message": "No Trading Central ID configured", "records": 0}
        
        # Fetch data from Trading Central API
        raw_data = self.api_client.fetch_tc_target_prices(tc_id)
        
        if not raw_data:
            return {"status": "error", "message": "No data received", "records": 0}
        
        # Parse response using notebook-style method
        parsed_data = self.response_builder.build_target_price(raw_data, ticker)
        
        # Create database record with notebook-style fields only
        db_record = TargetPrice(
            ticker=parsed_data["ticker"],
            timestamp=get_utc_now(),
            close_price=parsed_data.get("close_price"),
            target_price=parsed_data.get("target_price"),
            target_date=parsed_data.get("target_date"),
            last_updated=parsed_data.get("last_updated"),
            source="trading_central",
            raw_data=raw_data
        )
        db.add(db_record)
        
        db.commit()
        
        return {"status": "success", "records": 1}
    
    def collect_all_data_for_ticker(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect all data types for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection results for each data type
        """
        if not is_valid_ticker(ticker):
            return {"error": f"Invalid ticker: {ticker}"}
        
        ticker = normalize_ticker(ticker)
        logger.info(f"Starting data collection for {ticker}")
        
        start_time = time.time()
        results = {
            "ticker": ticker,
            "timestamp": get_utc_now().isoformat(),
            "data_types": {}
        }
        
        # Collect all data types
        collection_methods = [
            ("analyst_ratings", self.collect_analyst_ratings),
            ("news_sentiment", self.collect_news_sentiment),
            ("quantamental_scores", self.collect_quantamental_scores),
            ("hedge_fund_data", self.collect_hedge_fund_data),
            ("crowd_statistics", self.collect_crowd_data),
            ("blogger_sentiment", self.collect_blogger_sentiment),
            ("technical_indicators", self.collect_technical_indicators),
            ("target_prices", self.collect_target_prices),
        ]
        
        total_records = 0
        success_count = 0
        error_count = 0
        
        for data_type, method in collection_methods:
            result = method(ticker, db)
            results["data_types"][data_type] = result
            
            if result.get("status") == "success":
                success_count += 1
                total_records += result.get("records", 0)
            else:
                error_count += 1
        
        duration = time.time() - start_time
        results["summary"] = {
            "total_data_types": len(collection_methods),
            "successful": success_count,
            "failed": error_count,
            "total_records": total_records,
            "duration_seconds": round(duration, 2)
        }
        
        logger.info(
            f"Completed data collection for {ticker}: "
            f"{success_count} successful, {error_count} failed, "
            f"{total_records} records in {duration:.2f}s"
        )
        
        return results
    
    def collect_all_tickers(self, db: Session) -> Dict[str, Any]:
        """
        Collect data for all configured tickers.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with collection results for all tickers
        """
        start_time = time.time()
        tickers = settings.ticker_list
        
        logger.info(f"Starting data collection for {len(tickers)} tickers: {tickers}")
        
        results = {
            "timestamp": get_utc_now().isoformat(),
            "tickers": {}
        }
        
        total_records = 0
        success_count = 0
        partial_count = 0
        error_count = 0
        
        for ticker in tickers:
            ticker_result = self.collect_all_data_for_ticker(ticker, db)
            results["tickers"][ticker] = ticker_result
            
            summary = ticker_result.get("summary", {})
            ticker_records = summary.get("total_records", 0)
            total_records += ticker_records
            
            # Categorize ticker result
            if summary.get("failed", 0) == 0:
                success_count += 1
            elif summary.get("successful", 0) > 0:
                partial_count += 1
            else:
                error_count += 1
        
        duration = time.time() - start_time
        results["summary"] = {
            "total_tickers": len(tickers),
            "fully_successful": success_count,
            "partially_successful": partial_count,
            "failed": error_count,
            "total_records": total_records,
            "duration_seconds": round(duration, 2)
        }
        
        logger.info(
            f"Completed data collection for all tickers: "
            f"{success_count} successful, {partial_count} partial, {error_count} failed, "
            f"{total_records} total records in {duration:.2f}s"
        )
        
        return results
    
    def close(self) -> None:
        """Clean up resources"""
        self.api_client.close()


# Create a singleton instance
data_collection_service = DataCollectionService()
