import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

export const stockApi = {
  // Current Data
  getAnalystRatings: (ticker) => api.get(`/analyst-ratings/${ticker}`),
  getAllAnalystRatings: () => api.get('/analyst-ratings'),
  getNewsSentiment: (ticker) => api.get(`/news-sentiment/${ticker}`),
  getQuantamental: (ticker) => api.get(`/quantamental-scores/${ticker}`),
  getHedgeFund: (ticker) => api.get(`/hedge-fund-data/${ticker}`),
  getCrowd: (ticker) => api.get(`/crowd-statistics/${ticker}`),
  getTechnical: (ticker, timeframe) => 
    api.get(`/technical-indicators/${ticker}${timeframe ? `?timeframe=${timeframe}` : ''}`),
  getTargetPrice: (ticker) => api.get(`/target-prices/${ticker}`),
  getBloggerSentiment: (ticker) => api.get(`/blogger-sentiment/${ticker}`),
  
  // Historical Data
  getHistoricalAnalystRatings: (ticker, hoursAgo) => 
    api.get(`/history/analyst-ratings/${ticker}?hours_ago=${hoursAgo}`),
  
  // Comparison
  compareOverTime: (ticker, periods, dataType) => 
    api.get(`/compare/${ticker}?periods=${periods}${dataType ? `&data_type=${dataType}` : ''}`),
  compareTickers: (tickers, period, dataType) => 
    api.get(`/compare/tickers/multi?tickers=${tickers}&period=${period}${dataType ? `&data_type=${dataType}` : ''}`),
  
  // Collection
  triggerCollection: (ticker) => 
    ticker ? api.post(`/v1/collection/trigger?ticker=${ticker}`) : api.post('/v1/collection/trigger'),
  getCollectionStatus: () => api.get('/v1/collection/status'),
  getConfiguredTickers: () => api.get('/v1/collection/tickers'),
  
  // Dashboard
  getDashboardOverview: () => api.get('/dashboard/overview'),
  getDashboardAlerts: (hours = 24) => api.get(`/dashboard/alerts?hours_ago=${hours}`),
  getTickerOverview: (ticker) => api.get(`/dashboard/ticker/${ticker}`),
  getCollectionSummary: (hours = 24) => api.get(`/dashboard/collection-summary?hours_ago=${hours}`)
};

export default stockApi;
