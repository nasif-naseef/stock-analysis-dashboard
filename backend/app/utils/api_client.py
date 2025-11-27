"""
API Client Utility

This module contains the APIClient class for making HTTP requests to external APIs
with connection pooling, caching, rate limiting, error handling, and retries.
"""
import time
import logging
from typing import Optional, Dict, Any, List
from collections import OrderedDict
from threading import Lock

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import settings

logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Simple in-memory cache with TTL support.
    
    Thread-safe cache implementation using OrderedDict for LRU behavior.
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of items to store
            ttl_seconds: Time-to-live for cached items in seconds
        """
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if not expired"""
        with self._lock:
            if key not in self._cache:
                return None
            
            # Check if expired
            if time.time() - self._timestamps[key] > self._ttl:
                self._remove(key)
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        with self._lock:
            # Remove oldest if at capacity
            while len(self._cache) >= self._max_size:
                oldest = next(iter(self._cache))
                self._remove(oldest)
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def _remove(self, key: str) -> None:
        """Remove item from cache (internal, not thread-safe)"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Clear all items from cache"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()


class RateLimiter:
    """
    Simple rate limiter using token bucket algorithm.
    
    Limits requests to a maximum number per second.
    """
    
    def __init__(self, requests_per_second: float = 10.0):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum requests per second
        """
        self._requests_per_second = requests_per_second
        self._min_interval = 1.0 / requests_per_second
        self._last_request_time = 0.0
        self._lock = Lock()
    
    def acquire(self) -> None:
        """Wait if necessary to stay within rate limit"""
        with self._lock:
            current_time = time.time()
            elapsed = current_time - self._last_request_time
            
            if elapsed < self._min_interval:
                sleep_time = self._min_interval - elapsed
                time.sleep(sleep_time)
            
            self._last_request_time = time.time()


