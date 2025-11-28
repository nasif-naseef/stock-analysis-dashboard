import React from 'react';
import {
  Paper, Typography, Box, Button, Grid, Chip, CircularProgress
} from '@mui/material';
import { Refresh as RefreshIcon, Check as CheckIcon } from '@mui/icons-material';

export default function ConfigStatus({ 
  status, 
  isLoading, 
  onReload, 
  isReloading 
}) {
  if (isLoading) {
    return (
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={100}>
          <CircularProgress size={30} />
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Configuration Status</Typography>
        <Button
          variant="outlined"
          startIcon={isReloading ? <CircularProgress size={20} /> : <RefreshIcon />}
          onClick={onReload}
          disabled={isReloading}
        >
          {isReloading ? 'Reloading...' : 'Reload Configuration'}
        </Button>
      </Box>
      
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <Box>
            <Typography variant="body2" color="textSecondary">Active Tickers</Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="h5">{status?.active_tickers || 0}</Typography>
              <Chip 
                label={`/ ${status?.total_tickers || 0} total`} 
                size="small" 
                variant="outlined"
              />
            </Box>
          </Box>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Box>
            <Typography variant="body2" color="textSecondary">Active API Keys</Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="h5">{status?.active_api_keys || 0}</Typography>
              <Chip 
                label={`/ ${status?.total_api_keys || 0} total`} 
                size="small" 
                variant="outlined"
              />
            </Box>
          </Box>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Box>
            <Typography variant="body2" color="textSecondary">Status</Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <CheckIcon color="success" fontSize="small" />
              <Typography variant="body1" color="success.main">Active</Typography>
            </Box>
          </Box>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Box>
            <Typography variant="body2" color="textSecondary">Last Reload</Typography>
            <Typography variant="body1">
              {status?.last_reload 
                ? new Date(status.last_reload).toLocaleString() 
                : 'Never'}
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
}
