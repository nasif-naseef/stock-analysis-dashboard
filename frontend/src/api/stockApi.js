import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Configuration constants
const DEFAULT_TIMEOUT = 15000;
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: DEFAULT_TIMEOUT,
  headers: { 'Content-Type': 'application/json' }
});

/**
 * Retry logic for failed requests
 * @param {Function} fn - The function to retry
 * @param {number} retries - Number of retries remaining
 * @param {number} delay - Delay between retries
 * @returns {Promise} - Result of the function
 */
const retryWithDelay = async (fn, retries = MAX_RETRIES, delay = RETRY_DELAY) => {
  try {
    return await fn();
  } catch (error) {
    // Only retry on network errors or 5xx server errors
    const shouldRetry = 
      retries > 0 && 
      (error.code === 'ERR_NETWORK' || 
       error.code === 'ECONNABORTED' ||
       (error.response && error.response.status >= 500 && error.response.status < 600));
    
    if (shouldRetry) {
      await new Promise(resolve => setTimeout(resolve, delay));
      return retryWithDelay(fn, retries - 1, delay * 2);
    }
    throw error;
  }
};

/**
 * Request interceptor for adding common headers and logging
 */
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling and logging
 */
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Log error details in development
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        message: error.message,
      });
    }

    // Enhance error with additional context
    if (error.response) {
      error.isServerError = error.response.status >= 500;
      error.isClientError = error.response.status >= 400 && error.response.status < 500;
      error.isNotFound = error.response.status === 404;
    } else if (error.code === 'ECONNABORTED') {
      error.isTimeout = true;
    } else if (error.code === 'ERR_NETWORK') {
      error.isNetworkError = true;
    }

    return Promise.reject(error);
  }
);

/**
 * Make API request with automatic retry for transient failures
 */
const makeRequest = (requestFn) => {
  return retryWithDelay(requestFn);
};

