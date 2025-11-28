import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import PropTypes from 'prop-types';

/**
 * Size configurations for the loading spinner
 */
const SIZES = {
  small: 24,
  medium: 40,
  large: 60,
};

/**
 * Loading spinner component with size variants and optional loading text
 * 
 * @param {Object} props - Component props
 * @param {string} props.message - Loading message to display
 * @param {number|string} props.size - Spinner size (small, medium, large, or numeric value)
 * @param {string} props.color - Spinner color (primary, secondary, inherit)
 * @param {boolean} props.fullScreen - Whether to display full screen
 * @param {boolean} props.overlay - Whether to display as overlay
 */
export default function LoadingSpinner({ 
  message = 'Loading...', 
  size = 'medium',
  color = 'primary',
  fullScreen = false,
  overlay = false,
}) {
  // Determine spinner size
  const spinnerSize = typeof size === 'number' ? size : (SIZES[size] || SIZES.medium);
  
  // Determine text variant based on size
  const textVariant = spinnerSize <= 24 ? 'caption' : spinnerSize >= 60 ? 'h6' : 'body2';
  
  const containerStyles = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spinnerSize <= 24 ? 1 : 2,
    minHeight: fullScreen ? '100vh' : spinnerSize <= 24 ? '80px' : '200px',
    ...(overlay && {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(255, 255, 255, 0.8)',
      zIndex: 1000,
    }),
    ...(fullScreen && {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      zIndex: 9999,
    }),
  };

  return (
    <Box sx={containerStyles}>
      <CircularProgress 
        size={spinnerSize} 
        color={color}
        aria-label="Loading content"
      />
      {message && (
        <Typography 
          color="textSecondary" 
          variant={textVariant}
          role="status"
          aria-live="polite"
        >
          {message}
        </Typography>
      )}
    </Box>
  );
}

LoadingSpinner.propTypes = {
  message: PropTypes.string,
  size: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.oneOf(['small', 'medium', 'large']),
  ]),
  color: PropTypes.oneOf(['primary', 'secondary', 'inherit']),
  fullScreen: PropTypes.bool,
  overlay: PropTypes.bool,
};
