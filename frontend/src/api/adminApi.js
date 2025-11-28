import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

export const adminApi = {
  // Ticker endpoints
  getTickers: (includeInactive = false) => 
    api.get(`/api/config/tickers?include_inactive=${includeInactive}`),
  getTicker: (symbol) => api.get(`/api/config/tickers/${symbol}`),
  createTicker: (data) => api.post('/api/config/tickers', data),
  updateTicker: (symbol, data) => api.put(`/api/config/tickers/${symbol}`, data),
  deleteTicker: (symbol) => api.delete(`/api/config/tickers/${symbol}`),

  // API Key endpoints
  getAPIKeys: (includeInactive = false) => 
    api.get(`/api/config/api-keys?include_inactive=${includeInactive}`),
  createAPIKey: (data) => api.post('/api/config/api-keys', data),
  updateAPIKey: (serviceName, data) => api.put(`/api/config/api-keys/${serviceName}`, data),

  // Config management
  getConfigStatus: () => api.get('/api/config/status'),
  reloadConfig: () => api.post('/api/config/reload'),
};

export default adminApi;