class APIClient:
    """
    HTTP client for external API requests.
    
    Features:
    - Connection pooling via requests.Session
    - Configurable retries with exponential backoff
    - In-memory caching
    - Rate limiting
    - Timeout configuration
    - Error handling
    """
    
    # TipRanks API endpoints
    TIPRANKS_BASE_URL = "https://widgets.tipranks.com/api"
    TIPRANKS_ANALYST_RATINGS = "/IB/analystratings"
    TIPRANKS_NEWS = "/IB/news"
    TIPRANKS_STOCK_OVERVIEW = "/widgets/stockAnalysisOverview"
    TIPRANKS_ETORO_DATA = "/etoro/dataForTicker"
    # Note: crowd and blogger endpoints use path parameters, not query params
    TIPRANKS_CROWD_DATA = "/widgets/crowd/generalData"  # Append /{ticker} as path param
    TIPRANKS_BLOGGERS = "/widgets/bloggers"  # Append /{ticker} as path param
    
    # Trading Central API endpoints
    TC_BASE_URL = "https://api.tradingcentral.com"
    # V4 APIs use Bearer token in header
    TC_QUANTAMENTAL = "/quantamental/v4"
    TC_TARGET_PRICES = "/target-prices/v4"
    TC_ARTICLE_ANALYTICS = "/article-analytics/v4/entities"  # Append /{entity_id}
    TC_ARTICLE_SENTIMENTS = "/article-sentiments/v5/entities"  # Append /{entity_id}
    # V3 APIs use token in URL query parameter
    TC_SUPPORT_RESISTANCE = "/supportandresistance/v3"  # Uses ?token= and ?id=
    TC_STOP_TIMESERIES = "/stoptimeseries/v3"  # Uses ?token= and ?id=
    TC_INSTRUMENT_EVENTS = "/instrumentevents/v3"  # Uses ?token= and ?id=
    TC_TECHNICAL_SUMMARIES = "/technicalsummaries/v3"  # Uses ?token= and ?id=
    
    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 3,
        cache_ttl: int = 300,
        rate_limit: float = 10.0
    ):
        """
        Initialize API client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            cache_ttl: Cache time-to-live in seconds
            rate_limit: Maximum requests per second
        """
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize session with connection pooling
        self.session = self._create_session()
        
        # Initialize cache and rate limiter
        self.cache = SimpleCache(max_size=1000, ttl_seconds=cache_ttl)
        self.rate_limiter = RateLimiter(requests_per_second=rate_limit)
        
        # Trading Central auth token
        self.tc_token = settings.TRADING_CENTRAL_TOKEN
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry configuration"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # 1s, 2s, 4s
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        return session
    
    def _build_url(self, base_url: str, endpoint: str, path_params: List[str] = None) -> str:
        """
        Build URL with proper string concatenation.
        
        This replaces urljoin which incorrectly handles paths with leading slashes.
        
        Args:
            base_url: Base URL (e.g., "https://widgets.tipranks.com/api")
            endpoint: API endpoint path (e.g., "/widgets/crowd/generalData")
            path_params: Optional list of path parameters to append
            
        Returns:
            Properly constructed URL
        """
        # Normalize base URL (ensure trailing slash)
        base = base_url.rstrip('/') + '/'
        
        # Normalize endpoint (remove leading slash)
        endpoint = endpoint.lstrip('/')
        
        # Build path parameters if any
        if path_params:
            path_suffix = '/' + '/'.join(str(p) for p in path_params)
        else:
            path_suffix = ''
        
        # Concatenate: base + endpoint + path_params
        return f"{base}{endpoint}{path_suffix}"
    
    def fetch(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_cache: bool = True,
        method: str = "GET"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data from URL with caching and rate limiting.
        
        Args:
            url: The URL to fetch
            params: Query parameters
            headers: Additional headers
            use_cache: Whether to use caching
            method: HTTP method (GET or POST)
            
        Returns:
            JSON response as dictionary, or None on error
        """
        # Build cache key
        cache_key = f"{method}:{url}:{str(params)}"
        
        # Check cache first
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {url}")
                return cached
        
        # Apply rate limiting
        self.rate_limiter.acquire()
        
        try:
            logger.debug(f"Fetching {url} with params {params}")
            
            if method.upper() == "GET":
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                response = self.session.post(
                    url,
                    json=params,
                    headers=headers,
                    timeout=self.timeout
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Cache successful response
            if use_cache:
                self.cache.set(cache_key, data)
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching {url}: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON decode error for {url}: {e}")
            return None
    
    def fetch_tipranks(
        self,
        endpoint: str,
        ticker: str,
        extra_params: Optional[Dict[str, Any]] = None,
        use_path_param: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data from TipRanks API.
        
        Args:
            endpoint: API endpoint path
            ticker: Stock ticker symbol
            extra_params: Additional query parameters
            use_path_param: If True, append ticker to URL path instead of query param
            
        Returns:
            API response as dictionary
        """
        if use_path_param:
            # Append ticker to URL path (e.g., /api/widgets/crowd/generalData/AAPL)
            url = self._build_url(self.TIPRANKS_BASE_URL, endpoint, [ticker])
            params = extra_params or {}
        else:
            # Use ticker as query parameter (e.g., ?ticker=AAPL)
            url = self._build_url(self.TIPRANKS_BASE_URL, endpoint)
            params = {"ticker": ticker}
            if extra_params:
                params.update(extra_params)
        
        return self.fetch(url, params=params)
    
    def fetch_trading_central(
        self,
        endpoint: str,
        ticker_id: str,
        extra_params: Optional[Dict[str, Any]] = None,
        use_path_id: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data from Trading Central V4 API with Bearer token in header.
        
        Args:
            endpoint: API endpoint path
            ticker_id: Trading Central instrument ID
            extra_params: Additional query parameters
            use_path_id: If True, append ID to URL path instead of query param
            
        Returns:
            API response as dictionary
        """
        if not self.tc_token:
            logger.warning("Trading Central token not configured")
            return None
        
        if use_path_id:
            # Append ID to URL path (e.g., /article-analytics/v4/entities/EQ-0C00000ADA)
            url = self._build_url(self.TC_BASE_URL, endpoint, [ticker_id])
            params = extra_params or {}
        else:
            # Use ID as query parameter
            url = self._build_url(self.TC_BASE_URL, endpoint)
            params = {"id": ticker_id}
            if extra_params:
                params.update(extra_params)
        
        headers = {"Authorization": f"Bearer {self.tc_token}"}
        
        return self.fetch(url, params=params, headers=headers)
    
    def fetch_trading_central_v3(
        self,
        endpoint: str,
        ticker_id: str,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data from Trading Central V3 API with token in URL query parameter.
        
        V3 APIs use token as a query parameter instead of Bearer header.
        
        Args:
            endpoint: API endpoint path
            ticker_id: Trading Central V3 instrument ID (e.g., "US-303648")
            extra_params: Additional query parameters
            
        Returns:
            API response as dictionary
        """
        if not self.tc_token:
            logger.warning("Trading Central token not configured")
            return None
        
        url = self._build_url(self.TC_BASE_URL, endpoint)
        params = {"id": ticker_id, "token": self.tc_token}
        if extra_params:
            params.update(extra_params)
        
        # No Authorization header for V3 APIs - token is in URL
        return self.fetch(url, params=params)
    
    def fetch_tipranks_analyst_ratings(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch analyst ratings from TipRanks"""
        return self.fetch_tipranks(self.TIPRANKS_ANALYST_RATINGS, ticker)
    
    def fetch_tipranks_news(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch news from TipRanks"""
        return self.fetch_tipranks(self.TIPRANKS_NEWS, ticker)
    
    def fetch_tipranks_stock_overview(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch stock overview from TipRanks"""
        return self.fetch_tipranks(self.TIPRANKS_STOCK_OVERVIEW, ticker)
    
    def fetch_tipranks_etoro_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch eToro data from TipRanks"""
        return self.fetch_tipranks(self.TIPRANKS_ETORO_DATA, ticker)
    
    def fetch_tipranks_crowd_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch crowd data from TipRanks using path parameter"""
        return self.fetch_tipranks(self.TIPRANKS_CROWD_DATA, ticker, use_path_param=True)
    
    def fetch_tipranks_bloggers(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch blogger sentiment from TipRanks using path parameter"""
        return self.fetch_tipranks(self.TIPRANKS_BLOGGERS, ticker, use_path_param=True)
    
    def fetch_tc_quantamental(self, ticker_id: str) -> Optional[Dict[str, Any]]:
        """Fetch quantamental data from Trading Central V4 API"""
        return self.fetch_trading_central(self.TC_QUANTAMENTAL, ticker_id)
    
    def fetch_tc_target_prices(self, ticker_id: str) -> Optional[Dict[str, Any]]:
        """Fetch target prices from Trading Central V4 API"""
        return self.fetch_trading_central(self.TC_TARGET_PRICES, ticker_id)
    
    def fetch_tc_article_analytics(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Fetch article analytics from Trading Central V4 API with entity ID in path"""
        return self.fetch_trading_central(self.TC_ARTICLE_ANALYTICS, entity_id, use_path_id=True)
    
    def fetch_tc_article_sentiments(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Fetch article sentiments from Trading Central V5 API with entity ID in path"""
        # Note: V5 article-sentiments API uses same authentication pattern as V4 (Bearer token in header)
        return self.fetch_trading_central(self.TC_ARTICLE_SENTIMENTS, entity_id, use_path_id=True)
    
    def fetch_tc_technical_summaries(self, ticker_id: str) -> Optional[Dict[str, Any]]:
        """Fetch technical summaries from Trading Central V3 API with token in URL"""
        return self.fetch_trading_central_v3(self.TC_TECHNICAL_SUMMARIES, ticker_id)
    
    def fetch_tc_support_resistance(self, ticker_id: str) -> Optional[Dict[str, Any]]:
        """Fetch support/resistance levels from Trading Central V3 API with token in URL"""
        return self.fetch_trading_central_v3(self.TC_SUPPORT_RESISTANCE, ticker_id)
    
    def fetch_tc_stop_timeseries(self, ticker_id: str) -> Optional[Dict[str, Any]]:
        """Fetch stop timeseries from Trading Central V3 API with token in URL"""
        return self.fetch_trading_central_v3(self.TC_STOP_TIMESERIES, ticker_id)
    
    def fetch_tc_instrument_events(self, ticker_id: str) -> Optional[Dict[str, Any]]:
        """Fetch instrument events from Trading Central V3 API with token in URL"""
        return self.fetch_trading_central_v3(self.TC_INSTRUMENT_EVENTS, ticker_id)
    
    def close(self) -> None:
        """Close the session and release resources"""
        self.session.close()
        self.cache.clear()
