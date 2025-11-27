import { format, parseISO, formatDistanceToNow } from 'date-fns';

/**
 * Format a number with thousands separators
 */
export const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return 'N/A';
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(num);
};

/**
 * Format a large number (millions, billions, etc.)
 */
export const formatLargeNumber = (num) => {
  if (num === null || num === undefined) return 'N/A';
  
  const absNum = Math.abs(num);
  const sign = num < 0 ? '-' : '';
  
  if (absNum >= 1e12) return `${sign}${(absNum / 1e12).toFixed(2)}T`;
  if (absNum >= 1e9) return `${sign}${(absNum / 1e9).toFixed(2)}B`;
  if (absNum >= 1e6) return `${sign}${(absNum / 1e6).toFixed(2)}M`;
  if (absNum >= 1e3) return `${sign}${(absNum / 1e3).toFixed(2)}K`;
  
  return formatNumber(num);
};

/**
 * Format currency
 */
export const formatCurrency = (num, currency = 'USD') => {
  if (num === null || num === undefined) return 'N/A';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(num);
};

/**
 * Format percentage
 */
export const formatPercent = (num, decimals = 2) => {
  if (num === null || num === undefined) return 'N/A';
  return `${num >= 0 ? '+' : ''}${num.toFixed(decimals)}%`;
};

/**
 * Format a date string
 */
export const formatDate = (dateString, formatStr = 'MMM dd, yyyy') => {
  if (!dateString) return 'N/A';
  try {
    const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
    return format(date, formatStr);
  } catch {
    return dateString;
  }
};

/**
 * Format datetime
 */
export const formatDateTime = (dateString) => {
  return formatDate(dateString, 'MMM dd, yyyy HH:mm');
};

/**
 * Format relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
    return formatDistanceToNow(date, { addSuffix: true });
  } catch {
    return dateString;
  }
};

/**
 * Format change with sign
 */
export const formatChange = (change, isPercent = false) => {
  if (change === null || change === undefined) return '-';
  const formatted = isPercent ? `${Math.abs(change).toFixed(2)}%` : Math.abs(change).toFixed(2);
  return change >= 0 ? `+${formatted}` : `-${formatted}`;
};

/**
 * Get color based on value (positive/negative)
 */
export const getChangeColor = (value) => {
  if (value > 0) return '#2e7d32'; // green
  if (value < 0) return '#d32f2f'; // red
  return '#9e9e9e'; // grey
};

/**
 * Get sentiment label and color
 */
export const getSentimentInfo = (score) => {
  if (score >= 0.5) return { label: 'Very Bullish', color: 'success' };
  if (score >= 0.2) return { label: 'Bullish', color: 'success' };
  if (score >= -0.2) return { label: 'Neutral', color: 'default' };
  if (score >= -0.5) return { label: 'Bearish', color: 'error' };
  return { label: 'Very Bearish', color: 'error' };
};

/**
 * Get rating consensus info
 */
export const getRatingInfo = (consensus) => {
  const consensusLower = (consensus || '').toLowerCase();
  if (consensusLower.includes('strong buy')) return { color: 'success', label: 'Strong Buy' };
  if (consensusLower.includes('buy')) return { color: 'success', label: 'Buy' };
  if (consensusLower.includes('strong sell')) return { color: 'error', label: 'Strong Sell' };
  if (consensusLower.includes('sell')) return { color: 'error', label: 'Sell' };
  return { color: 'default', label: consensus || 'Hold' };
};

/**
 * Get trend icon name
 */
export const getTrend = (value) => {
  if (value > 0) return 'up';
  if (value < 0) return 'down';
  return 'flat';
};
