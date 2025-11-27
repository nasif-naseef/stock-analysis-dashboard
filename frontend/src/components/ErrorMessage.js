import React from 'react';
import { Alert, AlertTitle, Button, Box } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';

export default function ErrorMessage({ 
  title = 'Error', 
  message = 'Something went wrong',
  onRetry,
  severity = 'error'
}) {
  return (
    <Box sx={{ my: 2 }}>
      <Alert 
        severity={severity}
        action={onRetry && (
          <Button 
            color="inherit" 
            size="small" 
            onClick={onRetry}
            startIcon={<RefreshIcon />}
          >
            Retry
          </Button>
        )}
      >
        <AlertTitle>{title}</AlertTitle>
        {message}
      </Alert>
    </Box>
  );
}
