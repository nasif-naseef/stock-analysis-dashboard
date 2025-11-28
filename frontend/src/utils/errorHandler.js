/**
 * Centralized Error Handler Utility
 * 
 * This module provides utilities for handling, formatting, and logging errors
 * across the application.
 */

/**
 * Error severity levels
 */
export const ErrorSeverity = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical',
};

/**
 * Error types for categorization
 */
export const ErrorType = {
  NETWORK: 'network',
  API: 'api',
  VALIDATION: 'validation',
  AUTH: 'auth',
  NOT_FOUND: 'not_found',
  SERVER: 'server',
  CLIENT: 'client',
  UNKNOWN: 'unknown',
};

/**
 * Format error message for user display
 * @param {Error|string|Object} error - The error to format
 * @returns {string} - User-friendly error message
 */
export const formatErrorMessage = (error) => {
  if (!error) return 'An unexpected error occurred';

  // Handle string errors
  if (typeof error === 'string') return error;

  // Handle Axios error responses
  if (error.response) {
    const status = error.response.status;
    const detail = error.response.data?.detail || error.response.data?.message;

    if (detail) return detail;

    switch (status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication required. Please log in.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 409:
        return 'This resource already exists.';
      case 422:
        return 'Invalid data provided. Please check your input.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Server error. Please try again later.';
      case 502:
        return 'Service temporarily unavailable. Please try again.';
      case 503:
        return 'Service is currently unavailable. Please try again later.';
      default:
        return `Request failed with status ${status}`;
    }
  }

  // Handle network errors
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return 'Request timed out. Please check your connection and try again.';
  }

  if (error.message?.includes('Network Error')) {
    return 'Unable to connect to the server. Please check your internet connection.';
  }

  // Handle standard Error objects
  if (error.message) return error.message;

  // Handle objects with error property
  if (error.error) return formatErrorMessage(error.error);

  return 'An unexpected error occurred';
};

/**
 * Determine error type from error object
 * @param {Error|Object} error - The error to classify
 * @returns {string} - Error type from ErrorType enum
 */
export const getErrorType = (error) => {
  if (!error) return ErrorType.UNKNOWN;

  // Check for network errors
  if (error.message?.includes('Network Error') || error.code === 'ERR_NETWORK') {
    return ErrorType.NETWORK;
  }

  // Check for timeout
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return ErrorType.NETWORK;
  }

  // Check HTTP status codes
  if (error.response) {
    const status = error.response.status;
    if (status === 401 || status === 403) return ErrorType.AUTH;
    if (status === 404) return ErrorType.NOT_FOUND;
    if (status === 400 || status === 422) return ErrorType.VALIDATION;
    if (status >= 500) return ErrorType.SERVER;
    return ErrorType.API;
  }

  return ErrorType.UNKNOWN;
};

/**
 * Determine error severity from error object
 * @param {Error|Object} error - The error to assess
 * @returns {string} - Severity level from ErrorSeverity enum
 */
export const getErrorSeverity = (error) => {
  if (!error) return ErrorSeverity.ERROR;

  const errorType = getErrorType(error);

  switch (errorType) {
    case ErrorType.NETWORK:
      return ErrorSeverity.WARNING;
    case ErrorType.VALIDATION:
      return ErrorSeverity.WARNING;
    case ErrorType.NOT_FOUND:
      return ErrorSeverity.WARNING;
    case ErrorType.AUTH:
      return ErrorSeverity.ERROR;
    case ErrorType.SERVER:
      return ErrorSeverity.CRITICAL;
    default:
      return ErrorSeverity.ERROR;
  }
};

/**
 * Check if error is retryable
 * @param {Error|Object} error - The error to check
 * @returns {boolean} - True if the error is retryable
 */
export const isRetryableError = (error) => {
  if (!error) return false;

  const errorType = getErrorType(error);

  // Network errors and server errors are typically retryable
  if (errorType === ErrorType.NETWORK || errorType === ErrorType.SERVER) {
    return true;
  }

  // Check specific status codes
  if (error.response) {
    const status = error.response.status;
    // 429 (Rate Limit), 503 (Service Unavailable), 502 (Bad Gateway) are retryable
    return [429, 502, 503, 504].includes(status);
  }

  return false;
};

/**
 * Log error to console with structured format
 * @param {Error|Object} error - The error to log
 * @param {string} context - Context where error occurred
 */
export const logError = (error, context = 'Unknown') => {
  const errorInfo = {
    timestamp: new Date().toISOString(),
    context,
    type: getErrorType(error),
    severity: getErrorSeverity(error),
    message: formatErrorMessage(error),
    originalError: error,
  };

  // In development, log full error details
  if (process.env.NODE_ENV === 'development') {
    console.error('[Error]', errorInfo);
  } else {
    // In production, log minimal info
    console.error(`[${errorInfo.severity.toUpperCase()}] ${errorInfo.context}: ${errorInfo.message}`);
  }

  return errorInfo;
};

/**
 * Create a standardized error response object
 * @param {Error|Object} error - The error to process
 * @param {string} context - Context where error occurred
 * @returns {Object} - Standardized error object
 */
export const createErrorResponse = (error, context = '') => {
  return {
    message: formatErrorMessage(error),
    type: getErrorType(error),
    severity: getErrorSeverity(error),
    retryable: isRetryableError(error),
    context,
    timestamp: new Date().toISOString(),
  };
};

/**
 * Handle API error with logging and formatting
 * @param {Error|Object} error - The error to handle
 * @param {string} context - Context where error occurred
 * @param {Function} onError - Optional callback for error handling
 * @returns {Object} - Error response object
 */
export const handleApiError = (error, context = 'API Call', onError = null) => {
  const errorResponse = createErrorResponse(error, context);
  logError(error, context);

  if (onError && typeof onError === 'function') {
    onError(errorResponse);
  }

  return errorResponse;
};

/**
 * Get user action suggestion based on error type
 * @param {string} errorType - Type of error from ErrorType enum
 * @returns {string} - Suggested action for user
 */
export const getErrorSuggestion = (errorType) => {
  switch (errorType) {
    case ErrorType.NETWORK:
      return 'Please check your internet connection and try again.';
    case ErrorType.AUTH:
      return 'Please log in to continue.';
    case ErrorType.NOT_FOUND:
      return 'The requested data may have been removed or is not available.';
    case ErrorType.VALIDATION:
      return 'Please review your input and try again.';
    case ErrorType.SERVER:
      return 'Our servers are experiencing issues. Please try again in a few minutes.';
    default:
      return 'Please try again or contact support if the problem persists.';
  }
};

export default {
  ErrorSeverity,
  ErrorType,
  formatErrorMessage,
  getErrorType,
  getErrorSeverity,
  isRetryableError,
  logError,
  createErrorResponse,
  handleApiError,
  getErrorSuggestion,
};
