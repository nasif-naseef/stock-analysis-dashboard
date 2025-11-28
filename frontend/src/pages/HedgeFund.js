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

/**
 * Get sentiment label from trend action value
 * trend_action: 1 = increasing, -1 = decreasing, 0 = neutral
 */
const getSentimentLabel = (trendAction, sentiment) => {
  if (trendAction > 0 || sentiment > 0) return { label: 'Accumulating', color: 'success', icon: <TrendingUp /> };
  if (trendAction < 0 || sentiment < 0) return { label: 'Distributing', color: 'error', icon: <TrendingDown /> };
  return { label: 'Neutral', color: 'default', icon: <TrendingFlat /> };
};

/**
 * Format sentiment score for display
 */
const formatSentiment = (value) => {
  if (value === null || value === undefined) return 'N/A';
  return value.toFixed(2);
};

export default function HedgeFund() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');

  const { data, isLoading, error, refetch } = useQuery(
    ['hedgeFund', selectedTicker],
    () => stockApi.getHedgeFund(selectedTicker),
    { enabled: !!selectedTicker }
  );

  const hedgeFundData = data?.data || {};
  
  // Extract notebook-style fields
  const sentiment = hedgeFundData.sentiment;
  const trendAction = hedgeFundData.trend_action;
  const trendValue = hedgeFundData.trend_value;
  
  const sentimentInfo = getSentimentLabel(trendAction, sentiment);

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
          {/* Summary Cards - Using notebook-style fields */}
          <Grid item xs={12} sm={6} md={4}>
            <DataCard 
              title="Sentiment Score" 
              value={formatSentiment(sentiment)}
              subtitle="Hedge fund sentiment indicator"
              color={sentiment > 0 ? '#2e7d32' : sentiment < 0 ? '#d32f2f' : 'inherit'}
              trend={sentiment > 0 ? 'up' : sentiment < 0 ? 'down' : 'flat'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <DataCard 
              title="Trend Action" 
              value={trendAction !== null && trendAction !== undefined ? trendAction : 'N/A'}
              subtitle={trendAction > 0 ? 'Increasing' : trendAction < 0 ? 'Decreasing' : 'Stable'}
              color={trendAction > 0 ? '#2e7d32' : trendAction < 0 ? '#d32f2f' : 'inherit'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <DataCard 
              title="Trend Value" 
              value={trendValue !== null && trendValue !== undefined ? trendValue : 'N/A'}
              subtitle="Net position change indicator"
            />
          </Grid>

          {/* Sentiment Indicator */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Hedge Fund Sentiment Analysis</Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Typography variant="body1">Overall Trend:</Typography>
                    <Chip 
                      icon={sentimentInfo.icon}
                      label={sentimentInfo.label}
                      color={sentimentInfo.color}
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Based on hedge fund sentiment and trend indicators
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">Sentiment Details</Typography>
                    <Box sx={{ mt: 1 }}>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2">Sentiment Score:</Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {formatSentiment(sentiment)}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2">Trend Action:</Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {trendAction !== null && trendAction !== undefined ? trendAction : 'N/A'}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2">Trend Value:</Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {trendValue !== null && trendValue !== undefined ? trendValue : 'N/A'}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
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
