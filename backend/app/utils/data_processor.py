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
    Builder class for parsing and transforming API responses into
    structured data suitable for database storage.
    """
    
    def build_analyst_ratings(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build analyst ratings data from TipRanks API response.
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed analyst rating fields
        """
        try:
            # Extract consensus data - handle both list and dict responses
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            # Fix: Use correct field names from TipRanks API
            # Primary: analystConsensus, analystPriceTarget (TipRanks format)
            # Fallback: consensus, priceTarget (legacy format)
            consensus = raw_data.get("analystConsensus", {}) or raw_data.get("consensus", {}) or {}
            price_target = raw_data.get("analystPriceTarget", {}) or raw_data.get("priceTarget", {}) or {}
            prices = raw_data.get("prices", [])
            
            # Extract rating counts from analystConsensus first, then fall back to top-level
            buy = safe_int(consensus.get("buy", 0)) or safe_int(raw_data.get("buy", 0)) or 0
            hold = safe_int(consensus.get("hold", 0)) or safe_int(raw_data.get("hold", 0)) or 0
            sell = safe_int(consensus.get("sell", 0)) or safe_int(raw_data.get("sell", 0)) or 0
            
            # Strong buy/sell might be separate (not in TipRanks analystConsensus, but check top-level)
            strong_buy = safe_int(raw_data.get("strongBuy", 0)) or 0
            strong_sell = safe_int(raw_data.get("strongSell", 0)) or 0
            
            # Total analysts - use numberOfAnalystRatings from consensus if available
            total = safe_int(consensus.get("numberOfAnalystRatings", 0)) or (buy + hold + sell + strong_buy + strong_sell)
            
            # Price targets from analystPriceTarget
            avg_target = safe_float(price_target.get("average"))
            high_target = safe_float(price_target.get("high"))
            low_target = safe_float(price_target.get("low"))
            
            # Get current price - try from prices array first, then fall back to currentPrice
            current = None
            if prices and len(prices) > 0:
                # Get the most recent price (last item in prices array)
                current = safe_float(prices[-1].get("p"))
            if current is None:
                current = safe_float(raw_data.get("currentPrice"))
            
            # Calculate upside potential
            upside = None
            if avg_target and current and current > 0:
                upside = ((avg_target - current) / current) * 100
            
            # Consensus score - use consensusRating from analystConsensus if available
            consensus_score = safe_float(consensus.get("consensusRating")) or safe_float(consensus.get("rating"))
            
            # Consensus text (e.g., "Moderate Buy")
            consensus_text = consensus.get("consensus")
            
            return {
                "ticker": ticker,
                "timestamp": get_utc_now(),
                "strong_buy_count": strong_buy,
                "buy_count": buy,
                "hold_count": hold,
                "sell_count": sell,
                "strong_sell_count": strong_sell,
                "total_analysts": total,
                "consensus_rating": determine_rating(
                    buy + strong_buy,
                    hold,
                    sell + strong_sell,
                    consensus_score
                ),
                "consensus_score": consensus_score,
                "consensus_text": consensus_text,
                "avg_price_target": avg_target,
                "high_price_target": high_target,
                "low_price_target": low_target,
                "current_price": current,
                "upside_potential": upside,
                "source": "tipranks",
                "raw_data": raw_data
            }
        except Exception as e:
            logger.error(f"Error building analyst ratings: {e}")
            raise
    
    def build_news_sentiment(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build news sentiment data from API response.
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed news sentiment fields
        """
        try:
            # Handle list response
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            sentiment_data = raw_data.get("sentiment", {})
            
            # Extract counts
            positive = safe_int(sentiment_data.get("bullish", 0)) or 0
            negative = safe_int(sentiment_data.get("bearish", 0)) or 0
            neutral_count = safe_int(sentiment_data.get("neutral", 0)) or 0
            total = positive + negative + neutral_count
            
            # Sentiment score
            score = safe_float(sentiment_data.get("score"))
            buzz = safe_float(raw_data.get("buzz"))
            news_score = safe_float(raw_data.get("newsScore"))
            
            return {
                "ticker": ticker,
                "timestamp": get_utc_now(),
                "sentiment": determine_sentiment(score),
                "sentiment_score": score,
                "buzz_score": buzz,
                "news_score": news_score,
                "total_articles": total,
                "positive_articles": positive,
                "negative_articles": negative,
                "neutral_articles": neutral_count,
                "sector_sentiment": safe_float(raw_data.get("sectorSentiment")),
                "sector_avg": safe_float(raw_data.get("sectorAvg")),
                "source": "tipranks",
                "raw_data": raw_data
            }
        except Exception as e:
            logger.error(f"Error building news sentiment: {e}")
            raise
    
    def build_quantamental_scores(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build quantamental scores from Trading Central API response.
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed quantamental score fields
        """
        try:
            # Handle list response
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            scores = raw_data.get("scores", {})
            fundamentals = raw_data.get("fundamentals", {})
            valuation = raw_data.get("valuation", {})
            ranking = raw_data.get("ranking", {})
            
            return {
                "ticker": ticker,
                "timestamp": get_utc_now(),
                "overall_score": safe_float(scores.get("overall")),
                "quality_score": safe_float(scores.get("quality")),
                "value_score": safe_float(scores.get("value")),
                "growth_score": safe_float(scores.get("growth")),
                "momentum_score": safe_float(scores.get("momentum")),
                "revenue_growth": safe_float(fundamentals.get("revenueGrowth")),
                "earnings_growth": safe_float(fundamentals.get("earningsGrowth")),
                "profit_margin": safe_float(fundamentals.get("profitMargin")),
                "debt_to_equity": safe_float(fundamentals.get("debtToEquity")),
                "return_on_equity": safe_float(fundamentals.get("returnOnEquity")),
                "pe_ratio": safe_float(valuation.get("peRatio")),
                "pb_ratio": safe_float(valuation.get("pbRatio")),
                "ps_ratio": safe_float(valuation.get("psRatio")),
                "peg_ratio": safe_float(valuation.get("pegRatio")),
                "ev_ebitda": safe_float(valuation.get("evEbitda")),
                "sector_rank": safe_int(ranking.get("sectorRank")),
                "industry_rank": safe_int(ranking.get("industryRank")),
                "overall_rank": safe_int(ranking.get("overallRank")),
                "source": "trading_central",
                "raw_data": raw_data
            }
        except Exception as e:
            logger.error(f"Error building quantamental scores: {e}")
            raise
    
    def build_hedge_fund_data(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build hedge fund data from TipRanks/eToro API response.
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed hedge fund data fields
        """
        try:
            # Handle list response
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            hedge_fund = raw_data.get("hedgeFundData", {})
            institutional = raw_data.get("institutional", {})
            
            # Position changes
            new_pos = safe_int(hedge_fund.get("newPositions", 0)) or 0
            increased = safe_int(hedge_fund.get("increasedPositions", 0)) or 0
            decreased = safe_int(hedge_fund.get("decreasedPositions", 0)) or 0
            closed = safe_int(hedge_fund.get("soldOutPositions", 0)) or 0
            
            # Calculate sentiment
            if increased + new_pos > decreased + closed:
                sentiment = SentimentType.BULLISH
            elif decreased + closed > increased + new_pos:
                sentiment = SentimentType.BEARISH
            else:
                sentiment = SentimentType.NEUTRAL
            
            return {
                "ticker": ticker,
                "timestamp": get_utc_now(),
                "institutional_ownership_pct": safe_float(institutional.get("ownershipPercent")),
                "hedge_fund_count": safe_int(hedge_fund.get("count")) or 0,
                "total_shares_held": safe_float(hedge_fund.get("totalSharesHeld")),
                "market_value_held": safe_float(hedge_fund.get("marketValue")),
                "new_positions": new_pos,
                "increased_positions": increased,
                "decreased_positions": decreased,
                "closed_positions": closed,
                "hedge_fund_sentiment": sentiment,
                "smart_money_score": safe_float(hedge_fund.get("smartScore")),
                "top_holders": hedge_fund.get("topHolders"),
                "shares_change_qoq": safe_float(hedge_fund.get("sharesChangeQoQ")),
                "ownership_change_qoq": safe_float(hedge_fund.get("ownershipChangeQoQ")),
                "source": "tipranks",
                "raw_data": raw_data
            }
        except Exception as e:
            logger.error(f"Error building hedge fund data: {e}")
            raise
    
    def build_crowd_statistics(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build crowd statistics from TipRanks API response.
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed crowd statistics fields
        """
        try:
            # Handle list response
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            crowd = raw_data.get("crowdWisdom", raw_data)
            
            bullish_pct = safe_float(crowd.get("bullishPercent"))
            bearish_pct = safe_float(crowd.get("bearishPercent"))
            
            # Determine sentiment
            if bullish_pct and bearish_pct:
                if bullish_pct > bearish_pct:
                    sentiment = SentimentType.BULLISH
                elif bearish_pct > bullish_pct:
                    sentiment = SentimentType.BEARISH
                else:
                    sentiment = SentimentType.NEUTRAL
            else:
                sentiment = None
            
            return {
                "ticker": ticker,
                "timestamp": get_utc_now(),
                "crowd_sentiment": sentiment,
                "sentiment_score": safe_float(crowd.get("sentimentScore")),
                "mentions_count": safe_int(crowd.get("mentionsCount")) or 0,
                "mentions_change": safe_float(crowd.get("mentionsChange")),
                "impressions": safe_int(crowd.get("impressions")) or 0,
                "engagement_rate": safe_float(crowd.get("engagementRate")),
                "bullish_percent": bullish_pct,
                "bearish_percent": bearish_pct,
                "neutral_percent": safe_float(crowd.get("neutralPercent")),
                "trending_score": safe_float(crowd.get("trendingScore")),
                "rank_day": safe_int(crowd.get("dailyRank")),
                "rank_week": safe_int(crowd.get("weeklyRank")),
                "total_posts": safe_int(crowd.get("totalPosts")) or 0,
                "unique_users": safe_int(crowd.get("uniqueUsers")) or 0,
                "avg_sentiment_post": safe_float(crowd.get("avgSentiment")),
                "source": "tipranks",
                "raw_data": raw_data
            }
        except Exception as e:
            logger.error(f"Error building crowd statistics: {e}")
            raise
    
    def build_blogger_sentiment(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build blogger sentiment from TipRanks API response.
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed blogger sentiment fields
        """
        try:
            # Handle list response
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            blogger = raw_data.get("bloggerSentiment", raw_data)
            
            bullish = safe_int(blogger.get("bullish", 0)) or 0
            bearish = safe_int(blogger.get("bearish", 0)) or 0
            neutral_count = safe_int(blogger.get("neutral", 0)) or 0
            total = bullish + bearish + neutral_count
            
            # Calculate percentages
            bullish_pct = (bullish / total * 100) if total > 0 else None
            bearish_pct = (bearish / total * 100) if total > 0 else None
            
            # Determine sentiment
            if bullish > bearish:
                sentiment = SentimentType.BULLISH
            elif bearish > bullish:
                sentiment = SentimentType.BEARISH
            else:
                sentiment = SentimentType.NEUTRAL
            
            return {
                "ticker": ticker,
                "timestamp": get_utc_now(),
                "blogger_sentiment": sentiment if total > 0 else None,
                "sentiment_score": safe_float(blogger.get("sentimentScore")),
                "total_articles": total,
                "bullish_articles": bullish,
                "bearish_articles": bearish,
                "neutral_articles": neutral_count,
                "bullish_percent": bullish_pct,
                "bearish_percent": bearish_pct,
                "avg_blogger_accuracy": safe_float(blogger.get("avgAccuracy")),
                "top_blogger_opinion": blogger.get("topBloggerOpinion"),
                "sentiment_change_1d": safe_float(blogger.get("change1d")),
                "sentiment_change_1w": safe_float(blogger.get("change1w")),
                "sentiment_change_1m": safe_float(blogger.get("change1m")),
                "source": "tipranks",
                "raw_data": raw_data
            }
        except Exception as e:
            logger.error(f"Error building blogger sentiment: {e}")
            raise
    
    def build_technical_indicators(
        self,
        raw_data: Dict[str, Any],
        ticker: str,
        timeframe: TimeframeType = TimeframeType.ONE_DAY
    ) -> Dict[str, Any]:
        """
        Build technical indicators from Trading Central API response.
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            timeframe: Indicator timeframe
            
        Returns:
            Dictionary with parsed technical indicator fields
        """
        try:
            # Handle list response
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            price = raw_data.get("price", {})
            indicators = raw_data.get("indicators", {})
            signals = raw_data.get("signals", {})
            levels = raw_data.get("levels", {})
            
            # Determine overall signal
            oscillator_sig = signals.get("oscillator")
            ma_sig = signals.get("movingAverage")
            overall_sig = signals.get("overall")
            
            return {
                "ticker": ticker,
                "timestamp": get_utc_now(),
                "timeframe": timeframe,
                "open_price": safe_float(price.get("open")),
                "high_price": safe_float(price.get("high")),
                "low_price": safe_float(price.get("low")),
                "close_price": safe_float(price.get("close")),
                "volume": safe_float(price.get("volume")),
                "sma_20": safe_float(indicators.get("sma20")),
                "sma_50": safe_float(indicators.get("sma50")),
                "sma_200": safe_float(indicators.get("sma200")),
                "ema_12": safe_float(indicators.get("ema12")),
                "ema_26": safe_float(indicators.get("ema26")),
                "rsi_14": safe_float(indicators.get("rsi14")),
                "stoch_k": safe_float(indicators.get("stochK")),
                "stoch_d": safe_float(indicators.get("stochD")),
                "cci": safe_float(indicators.get("cci")),
                "williams_r": safe_float(indicators.get("williamsR")),
                "macd": safe_float(indicators.get("macd")),
                "macd_signal": safe_float(indicators.get("macdSignal")),
                "macd_histogram": safe_float(indicators.get("macdHistogram")),
                "adx": safe_float(indicators.get("adx")),
                "plus_di": safe_float(indicators.get("plusDi")),
                "minus_di": safe_float(indicators.get("minusDi")),
                "atr": safe_float(indicators.get("atr")),
                "bollinger_upper": safe_float(indicators.get("bollingerUpper")),
                "bollinger_middle": safe_float(indicators.get("bollingerMiddle")),
                "bollinger_lower": safe_float(indicators.get("bollingerLower")),
                "support_1": safe_float(levels.get("support1")),
                "support_2": safe_float(levels.get("support2")),
                "resistance_1": safe_float(levels.get("resistance1")),
                "resistance_2": safe_float(levels.get("resistance2")),
                "pivot_point": safe_float(levels.get("pivot")),
                "oscillator_signal": determine_sentiment(
                    safe_float(oscillator_sig)
                ) if oscillator_sig else None,
                "moving_avg_signal": determine_sentiment(
                    safe_float(ma_sig)
                ) if ma_sig else None,
                "overall_signal": determine_sentiment(
                    safe_float(overall_sig)
                ) if overall_sig else None,
                "source": "trading_central",
                "raw_data": raw_data
            }
        except Exception as e:
            logger.error(f"Error building technical indicators: {e}")
            raise
    
    def build_target_prices(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> List[Dict[str, Any]]:
        """
        Build target price data from Trading Central API response.
        
        May return multiple records if there are multiple analysts.
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            List of dictionaries with parsed target price fields
        """
        try:
            # Handle both single and list responses
            if isinstance(raw_data, dict):
                targets = raw_data.get("targets", [raw_data])
            elif isinstance(raw_data, list):
                targets = raw_data
            else:
                targets = []
            
            results = []
            for target in targets:
                results.append({
                    "ticker": ticker,
                    "timestamp": get_utc_now(),
                    "analyst_name": target.get("analystName"),
                    "analyst_firm": target.get("firm"),
                    "target_price": safe_float(target.get("targetPrice")),
                    "previous_target": safe_float(target.get("previousTarget")),
                    "target_change": safe_float(target.get("change")),
                    "target_change_pct": safe_float(target.get("changePercent")),
                    "rating": self._map_rating(target.get("rating")),
                    "previous_rating": self._map_rating(target.get("previousRating")),
                    "rating_changed": target.get("ratingChanged", False),
                    "current_price_at_rating": safe_float(target.get("priceAtRating")),
                    "upside_to_target": safe_float(target.get("upside")),
                    "analyst_accuracy_score": safe_float(target.get("accuracy")),
                    "rating_date": self._parse_date(target.get("date")),
                    "source": "trading_central",
                    "raw_data": target
                })
            
            return results
        except Exception as e:
            logger.error(f"Error building target prices: {e}")
            raise
    
    def _map_rating(self, rating: Optional[str]) -> Optional[RatingType]:
        """Map string rating to RatingType enum"""
        if not rating:
            return None
        
        rating_lower = rating.lower()
        mapping = {
            "strong buy": RatingType.STRONG_BUY,
            "buy": RatingType.BUY,
            "hold": RatingType.HOLD,
            "neutral": RatingType.HOLD,
            "sell": RatingType.SELL,
            "strong sell": RatingType.STRONG_SELL,
            "underperform": RatingType.SELL,
            "outperform": RatingType.BUY,
        }
        return mapping.get(rating_lower)
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    # ============================================
    # Notebook API Response Builder Methods
    # These methods match the exact JSON paths from the Jupyter notebook (Final.ipynb)
    # ============================================

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

    def build_notebook_news_sentiment(
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
            logger.error(f"Error building notebook news sentiment: {e}")
            raise

    def build_notebook_hedge_fund(
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
            logger.error(f"Error building notebook hedge fund: {e}")
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

    def build_notebook_crowd_stats(
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
            logger.error(f"Error building notebook crowd stats: {e}")
            raise

    def build_notebook_blogger_sentiment(
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
            logger.error(f"Error building notebook blogger sentiment: {e}")
            raise

    def build_notebook_quantamental(
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
            logger.error(f"Error building notebook quantamental: {e}")
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

    def build_notebook_target_price(
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
            logger.error(f"Error building notebook target price: {e}")
            raise

    def build_article_distribution(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build article distribution data matching notebook API structure.
        
        Extracts from: topics
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed article distribution fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            
            topics = raw_data.get('topics', []) or []
            
            news_count = 0
            social_count = 0
            web_count = 0
            
            for topic in topics:
                topic_type = topic.get('type', '').lower()
                count = safe_int(topic.get('count', 0)) or 0
                if topic_type == 'news':
                    news_count = count
                elif topic_type == 'social':
                    social_count = count
                elif topic_type == 'web':
                    web_count = count
            
            total = news_count + social_count + web_count
            
            return {
                "ticker": ticker,
                "total_articles": total,
                "news_count": news_count,
                "news_percentage": (news_count / total * 100) if total > 0 else 0.0,
                "social_count": social_count,
                "social_percentage": (social_count / total * 100) if total > 0 else 0.0,
                "web_count": web_count,
                "web_percentage": (web_count / total * 100) if total > 0 else 0.0,
            }
        except Exception as e:
            logger.error(f"Error building article distribution: {e}")
            raise

    def build_article_sentiment(
        self,
        raw_data: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """
        Build article sentiment data matching notebook API structure.
        
        Handles sentiment, subjectivity, confidence fields
        
        Args:
            raw_data: Raw API response
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with parsed article sentiment fields
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            raw_data = raw_data or {}
            
            sentiment = raw_data.get('sentiment', {}) or {}
            subjectivity = raw_data.get('subjectivity', {}) or {}
            confidence = raw_data.get('confidence', {}) or {}
            
            return {
                "ticker": ticker,
                "sentiment_id": sentiment.get('id'),
                "sentiment_label": sentiment.get('label'),
                "sentiment_value": safe_int(sentiment.get('value')),
                "subjectivity_id": subjectivity.get('id'),
                "subjectivity_label": subjectivity.get('label'),
                "subjectivity_value": safe_int(subjectivity.get('value')),
                "confidence_id": confidence.get('id'),
                "confidence_name": confidence.get('name'),
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
            support = raw_item.get('support', {}) or {}
            resistance = raw_item.get('resistance', {}) or {}
            
            return {
                "symbol": instrument.get('symbol', ''),
                "date": raw_item.get('date', ''),
                "exchange": instrument.get('exchange', ''),
                "support_10": safe_float(support.get('10')),
                "resistance_10": safe_float(resistance.get('10')),
                "support_20": safe_float(support.get('20')),
                "resistance_20": safe_float(resistance.get('20')),
                "support_40": safe_float(support.get('40')),
                "resistance_40": safe_float(resistance.get('40')),
                "support_100": safe_float(support.get('100')),
                "resistance_100": safe_float(resistance.get('100')),
                "support_250": safe_float(support.get('250')),
                "resistance_250": safe_float(resistance.get('250')),
                "support_500": safe_float(support.get('500')),
                "resistance_500": safe_float(resistance.get('500')),
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
        
        Extracts from: stops, timestamps arrays
        
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
                recommended_stop = safe_float(stops[-1])
            if timestamps and len(timestamps) > 0:
                calculation_timestamp = timestamps[-1]
            
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
        raw_data: List[Dict[str, Any]],
        ticker: str,
        is_active: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Build chart events data matching notebook API structure.
        
        Flattens nested event columns
        
        Args:
            raw_data: Raw API response list
            ticker: Stock ticker symbol
            is_active: Whether these are active events
            
        Returns:
            List of dictionaries with flattened chart event data
        """
        try:
            if not isinstance(raw_data, list):
                raw_data = [raw_data] if raw_data else []
            
            results = []
            for item in raw_data:
                if not item:
                    continue
                    
                event = {
                    "ticker": ticker,
                    "is_active": is_active,
                    "event_id": item.get('id'),
                    "event_type": item.get('type'),
                    "event_name": item.get('name'),
                    "start_date": item.get('startDate'),
                    "end_date": item.get('endDate'),
                    "price": safe_float(item.get('price')),
                    "target_price": safe_float(item.get('targetPrice')),
                    "stop_price": safe_float(item.get('stopPrice')),
                }
                results.append(event)
            
            return results
        except Exception as e:
            logger.error(f"Error building chart events dataframe: {e}")
            raise

    def build_technical_summaries_dataframe(
        self,
        raw_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Build technical summaries data matching notebook API structure.
        
        Extracts from scores with multiple categories
        
        Args:
            raw_data: Raw API response
            
        Returns:
            List of dictionaries with technical summary data
        """
        try:
            if isinstance(raw_data, list):
                raw_data = raw_data[0] if raw_data else {}
            raw_data = raw_data or {}
            
            scores = raw_data.get('scores', {}) or {}
            
            results = []
            for category, score_data in scores.items():
                if isinstance(score_data, dict):
                    results.append({
                        "category": category,
                        "score": safe_float(score_data.get('score')),
                        "signal": score_data.get('signal'),
                        "trend": score_data.get('trend'),
                    })
                elif isinstance(score_data, (int, float)):
                    results.append({
                        "category": category,
                        "score": safe_float(score_data),
                        "signal": None,
                        "trend": None,
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error building technical summaries dataframe: {e}")
            raise

    def build_quantamental_timeseries_dataframe(
        self,
        raw_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Build quantamental timeseries data matching notebook API structure.
        
        Returns DataFrame-like structure with timestamps and scores
        
        Args:
            raw_data: Raw API response
            
        Returns:
            List of dictionaries with timeseries data
        """
        try:
            if isinstance(raw_data, list):
                return raw_data
            
            raw_data = raw_data or {}
            timestamps = raw_data.get('timestamps', [])
            scores = raw_data.get('scores', [])
            
            results = []
            for i, ts in enumerate(timestamps):
                score = scores[i] if i < len(scores) else None
                results.append({
                    "timestamp": ts,
                    "score": safe_float(score),
                })
            
            return results
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
