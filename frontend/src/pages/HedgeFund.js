import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Grid, Typography, Box, Paper, Divider, Chip } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';
import stockApi from '../api/stockApi';
import TickerSelector from '../components/TickerSelector';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const DataCard = ({ title, value, subtitle, color, trend }) => (
  <Paper sx={{ p: 2, height: '100%' }}>
    <Typography variant="body2" color="textSecondary">{title}</Typography>
    <Box display="flex" alignItems="center" gap={1}>
      <Typography variant="h4" sx={{ color: color || 'inherit' }}>{value}</Typography>
      {trend === 'up' && <TrendingUp color="success" />}
      {trend === 'down' && <TrendingDown color="error" />}
      {trend === 'flat' && <TrendingFlat />}
    </Box>
    {subtitle && <Typography variant="body2" color="textSecondary">{subtitle}</Typography>}
  </Paper>
);

const formatLargeNumber = (num) => {
  if (!num) return 'N/A';
  if (num >= 1000000000) return `${(num / 1000000000).toFixed(2)}B`;
  if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(2)}K`;
  return num.toFixed(2);
};

export default function HedgeFund() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');

  const { data, isLoading, error, refetch } = useQuery(
    ['hedgeFund', selectedTicker],
    () => stockApi.getHedgeFund(selectedTicker),
    { enabled: !!selectedTicker }
  );

  const hedgeFundData = data?.data || {};

  const getTrendFromChange = (change) => {
    if (change > 0) return 'up';
    if (change < 0) return 'down';
    return 'flat';
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Typography variant="h4">Hedge Fund Activity</Typography>
        <Box width={200}>
          <TickerSelector
            value={selectedTicker}
            onChange={setSelectedTicker}
            size="small"
          />
        </Box>
      </Box>

      {isLoading ? (
        <LoadingSpinner message={`Loading hedge fund data for ${selectedTicker}...`} />
      ) : error ? (
        <ErrorMessage message="Failed to load hedge fund data" onRetry={refetch} />
      ) : (
        <Grid container spacing={3}>
          {/* Summary Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Hedge Fund Holders" 
              value={hedgeFundData.hedge_fund_count || 0}
              subtitle="Total funds holding"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Net Change" 
              value={hedgeFundData.net_shares_change ? formatLargeNumber(hedgeFundData.net_shares_change) : 'N/A'}
              trend={getTrendFromChange(hedgeFundData.net_shares_change)}
              color={hedgeFundData.net_shares_change > 0 ? '#2e7d32' : hedgeFundData.net_shares_change < 0 ? '#d32f2f' : 'inherit'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="New Positions" 
              value={hedgeFundData.new_positions || 0}
              color="#2e7d32"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Closed Positions" 
              value={hedgeFundData.closed_positions || 0}
              color="#d32f2f"
            />
          </Grid>

          {/* Position Changes */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Position Changes</Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Increased Positions</Typography>
                  <Typography variant="h5" color="success.main">
                    {hedgeFundData.increased_positions || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Decreased Positions</Typography>
                  <Typography variant="h5" color="error.main">
                    {hedgeFundData.decreased_positions || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">No Change</Typography>
                  <Typography variant="h5">
                    {hedgeFundData.no_change_positions || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Activity Ratio</Typography>
                  <Typography variant="h5">
                    {hedgeFundData.activity_ratio ? `${(hedgeFundData.activity_ratio * 100).toFixed(1)}%` : 'N/A'}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Holdings Summary */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Holdings Summary</Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Total Shares Held</Typography>
                  <Typography variant="h5">
                    {formatLargeNumber(hedgeFundData.total_shares_held)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Total Value</Typography>
                  <Typography variant="h5">
                    ${formatLargeNumber(hedgeFundData.total_value)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Avg Position Size</Typography>
                  <Typography variant="h5">
                    ${formatLargeNumber(hedgeFundData.avg_position_size)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">% Ownership</Typography>
                  <Typography variant="h5">
                    {hedgeFundData.ownership_percent ? `${hedgeFundData.ownership_percent.toFixed(2)}%` : 'N/A'}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Sentiment Indicator */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Hedge Fund Sentiment</Typography>
              <Divider sx={{ mb: 2 }} />
              <Box display="flex" alignItems="center" gap={2}>
                <Typography variant="body1">Overall Trend:</Typography>
                <Chip 
                  icon={hedgeFundData.net_shares_change > 0 ? <TrendingUp /> : 
                        hedgeFundData.net_shares_change < 0 ? <TrendingDown /> : <TrendingFlat />}
                  label={hedgeFundData.net_shares_change > 0 ? 'Accumulating' : 
                         hedgeFundData.net_shares_change < 0 ? 'Distributing' : 'Neutral'}
                  color={hedgeFundData.net_shares_change > 0 ? 'success' : 
                         hedgeFundData.net_shares_change < 0 ? 'error' : 'default'}
                />
                <Typography variant="body2" color="textSecondary" sx={{ ml: 'auto' }}>
                  Based on net position changes
                </Typography>
              </Box>
              {hedgeFundData.timestamp && (
                <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
                  Last updated: {new Date(hedgeFundData.timestamp).toLocaleString()}
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
