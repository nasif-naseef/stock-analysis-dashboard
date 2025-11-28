"""
Data Collection Service

This module contains the main data collection service that fetches stock data
from TipRanks and Trading Central APIs, processes it, and stores it in the database.
"""
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlalchemy.orm import Session

from app.config import settings
from app.models.stock_data import (
    AnalystRating,
    NewsSentiment,
    QuantamentalScore,
    HedgeFundData,
    CrowdStatistics,
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
    
    def collect_analyst_ratings(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store analyst ratings for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        start_time = time.time()
        ticker = normalize_ticker(ticker)
        
        try:
            # Fetch data from TipRanks API
            raw_data = self.api_client.fetch_tipranks_analyst_ratings(ticker)
            
            if not raw_data:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "analyst_ratings", False,
                    "No data received from API", duration, 0,
                    "tipranks", APIClient.TIPRANKS_ANALYST_RATINGS
                )
                return {"status": "error", "message": "No data received", "records": 0}
            
            # Parse response using notebook-style method
            parsed_data = self.response_builder.build_analyst_consensus(raw_data, ticker)
            
            # Create database record - map notebook-style fields to legacy database fields
            # Note: Some fields are not available in the notebook-style response
            buy_ratings = parsed_data.get("buy_ratings")
            hold_ratings = parsed_data.get("hold_ratings")
            sell_ratings = parsed_data.get("sell_ratings")
            
            db_record = AnalystRating(
                ticker=parsed_data["ticker"],
                timestamp=get_utc_now(),
                strong_buy_count=None,  # Not available in notebook-style response
                buy_count=buy_ratings,
                hold_count=hold_ratings,
                sell_count=sell_ratings,
                strong_sell_count=None,  # Not available in notebook-style response
                total_analysts=parsed_data.get("total_ratings"),
                consensus_rating=None,  # Not available in notebook-style response
                consensus_score=parsed_data.get("consensus_rating_score"),
                avg_price_target=parsed_data.get("price_target_average"),
                high_price_target=parsed_data.get("price_target_high"),
                low_price_target=parsed_data.get("price_target_low"),
                current_price=None,  # Not available in notebook-style response
                upside_potential=None,  # Not available in notebook-style response
                source="tipranks",
                raw_data=raw_data
            )
            
            db.add(db_record)
            db.commit()
            
            # Log success
            duration = time.time() - start_time
            self._log_collection(
                db, ticker, "analyst_ratings", True, None, duration, 1,
                "tipranks", APIClient.TIPRANKS_ANALYST_RATINGS
            )
            
            logger.info(f"Collected analyst ratings for {ticker}")
            return {"status": "success", "records": 1}
            
        except Exception as e:
            db.rollback()
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Error collecting analyst ratings for {ticker}: {error_msg}")
            self._log_collection(
                db, ticker, "analyst_ratings", False, error_msg, duration, 0,
                "tipranks", APIClient.TIPRANKS_ANALYST_RATINGS
            )
            return {"status": "error", "message": error_msg, "records": 0}
    
    def collect_news_sentiment(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store news sentiment for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        start_time = time.time()
        ticker = normalize_ticker(ticker)
        
        try:
            # Fetch data from TipRanks API
            raw_data = self.api_client.fetch_tipranks_news(ticker)
            
            if not raw_data:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "news_sentiment", False,
                    "No data received from API", duration, 0,
                    "tipranks", APIClient.TIPRANKS_NEWS
                )
                return {"status": "error", "message": "No data received", "records": 0}
            
            # Parse response using notebook-style method
            parsed_data = self.response_builder.build_news_sentiment(raw_data, ticker)
            
            # Create database record - map notebook-style fields to legacy database fields
            # Calculate sentiment score from bullish/bearish
            stock_bullish = parsed_data.get("stock_bullish_score")
            stock_bearish = parsed_data.get("stock_bearish_score")
            sentiment_score = None
            if stock_bullish is not None and stock_bearish is not None:
                sentiment_score = stock_bullish - stock_bearish
            
            db_record = NewsSentiment(
                ticker=parsed_data["ticker"],
                timestamp=get_utc_now(),
                sentiment=None,  # Not available in notebook-style response
                sentiment_score=sentiment_score,
                buzz_score=None,  # Not available in notebook-style response
                news_score=None,  # Not available in notebook-style response
                total_articles=None,  # Not available in notebook-style response
                positive_articles=None,  # Not available in notebook-style response
                negative_articles=None,  # Not available in notebook-style response
                neutral_articles=None,  # Not available in notebook-style response
                sector_sentiment=parsed_data.get("sector_bullish_score"),
                sector_avg=parsed_data.get("sector_bearish_score"),
                source="tipranks",
                raw_data=raw_data
            )
            
            db.add(db_record)
            db.commit()
            
            # Log success
            duration = time.time() - start_time
            self._log_collection(
                db, ticker, "news_sentiment", True, None, duration, 1,
                "tipranks", APIClient.TIPRANKS_NEWS
            )
            
            logger.info(f"Collected news sentiment for {ticker}")
            return {"status": "success", "records": 1}
            
        except Exception as e:
            db.rollback()
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Error collecting news sentiment for {ticker}: {error_msg}")
            self._log_collection(
                db, ticker, "news_sentiment", False, error_msg, duration, 0,
                "tipranks", APIClient.TIPRANKS_NEWS
            )
            return {"status": "error", "message": error_msg, "records": 0}
    
    def collect_quantamental_scores(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store quantamental scores for a ticker.
        
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
            tc_id = ticker_config.get("tr_v4_id")
            
            if not tc_id:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "quantamental_scores", False,
                    "No Trading Central ID configured", duration, 0,
                    "trading_central", APIClient.TC_QUANTAMENTAL
                )
                return {"status": "error", "message": "No Trading Central ID configured", "records": 0}
            
            # Fetch data from Trading Central API
            raw_data = self.api_client.fetch_tc_quantamental(tc_id)
            
            if not raw_data:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "quantamental_scores", False,
                    "No data received from API", duration, 0,
                    "trading_central", APIClient.TC_QUANTAMENTAL
                )
                return {"status": "error", "message": "No data received", "records": 0}
            
            # Parse response using notebook-style method
            parsed_data = self.response_builder.build_quantamental(raw_data, ticker)
            
            # Create database record - map notebook-style fields to legacy database fields
            db_record = QuantamentalScore(
                ticker=parsed_data["ticker"],
                timestamp=get_utc_now(),
                overall_score=float(parsed_data.get("overall") or 0) if parsed_data.get("overall") is not None else None,
                quality_score=float(parsed_data.get("quality") or 0) if parsed_data.get("quality") is not None else None,
                value_score=float(parsed_data.get("value") or 0) if parsed_data.get("value") is not None else None,
                growth_score=float(parsed_data.get("growth") or 0) if parsed_data.get("growth") is not None else None,
                momentum_score=float(parsed_data.get("momentum") or 0) if parsed_data.get("momentum") is not None else None,
                revenue_growth=None,  # Not available in notebook-style response
                earnings_growth=None,  # Not available in notebook-style response
                profit_margin=None,  # Not available in notebook-style response
                debt_to_equity=None,  # Not available in notebook-style response
                return_on_equity=None,  # Not available in notebook-style response
                pe_ratio=None,  # Not available in notebook-style response
                pb_ratio=None,  # Not available in notebook-style response
                ps_ratio=None,  # Not available in notebook-style response
                peg_ratio=None,  # Not available in notebook-style response
                ev_ebitda=None,  # Not available in notebook-style response
                sector_rank=None,  # Not available in notebook-style response
                industry_rank=None,  # Not available in notebook-style response
                overall_rank=None,  # Not available in notebook-style response
                source="trading_central",
                raw_data=raw_data
            )
            
            db.add(db_record)
            db.commit()
            
            # Log success
            duration = time.time() - start_time
            self._log_collection(
                db, ticker, "quantamental_scores", True, None, duration, 1,
                "trading_central", APIClient.TC_QUANTAMENTAL
            )
            
            logger.info(f"Collected quantamental scores for {ticker}")
            return {"status": "success", "records": 1}
            
        except Exception as e:
            db.rollback()
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Error collecting quantamental scores for {ticker}: {error_msg}")
            self._log_collection(
                db, ticker, "quantamental_scores", False, error_msg, duration, 0,
                "trading_central", APIClient.TC_QUANTAMENTAL
            )
            return {"status": "error", "message": error_msg, "records": 0}
    
    def collect_hedge_fund_data(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store hedge fund data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        start_time = time.time()
        ticker = normalize_ticker(ticker)
        
        try:
            # Fetch data from TipRanks eToro API
            raw_data = self.api_client.fetch_tipranks_etoro_data(ticker)
            
            if not raw_data:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "hedge_fund_data", False,
                    "No data received from API", duration, 0,
                    "tipranks", APIClient.TIPRANKS_ETORO_DATA
                )
                return {"status": "error", "message": "No data received", "records": 0}
            
            # Parse response using notebook-style method
            parsed_data = self.response_builder.build_hedge_fund(raw_data, ticker)
            
            # Create database record - map notebook-style fields to legacy database fields
            db_record = HedgeFundData(
                ticker=parsed_data["ticker"],
                timestamp=get_utc_now(),
                institutional_ownership_pct=None,  # Not available in notebook-style response
                hedge_fund_count=0,  # Not available in notebook-style response
                total_shares_held=None,  # Not available in notebook-style response
                market_value_held=None,  # Not available in notebook-style response
                new_positions=0,  # Not available in notebook-style response
                increased_positions=0,  # Not available in notebook-style response
                decreased_positions=0,  # Not available in notebook-style response
                closed_positions=0,  # Not available in notebook-style response
                hedge_fund_sentiment=None,  # Would need determine_sentiment() call based on sentiment value
                smart_money_score=None,  # Not available in notebook-style response
                top_holders=None,  # Not available in notebook-style response
                shares_change_qoq=None,  # Not available in notebook-style response
                ownership_change_qoq=None,  # Not available in notebook-style response
                source="tipranks",
                raw_data=raw_data
            )
            
            db.add(db_record)
            db.commit()
            
            # Log success
            duration = time.time() - start_time
            self._log_collection(
                db, ticker, "hedge_fund_data", True, None, duration, 1,
                "tipranks", APIClient.TIPRANKS_ETORO_DATA
            )
            
            logger.info(f"Collected hedge fund data for {ticker}")
            return {"status": "success", "records": 1}
            
        except Exception as e:
            db.rollback()
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Error collecting hedge fund data for {ticker}: {error_msg}")
            self._log_collection(
                db, ticker, "hedge_fund_data", False, error_msg, duration, 0,
                "tipranks", APIClient.TIPRANKS_ETORO_DATA
            )
            return {"status": "error", "message": error_msg, "records": 0}
    
    def collect_crowd_data(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store crowd statistics for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        start_time = time.time()
        ticker = normalize_ticker(ticker)
        
        try:
            # Fetch data from TipRanks API
            raw_data = self.api_client.fetch_tipranks_crowd_data(ticker)
            
            if not raw_data:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "crowd_statistics", False,
                    "No data received from API", duration, 0,
                    "tipranks", APIClient.TIPRANKS_CROWD_DATA
                )
                return {"status": "error", "message": "No data received", "records": 0}
            
            # Parse response using notebook-style method
            parsed_data = self.response_builder.build_crowd_stats(raw_data, ticker)
            
            # Create database record - map notebook-style fields to legacy database fields
            db_record = CrowdStatistics(
                ticker=parsed_data["ticker"],
                timestamp=get_utc_now(),
                crowd_sentiment=None,  # Not available in notebook-style response
                sentiment_score=parsed_data.get("score"),
                mentions_count=None,  # Not available in notebook-style response
                mentions_change=None,  # Not available in notebook-style response
                impressions=None,  # Not available in notebook-style response
                engagement_rate=None,  # Not available in notebook-style response
                bullish_percent=None,  # Not available in notebook-style response
                bearish_percent=None,  # Not available in notebook-style response
                neutral_percent=None,  # Not available in notebook-style response
                trending_score=None,  # Not available in notebook-style response
                rank_day=None,  # Not available in notebook-style response
                rank_week=None,  # Not available in notebook-style response
                total_posts=None,  # Not available in notebook-style response
                unique_users=None,  # Not available in notebook-style response
                avg_sentiment_post=None,  # Not available in notebook-style response
                source="tipranks",
                raw_data=raw_data
            )
            
            db.add(db_record)
            db.commit()
            
            # Log success
            duration = time.time() - start_time
            self._log_collection(
                db, ticker, "crowd_statistics", True, None, duration, 1,
                "tipranks", APIClient.TIPRANKS_CROWD_DATA
            )
            
            logger.info(f"Collected crowd data for {ticker}")
            return {"status": "success", "records": 1}
            
        except Exception as e:
            db.rollback()
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Error collecting crowd data for {ticker}: {error_msg}")
            self._log_collection(
                db, ticker, "crowd_statistics", False, error_msg, duration, 0,
                "tipranks", APIClient.TIPRANKS_CROWD_DATA
            )
            return {"status": "error", "message": error_msg, "records": 0}
    
    def collect_blogger_sentiment(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store blogger sentiment for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            db: Database session
            
        Returns:
            Dictionary with collection status and results
        """
        start_time = time.time()
        ticker = normalize_ticker(ticker)
        
        try:
            # Fetch data from TipRanks API
            raw_data = self.api_client.fetch_tipranks_bloggers(ticker)
            
            if not raw_data:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "blogger_sentiment", False,
                    "No data received from API", duration, 0,
                    "tipranks", APIClient.TIPRANKS_BLOGGERS
                )
                return {"status": "error", "message": "No data received", "records": 0}
            
            # Parse response using notebook-style method
            parsed_data = self.response_builder.build_blogger_sentiment(raw_data, ticker)
            
            # Calculate total from notebook-style fields
            total = (parsed_data.get("bullish") or 0) + (parsed_data.get("bearish") or 0) + (parsed_data.get("neutral") or 0)
            
            # Create database record - map notebook-style fields to legacy database fields
            db_record = BloggerSentiment(
                ticker=parsed_data["ticker"],
                timestamp=get_utc_now(),
                blogger_sentiment=None,  # Would need to compute from bullish/bearish counts
                sentiment_score=parsed_data.get("score"),
                total_articles=total,
                bullish_articles=parsed_data.get("bullish") or 0,
                bearish_articles=parsed_data.get("bearish") or 0,
                neutral_articles=parsed_data.get("neutral") or 0,
                bullish_percent=(parsed_data.get("bullish") or 0) / total * 100 if total > 0 else None,
                bearish_percent=(parsed_data.get("bearish") or 0) / total * 100 if total > 0 else None,
                avg_blogger_accuracy=parsed_data.get("avg"),
                top_blogger_opinion=None,  # Not available in notebook-style response
                sentiment_change_1d=None,  # Not available in notebook-style response
                sentiment_change_1w=None,  # Not available in notebook-style response
                sentiment_change_1m=None,  # Not available in notebook-style response
                source="tipranks",
                raw_data=raw_data
            )
            
            db.add(db_record)
            db.commit()
            
            # Log success
            duration = time.time() - start_time
            self._log_collection(
                db, ticker, "blogger_sentiment", True, None, duration, 1,
                "tipranks", APIClient.TIPRANKS_BLOGGERS
            )
            
            logger.info(f"Collected blogger sentiment for {ticker}")
            return {"status": "success", "records": 1}
            
        except Exception as e:
            db.rollback()
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Error collecting blogger sentiment for {ticker}: {error_msg}")
            self._log_collection(
                db, ticker, "blogger_sentiment", False, error_msg, duration, 0,
                "tipranks", APIClient.TIPRANKS_BLOGGERS
            )
            return {"status": "error", "message": error_msg, "records": 0}
    
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
    
    def collect_target_prices(self, ticker: str, db: Session) -> Dict[str, Any]:
        """
        Collect and store target prices for a ticker.
        
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
            tc_id = ticker_config.get("tr_v4_id")
            
            if not tc_id:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "target_prices", False,
                    "No Trading Central ID configured", duration, 0,
                    "trading_central", APIClient.TC_TARGET_PRICES
                )
                return {"status": "error", "message": "No Trading Central ID configured", "records": 0}
            
            # Fetch data from Trading Central API
            raw_data = self.api_client.fetch_tc_target_prices(tc_id)
            
            if not raw_data:
                duration = time.time() - start_time
                self._log_collection(
                    db, ticker, "target_prices", False,
                    "No data received from API", duration, 0,
                    "trading_central", APIClient.TC_TARGET_PRICES
                )
                return {"status": "error", "message": "No data received", "records": 0}
            
            # Parse response using notebook-style method
            parsed_data = self.response_builder.build_target_price(raw_data, ticker)
            
            # Create a single database record (notebook-style returns single dict, not list)
            db_record = TargetPrice(
                ticker=parsed_data["ticker"],
                timestamp=get_utc_now(),
                analyst_name=None,  # Not available in notebook-style response
                analyst_firm=None,  # Not available in notebook-style response
                target_price=parsed_data.get("target_price"),
                previous_target=None,  # Not available in notebook-style response
                target_change=None,  # Not available in notebook-style response
                target_change_pct=None,  # Not available in notebook-style response
                rating=None,  # Not available in notebook-style response
                previous_rating=None,  # Not available in notebook-style response
                rating_changed=False,  # Not available in notebook-style response
                current_price_at_rating=parsed_data.get("close_price"),
                upside_to_target=None,  # Not available in notebook-style response
                analyst_accuracy_score=None,  # Not available in notebook-style response
                rating_date=None,  # Not available in notebook-style response
                source="trading_central",
                raw_data=raw_data
            )
            db.add(db_record)
            records_added = 1
            
            db.commit()
            
            # Log success
            duration = time.time() - start_time
            self._log_collection(
                db, ticker, "target_prices", True, None, duration, records_added,
                "trading_central", APIClient.TC_TARGET_PRICES
            )
            
            logger.info(f"Collected {records_added} target prices for {ticker}")
            return {"status": "success", "records": records_added}
            
        except Exception as e:
            db.rollback()
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Error collecting target prices for {ticker}: {error_msg}")
            self._log_collection(
                db, ticker, "target_prices", False, error_msg, duration, 0,
                "trading_central", APIClient.TC_TARGET_PRICES
            )
            return {"status": "error", "message": error_msg, "records": 0}
    
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