export const stockApi = {
  // Current Data - with retry logic
  getAnalystRatings: (ticker) => makeRequest(() => api.get(`/analyst-ratings/${ticker}`)),
  getAllAnalystRatings: () => makeRequest(() => api.get('/analyst-ratings')),
  getNewsSentiment: (ticker) => makeRequest(() => api.get(`/news-sentiment/${ticker}`)),
  getQuantamental: (ticker) => makeRequest(() => api.get(`/quantamental-scores/${ticker}`)),
  getHedgeFund: (ticker) => makeRequest(() => api.get(`/hedge-fund-data/${ticker}`)),
  getCrowd: (ticker) => makeRequest(() => api.get(`/crowd-statistics/${ticker}`)),
  getTechnical: (ticker, timeframe) => 
    makeRequest(() => api.get(`/technical-indicators/${ticker}${timeframe ? `?timeframe=${timeframe}` : ''}`)),
  getTargetPrice: (ticker) => makeRequest(() => api.get(`/target-prices/${ticker}`)),
  getBloggerSentiment: (ticker) => makeRequest(() => api.get(`/blogger-sentiment/${ticker}`)),
  
  // New Stock Data APIs - matching notebook API structure
  getAnalystConsensus: (ticker) => makeRequest(() => api.get(`/stock/analyst/consensus/${ticker}`)),
  getAnalystConsensusHistory: (ticker) => makeRequest(() => api.get(`/stock/analyst/history/${ticker}`)),
  getStockNewsSentiment: (ticker) => makeRequest(() => api.get(`/stock/news/sentiment/${ticker}`)),
  getNewsArticles: (ticker) => makeRequest(() => api.get(`/stock/news/articles/${ticker}`)),
  getHedgeFundConfidence: (ticker) => makeRequest(() => api.get(`/stock/hedge-fund/${ticker}`)),
  getInsiderScore: (ticker) => makeRequest(() => api.get(`/stock/insider-score/${ticker}`)),
  getCrowdStats: (ticker, statsType = 'all') => 
    makeRequest(() => api.get(`/stock/crowd/stats/${ticker}?stats_type=${statsType}`)),
  getStockBloggerSentiment: (ticker) => makeRequest(() => api.get(`/stock/blogger/sentiment/${ticker}`)),
  getQuantamentalScores: (ticker) => makeRequest(() => api.get(`/stock/quantamental/${ticker}`)),
  getQuantamentalTimeseries: (ticker) => makeRequest(() => api.get(`/stock/quantamental/timeseries/${ticker}`)),
  getStockTargetPrices: (ticker) => makeRequest(() => api.get(`/stock/target-prices/${ticker}`)),
  getArticleDistribution: (ticker) => makeRequest(() => api.get(`/stock/articles/distribution/${ticker}`)),
  getArticleSentiment: (ticker) => makeRequest(() => api.get(`/stock/articles/sentiment/${ticker}`)),
  getSupportResistance: (ticker, date) => 
    makeRequest(() => api.get(`/stock/support-resistance/${ticker}${date ? `?date=${date}` : ''}`)),
  getStopLoss: (ticker, options = {}) => {
    const params = new URLSearchParams();
    if (options.stop_type) params.append('stop_type', options.stop_type);
    if (options.direction) params.append('direction', options.direction);
    if (options.tightness) params.append('tightness', options.tightness);
    if (options.priceperiod) params.append('priceperiod', options.priceperiod);
    const queryString = params.toString();
    return makeRequest(() => api.get(`/stock/stop-loss/${ticker}${queryString ? `?${queryString}` : ''}`));
  },
  getChartEvents: (ticker, active = true, priceperiod = 'daily') => 
    makeRequest(() => api.get(`/stock/chart-events/${ticker}?active=${active}&priceperiod=${priceperiod}`)),
  getChartEventsCombined: (ticker, priceperiod = 'daily') => 
    makeRequest(() => api.get(`/stock/chart-events/combined/${ticker}?priceperiod=${priceperiod}`)),
  getTechnicalSummaries: (ticker, category) => 
    makeRequest(() => api.get(`/stock/technical-summaries/${ticker}${category ? `?category=${category}` : ''}`)),
  getStockOverview: (ticker) => makeRequest(() => api.get(`/stock/overview/${ticker}`)),
  
  // Historical Data - with retry logic
  getHistoricalAnalystRatings: (ticker, hoursAgo) => 
    makeRequest(() => api.get(`/history/analyst-ratings/${ticker}?hours_ago=${hoursAgo}`)),
  
  // Comparison - with retry logic
  compareOverTime: (ticker, periods, dataType) => 
    makeRequest(() => api.get(`/compare/${ticker}?periods=${periods}${dataType ? `&data_type=${dataType}` : ''}`)),
  compareTickers: (tickers, period, dataType) => 
    makeRequest(() => api.get(`/compare/tickers/multi?tickers=${tickers}&period=${period}${dataType ? `&data_type=${dataType}` : ''}`)),
  
  // Collection - with retry logic
  triggerCollection: (ticker) => 
    makeRequest(() => ticker ? api.post(`/v1/collection/trigger?ticker=${ticker}`) : api.post('/v1/collection/trigger')),
  getCollectionStatus: () => makeRequest(() => api.get('/v1/collection/status')),
  getConfiguredTickers: () => makeRequest(() => api.get('/v1/collection/tickers')),
  
  // Dashboard - with retry logic
  getDashboardOverview: () => makeRequest(() => api.get('/dashboard/overview')),
  getDashboardAlerts: (hours = 24) => makeRequest(() => api.get(`/dashboard/alerts?hours_ago=${hours}`)),
  getTickerOverview: (ticker) => makeRequest(() => api.get(`/dashboard/ticker/${ticker}`)),
  getCollectionSummary: (hours = 24) => makeRequest(() => api.get(`/dashboard/collection-summary?hours_ago=${hours}`))
};

export default stockApi;
