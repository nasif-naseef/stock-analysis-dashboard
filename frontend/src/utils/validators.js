/**
 * Input Validation Utilities
 * 
 * This module provides validation functions for user inputs across the application.
 */

/**
 * Validate ticker symbol format
 * Valid tickers are 1-10 uppercase alphanumeric characters
 * @param {string} ticker - The ticker symbol to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidTicker = (ticker) => {
  if (!ticker || typeof ticker !== 'string') return false;
  const pattern = /^[A-Z0-9]{1,10}$/;
  return pattern.test(ticker.toUpperCase().trim());
};

/**
 * Normalize ticker to uppercase and trim whitespace
 * @param {string} ticker - The ticker symbol to normalize
 * @returns {string} - Normalized ticker
 */
export const normalizeTicker = (ticker) => {
  if (!ticker || typeof ticker !== 'string') return '';
  return ticker.trim().toUpperCase();
};

/**
 * Valid period options for time range selection
 */
export const VALID_PERIODS = ['1h', '2h', '4h', '6h', '12h', '1d', '1w', '1m'];

/**
 * Validate time range format
 * Valid formats: 1h, 2h, 4h, 6h, 12h, 1d, 1w, 1m (no leading zeros)
 * @param {string} range - The time range to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidTimeRange = (range) => {
  if (!range || typeof range !== 'string') return false;
  const pattern = /^[1-9][0-9]*[hdwm]$/i;
  return pattern.test(range.trim());
};

/**
 * Validate period format for comparison
 * @param {string} period - The period string (e.g., "1h", "4h", "1d", "1w")
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidPeriod = (period) => {
  if (!period || typeof period !== 'string') return false;
  // Use regex validation and also accept pre-defined valid periods
  const normalizedPeriod = period.toLowerCase().trim();
  return VALID_PERIODS.includes(normalizedPeriod) || isValidTimeRange(period);
};

/**
 * Validate numeric value is within range
 * @param {number} value - The value to validate
 * @param {number} min - Minimum allowed value
 * @param {number} max - Maximum allowed value
 * @returns {boolean} - True if within range, false otherwise
 */
export const isInRange = (value, min, max) => {
  if (value === null || value === undefined || isNaN(value)) return false;
  return value >= min && value <= max;
};

/**
 * Validate score is within 0-100 range
 * @param {number} score - The score to validate
 * @returns {boolean} - True if valid score, false otherwise
 */
export const isValidScore = (score) => {
  return isInRange(score, 0, 100);
};

/**
 * Validate percentage is within -100 to 100 range
 * @param {number} percentage - The percentage to validate
 * @returns {boolean} - True if valid percentage, false otherwise
 */
export const isValidPercentage = (percentage) => {
  return isInRange(percentage, -100, 100);
};

/**
 * Validate sentiment score is within -1 to 1 range
 * @param {number} score - The sentiment score to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidSentimentScore = (score) => {
  return isInRange(score, -1, 1);
};

/**
 * Validate RSI value (0-100 range)
 * @param {number} rsi - The RSI value to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidRSI = (rsi) => {
  return isInRange(rsi, 0, 100);
};

/**
 * Validate array has minimum number of items
 * @param {Array} arr - The array to validate
 * @param {number} minLength - Minimum required length
 * @returns {boolean} - True if valid, false otherwise
 */
export const hasMinItems = (arr, minLength) => {
  if (!Array.isArray(arr)) return false;
  return arr.length >= minLength;
};

/**
 * Validate object has required properties
 * @param {Object} obj - The object to validate
 * @param {Array<string>} requiredProps - List of required property names
 * @returns {boolean} - True if all required properties exist and are not null/undefined
 */
export const hasRequiredProperties = (obj, requiredProps) => {
  if (!obj || typeof obj !== 'object') return false;
  return requiredProps.every(prop => obj[prop] !== null && obj[prop] !== undefined);
};

/**
 * Validate email format
 * @param {string} email - The email to validate
 * @returns {boolean} - True if valid email format, false otherwise
 */
export const isValidEmail = (email) => {
  if (!email || typeof email !== 'string') return false;
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email.trim());
};

/**
 * Validate API key format (alphanumeric with dashes/underscores)
 * @param {string} apiKey - The API key to validate
 * @returns {boolean} - True if valid format, false otherwise
 */
export const isValidApiKey = (apiKey) => {
  if (!apiKey || typeof apiKey !== 'string') return false;
  const pattern = /^[A-Za-z0-9_-]+$/;
  return apiKey.trim().length >= 8 && pattern.test(apiKey.trim());
};

/**
 * Validate service name format (alphanumeric with underscores)
 * @param {string} serviceName - The service name to validate
 * @returns {boolean} - True if valid format, false otherwise
 */
export const isValidServiceName = (serviceName) => {
  if (!serviceName || typeof serviceName !== 'string') return false;
  const pattern = /^[A-Za-z0-9_\s]+$/;
  return pattern.test(serviceName.trim());
};

/**
 * Validate data exists and has content
 * @param {*} data - The data to validate
 * @returns {boolean} - True if data exists and is not empty
 */
export const hasData = (data) => {
  if (data === null || data === undefined) return false;
  if (Array.isArray(data)) return data.length > 0;
  if (typeof data === 'object') return Object.keys(data).length > 0;
  if (typeof data === 'string') return data.trim().length > 0;
  return true;
};

/**
 * Safe number parsing with fallback
 * @param {*} value - Value to parse
 * @param {number} fallback - Fallback value if parsing fails
 * @returns {number} - Parsed number or fallback
 */
export const safeParseNumber = (value, fallback = 0) => {
  if (value === null || value === undefined) return fallback;
  const parsed = Number(value);
  return isNaN(parsed) ? fallback : parsed;
};

/**
 * Clamp a value within a range
 * @param {number} value - The value to clamp
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {number} - Clamped value
 */
export const clamp = (value, min, max) => {
  const numValue = safeParseNumber(value, min);
  return Math.max(min, Math.min(max, numValue));
};

/**
 * Validate chart data has required structure
 * @param {Object} data - Chart data to validate
 * @returns {boolean} - True if valid chart data
 */
export const isValidChartData = (data) => {
  if (!data || typeof data !== 'object') return false;
  // Basic validation - data should have at least one numeric property
  return Object.values(data).some(value => typeof value === 'number' && !isNaN(value));
};
