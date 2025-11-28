import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

export const adminApi = {
  // Ticker endpoints
  getTickers: (includeInactive = false) => 
    api.get(`/config/tickers${includeInactive ? '?include_inactive=true' : ''}`),
  getTicker: (symbol) => 
    api.get(`/config/tickers/${symbol}`),
  createTicker: (data) => 
    api.post('/config/tickers', data),
  updateTicker: (symbol, data) => 
    api.put(`/config/tickers/${symbol}`, data),
  deleteTicker: (symbol) => 
    api.delete(`/config/tickers/${symbol}`),

  // API Key endpoints
  getAPIKeys: (includeInactive = false) => 
    api.get(`/config/api-keys${includeInactive ? '?include_inactive=true' : ''}`),
  getAPIKey: (serviceName) => 
    api.get(`/config/api-keys/${serviceName}`),
  createAPIKey: (data) => 
    api.post('/config/api-keys', data),
  updateAPIKey: (serviceName, data) => 
    api.put(`/config/api-keys/${serviceName}`, data),

  // Config management
  getConfigStatus: () => 
    api.get('/config/status'),
  reloadConfig: () => 
    api.post('/config/reload'),
};

export default adminApi;
