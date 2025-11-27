// Default tickers to track
export const DEFAULT_TICKERS = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META'];

// Time range options
export const TIME_RANGES = [
  { value: '1h', label: '1 Hour', hours: 1 },
  { value: '2h', label: '2 Hours', hours: 2 },
  { value: '4h', label: '4 Hours', hours: 4 },
  { value: '6h', label: '6 Hours', hours: 6 },
  { value: '12h', label: '12 Hours', hours: 12 },
  { value: '1d', label: '1 Day', hours: 24 },
  { value: '1w', label: '1 Week', hours: 168 },
];

// Data types for comparison
export const DATA_TYPES = [
  { value: 'analyst_ratings', label: 'Analyst Ratings' },
  { value: 'news_sentiment', label: 'News Sentiment' },
  { value: 'quantamental', label: 'Quantamental Scores' },
  { value: 'hedge_fund', label: 'Hedge Fund Activity' },
  { value: 'crowd', label: 'Crowd Sentiment' },
  { value: 'technical', label: 'Technical Indicators' },
];

// Technical indicator timeframes
export const TECHNICAL_TIMEFRAMES = [
  { value: '1h', label: '1H' },
  { value: '4h', label: '4H' },
  { value: '1d', label: '1D' },
  { value: '1w', label: '1W' },
];

// Alert severity levels
export const ALERT_SEVERITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
};

// Color palette for charts
export const CHART_COLORS = {
  primary: '#1976d2',
  secondary: '#dc004e',
  success: '#2e7d32',
  error: '#d32f2f',
  warning: '#ff9800',
  info: '#0288d1',
  grey: '#9e9e9e',
};

// Rating colors
export const RATING_COLORS = {
  strongBuy: 'rgba(76, 175, 80, 0.8)',
  buy: 'rgba(139, 195, 74, 0.8)',
  hold: 'rgba(255, 193, 7, 0.8)',
  sell: 'rgba(255, 152, 0, 0.8)',
  strongSell: 'rgba(244, 67, 54, 0.8)',
};

// Sentiment thresholds
export const SENTIMENT_THRESHOLDS = {
  veryBullish: 0.5,
  bullish: 0.2,
  neutral: -0.2,
  bearish: -0.5,
};

// Technical indicator thresholds
export const TECHNICAL_THRESHOLDS = {
  RSI_OVERBOUGHT: 70,
  RSI_OVERSOLD: 30,
};

// Platform distribution defaults (when breakdown not available)
export const PLATFORM_DISTRIBUTION = {
  TWITTER: 0.4,
  REDDIT: 0.3,
  STOCKTWITS: 0.3,
};

// API refresh intervals (in milliseconds)
export const REFRESH_INTERVALS = {
  realtime: 30000,    // 30 seconds
  fast: 60000,        // 1 minute
  normal: 300000,     // 5 minutes
  slow: 600000,       // 10 minutes
};

// Drawer width for layout
export const DRAWER_WIDTH = 240;

// Breakpoints
export const BREAKPOINTS = {
  xs: 0,
  sm: 600,
  md: 900,
  lg: 1200,
  xl: 1536,
};
