import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box, Grid, Card, CardContent, Typography, Button, CircularProgress
} from '@mui/material';
import { Refresh, Check, Close } from '@mui/icons-material';
import adminApi from '../../api/adminApi';
import LoadingSpinner from '../LoadingSpinner';
import ErrorMessage from '../ErrorMessage';

export default function ConfigStatus({ onNotify }) {
  const queryClient = useQueryClient();

  const { data: statusData, isLoading, error, refetch } = useQuery({
    queryKey: ['configStatus'],
    queryFn: () => adminApi.getConfigStatus().then(res => res.data)
  });

  const reloadMutation = useMutation({
    mutationFn: () => adminApi.reloadConfig(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configStatus'] });
      queryClient.invalidateQueries({ queryKey: ['tickers'] });
      queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
      onNotify('Configuration reloaded successfully', 'success');
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Failed to reload configuration';
      onNotify(message, 'error');
    }
  });

  const handleReload = () => {
    reloadMutation.mutate();
  };

  if (isLoading) return <LoadingSpinner message="Loading configuration status..." />;
  if (error) return <ErrorMessage message="Failed to load configuration status" onRetry={refetch} />;

  const status = statusData || {};
  const tickerStats = status.tickers || { active: 0, total: 0 };
  const apiKeyStats = status.api_keys || { active: 0, total: 0 };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Configuration Status</Typography>
        <Button
          variant="contained"
          startIcon={reloadMutation.isPending ? <CircularProgress size={20} color="inherit" /> : <Refresh />}
          onClick={handleReload}
          disabled={reloadMutation.isPending}
        >
          {reloadMutation.isPending ? 'Reloading...' : 'Reload Configuration'}
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Tickers
              </Typography>
              <Typography variant="h4">
                {tickerStats.active} / {tickerStats.total}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Active / Total
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                API Keys
              </Typography>
              <Typography variant="h4">
                {apiKeyStats.active} / {apiKeyStats.total}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Active / Total
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Last Reload
              </Typography>
              <Typography variant="h6">
                {status.last_reload 
                  ? new Date(status.last_reload).toLocaleString()
                  : 'Never'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {status.last_reload ? 'Last configuration reload' : 'Not reloaded yet'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {status.health_checks && (
          <>
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Health Checks</Typography>
            </Grid>
            {Object.entries(status.health_checks).map(([name, healthy]) => (
              <Grid item xs={12} sm={6} md={4} key={name}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={1}>
                      {healthy ? (
                        <Check color="success" />
                      ) : (
                        <Close color="error" />
                      )}
                      <Typography>{name}</Typography>
                    </Box>
                    <Typography variant="body2" color={healthy ? 'success.main' : 'error.main'}>
                      {healthy ? 'Healthy' : 'Unhealthy'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </>
        )}
      </Grid>
    </Box>
  );
}
