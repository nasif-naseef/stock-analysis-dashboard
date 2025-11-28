import React from 'react';
import { Alert, AlertTitle, Button, Box, Typography, Collapse } from '@mui/material';
import { Refresh as RefreshIcon, ExpandMore, ExpandLess } from '@mui/icons-material';
import PropTypes from 'prop-types';

/**
 * Error message component with retry button and severity levels
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Error title
 * @param {string} props.message - Error message to display
 * @param {Function} props.onRetry - Callback for retry action
 * @param {string} props.severity - Alert severity (error, warning, info, success)
 * @param {boolean} props.showDetails - Whether to show expanded error details
 * @param {string} props.details - Additional error details (expandable)
 * @param {boolean} props.dismissible - Whether the error can be dismissed
 * @param {Function} props.onDismiss - Callback for dismiss action
 * @param {string} props.suggestion - Suggestion for resolving the error
 */
export default function ErrorMessage({ 
  title, 
  message = 'Something went wrong',
  onRetry,
  severity = 'error',
  showDetails = false,
  details = '',
  dismissible = false,
  onDismiss,
  suggestion = '',
}) {
  const [expanded, setExpanded] = React.useState(false);
  const [visible, setVisible] = React.useState(true);

  // Default titles based on severity
  const defaultTitles = {
    error: 'Error',
    warning: 'Warning',
    info: 'Information',
    success: 'Success',
  };

  const displayTitle = title || defaultTitles[severity] || 'Error';

  const handleDismiss = () => {
    setVisible(false);
    if (onDismiss) {
      onDismiss();
    }
  };

  if (!visible) {
    return null;
  }

  return (
    <Box sx={{ my: 2 }}>
      <Alert 
        severity={severity}
        onClose={dismissible ? handleDismiss : undefined}
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {details && (
              <Button
                color="inherit"
                size="small"
                onClick={() => setExpanded(!expanded)}
                endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
                aria-expanded={expanded}
                aria-label={expanded ? 'Hide details' : 'Show details'}
              >
                Details
              </Button>
            )}
            {onRetry && (
              <Button 
                color="inherit" 
                size="small" 
                onClick={onRetry}
                startIcon={<RefreshIcon />}
                aria-label="Retry action"
              >
                Retry
              </Button>
            )}
          </Box>
        }
        role="alert"
        aria-live="assertive"
      >
        <AlertTitle>{displayTitle}</AlertTitle>
        <Typography variant="body2">{message}</Typography>
        
        {suggestion && (
          <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
            {suggestion}
          </Typography>
        )}

        {details && (
          <Collapse in={expanded}>
            <Box sx={{ mt: 2, p: 1, bgcolor: 'rgba(0,0,0,0.05)', borderRadius: 1 }}>
              <Typography 
                variant="caption" 
                component="pre" 
                sx={{ 
                  whiteSpace: 'pre-wrap', 
                  wordBreak: 'break-word',
                  fontFamily: 'monospace',
                  margin: 0,
                }}
              >
                {details}
              </Typography>
            </Box>
          </Collapse>
        )}
      </Alert>
    </Box>
  );
}

ErrorMessage.propTypes = {
  title: PropTypes.string,
  message: PropTypes.string,
  onRetry: PropTypes.func,
  severity: PropTypes.oneOf(['error', 'warning', 'info', 'success']),
  showDetails: PropTypes.bool,
  details: PropTypes.string,
  dismissible: PropTypes.bool,
  onDismiss: PropTypes.func,
  suggestion: PropTypes.string,
};

/**
 * Empty state component for when no data is available
 * 
 * @param {Object} props - Component props
 * @param {string} props.message - Message to display
 * @param {Function} props.onAction - Optional action callback
 * @param {string} props.actionLabel - Label for action button
 */
export function EmptyState({ 
  message = 'No data available', 
  onAction,
  actionLabel = 'Refresh',
}) {
  return (
    <Box 
      sx={{ 
        textAlign: 'center', 
        py: 4, 
        px: 2,
        color: 'text.secondary',
      }}
      role="status"
    >
      <Typography variant="body1" gutterBottom>
        {message}
      </Typography>
      {onAction && (
        <Button 
          variant="outlined" 
          size="small" 
          onClick={onAction}
          sx={{ mt: 2 }}
        >
          {actionLabel}
        </Button>
      )}
    </Box>
  );
}

EmptyState.propTypes = {
  message: PropTypes.string,
  onAction: PropTypes.func,
  actionLabel: PropTypes.string,
};
