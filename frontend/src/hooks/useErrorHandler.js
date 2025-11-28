/**
 * useErrorHandler Hook
 * 
 * Custom React hook for handling errors with state management,
 * automatic retry logic, and user-friendly error display.
 */
import { useState, useCallback, useRef } from 'react';
import {
  formatErrorMessage,
  getErrorType,
  getErrorSeverity,
  isRetryableError,
  logError,
  ErrorSeverity,
  ErrorType,
} from '../utils/errorHandler';

/**
 * Default configuration for the error handler hook
 */
const DEFAULT_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000,
  exponentialBackoff: true,
  autoReset: true,
  autoResetDelay: 5000,
};

/**
 * Custom hook for error handling
 * 
 * @param {Object} config - Configuration options
 * @param {number} config.maxRetries - Maximum number of retry attempts
 * @param {number} config.retryDelay - Base delay between retries in ms
 * @param {boolean} config.exponentialBackoff - Use exponential backoff for retries
 * @param {boolean} config.autoReset - Automatically reset error after delay
 * @param {number} config.autoResetDelay - Delay before auto-reset in ms
 * @returns {Object} - Error handler state and methods
 */
export function useErrorHandler(config = {}) {
  const options = { ...DEFAULT_CONFIG, ...config };
  
  const [error, setError] = useState(null);
  const [isRetrying, setIsRetrying] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const autoResetTimer = useRef(null);
  const retryTimer = useRef(null);

  /**
   * Clear any pending timers
   */
  const clearTimers = useCallback(() => {
    if (autoResetTimer.current) {
      clearTimeout(autoResetTimer.current);
      autoResetTimer.current = null;
    }
    if (retryTimer.current) {
      clearTimeout(retryTimer.current);
      retryTimer.current = null;
    }
  }, []);

  /**
   * Reset error state
   */
  const resetError = useCallback(() => {
    clearTimers();
    setError(null);
    setIsRetrying(false);
    setRetryCount(0);
  }, [clearTimers]);

  /**
   * Set error with full error info
   * @param {Error|Object|string} err - The error to set
   * @param {string} context - Context where error occurred
   */
  const setErrorState = useCallback((err, context = '') => {
    clearTimers();
    
    const errorInfo = {
      message: formatErrorMessage(err),
      type: getErrorType(err),
      severity: getErrorSeverity(err),
      retryable: isRetryableError(err),
      context,
      originalError: err,
      timestamp: new Date().toISOString(),
    };

    logError(err, context);
    setError(errorInfo);
    setIsRetrying(false);

    // Auto-reset if configured
    if (options.autoReset) {
      autoResetTimer.current = setTimeout(() => {
        resetError();
      }, options.autoResetDelay);
    }
  }, [clearTimers, options.autoReset, options.autoResetDelay, resetError]);

  /**
   * Handle an error from an async operation
   * @param {Error|Object} err - The error to handle
   * @param {string} context - Context where error occurred
   */
  const handleError = useCallback((err, context = 'Operation') => {
    setErrorState(err, context);
  }, [setErrorState]);

  /**
   * Execute a function with automatic error handling and retry logic
   * @param {Function} fn - The async function to execute
   * @param {string} context - Context for error logging
   * @returns {Promise<*>} - Result of the function or null on error
   */
  const executeWithRetry = useCallback(async (fn, context = 'Operation') => {
    resetError();
    let lastError = null;
    let attempts = 0;

    while (attempts <= options.maxRetries) {
      try {
        setIsRetrying(attempts > 0);
        setRetryCount(attempts);
        
        const result = await fn();
        
        // Success - reset error state
        resetError();
        return result;
      } catch (err) {
        lastError = err;
        attempts++;

        // Check if error is retryable and we have retries left
        if (isRetryableError(err) && attempts <= options.maxRetries) {
          const delay = options.exponentialBackoff
            ? options.retryDelay * Math.pow(2, attempts - 1)
            : options.retryDelay;

          await new Promise(resolve => {
            retryTimer.current = setTimeout(resolve, delay);
          });
        } else {
          break;
        }
      }
    }

    // All retries exhausted or error not retryable
    setErrorState(lastError, context);
    return null;
  }, [options.maxRetries, options.retryDelay, options.exponentialBackoff, resetError, setErrorState]);

  /**
   * Wrapper for executing async operations with error handling
   * @param {Function} fn - The async function to execute
   * @param {Object} options - Execution options
   * @returns {Promise<*>} - Result of the function
   */
  const execute = useCallback(async (fn, { context = 'Operation', retry = false } = {}) => {
    if (retry) {
      return executeWithRetry(fn, context);
    }

    try {
      const result = await fn();
      return result;
    } catch (err) {
      handleError(err, context);
      return null;
    }
  }, [executeWithRetry, handleError]);

  /**
   * Manually trigger a retry of the last failed operation
   * @param {Function} fn - The function to retry
   * @param {string} context - Context for error logging
   */
  const retry = useCallback(async (fn, context = 'Retry') => {
    if (!error?.retryable) {
      console.warn('Error is not retryable');
      return null;
    }

    setRetryCount(prev => prev + 1);
    setIsRetrying(true);

    try {
      const result = await fn();
      resetError();
      return result;
    } catch (err) {
      setErrorState(err, context);
      return null;
    }
  }, [error, resetError, setErrorState]);

  return {
    // State
    error,
    hasError: !!error,
    isRetrying,
    retryCount,
    
    // Derived state
    errorMessage: error?.message || null,
    errorType: error?.type || null,
    errorSeverity: error?.severity || null,
    isRetryable: error?.retryable || false,
    
    // Methods
    handleError,
    resetError,
    execute,
    executeWithRetry,
    retry,
    
    // Utilities
    clearTimers,
  };
}

/**
 * Hook for query error handling (React Query compatible)
 * @param {Object} options - Configuration options
 * @returns {Object} - Error handler for queries
 */
export function useQueryErrorHandler(options = {}) {
  const { handleError, error, resetError } = useErrorHandler(options);

  /**
   * onError callback for React Query
   */
  const onError = useCallback((err) => {
    handleError(err, 'Query Error');
  }, [handleError]);

  /**
   * onSettled callback to reset error on success
   */
  const onSettled = useCallback((data, err) => {
    if (!err && error) {
      resetError();
    }
  }, [error, resetError]);

  return {
    error,
    onError,
    onSettled,
    resetError,
  };
}

/**
 * Hook for mutation error handling (React Query compatible)
 * @param {Object} options - Configuration options
 * @returns {Object} - Error handler for mutations
 */
export function useMutationErrorHandler(options = {}) {
  const { handleError, error, resetError, isRetrying, retry } = useErrorHandler(options);

  /**
   * onError callback for React Query mutations
   */
  const onError = useCallback((err, variables, context) => {
    handleError(err, `Mutation Error: ${context?.operationName || 'Unknown'}`);
  }, [handleError]);

  /**
   * onSuccess callback to reset error
   */
  const onSuccess = useCallback(() => {
    if (error) {
      resetError();
    }
  }, [error, resetError]);

  return {
    error,
    onError,
    onSuccess,
    resetError,
    isRetrying,
    retry,
  };
}

// Re-export error utilities for convenience
export { ErrorSeverity, ErrorType } from '../utils/errorHandler';

export default useErrorHandler;
