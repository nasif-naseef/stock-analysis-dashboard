import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Configuration constants
const DEFAULT_TIMEOUT = 15000;
const MAX_RETRIES = 2;
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
 * Request interceptor for logging
 */
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    console.error('Admin API request error:', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling
 */
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Log error details in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Admin API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        message: error.message,
        detail: error.response?.data?.detail,
      });
    }

    // Enhance error with additional context
    if (error.response) {
      error.isServerError = error.response.status >= 500;
      error.isClientError = error.response.status >= 400 && error.response.status < 500;
      error.isNotFound = error.response.status === 404;
      error.isConflict = error.response.status === 409;
      error.isValidationError = error.response.status === 422;
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

export const adminApi = {
  // Ticker endpoints - with retry logic
  getTickers: (includeInactive = false) => 
    makeRequest(() => api.get(`/config/tickers${includeInactive ? '?include_inactive=true' : ''}`)),
  getTicker: (symbol) => 
    makeRequest(() => api.get(`/config/tickers/${symbol}`)),
  createTicker: (data) => 
    makeRequest(() => api.post('/config/tickers', data)),
  updateTicker: (symbol, data) => 
    makeRequest(() => api.put(`/config/tickers/${symbol}`, data)),
  deleteTicker: (symbol) => 
    makeRequest(() => api.delete(`/config/tickers/${symbol}`)),

  // API Key endpoints - with retry logic
  getAPIKeys: (includeInactive = false) => 
    makeRequest(() => api.get(`/config/api-keys${includeInactive ? '?include_inactive=true' : ''}`)),
  getAPIKey: (serviceName) => 
    makeRequest(() => api.get(`/config/api-keys/${serviceName}`)),
  createAPIKey: (data) => 
    makeRequest(() => api.post('/config/api-keys', data)),
  updateAPIKey: (serviceName, data) => 
    makeRequest(() => api.put(`/config/api-keys/${serviceName}`, data)),

  // Config management - with retry logic
  getConfigStatus: () => 
    makeRequest(() => api.get('/config/status')),
  reloadConfig: () => 
    makeRequest(() => api.post('/config/reload')),
};

export default adminApi;
