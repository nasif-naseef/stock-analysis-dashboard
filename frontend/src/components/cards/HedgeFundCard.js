import React from 'react';
import {
  Card, CardContent, Typography, Box, Chip
} from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

/**
 * HedgeFundCard - Display hedge fund confidence and trend data
 * 
 * @param {Object} data - Hedge fund data
 * @param {string} data.ticker - Stock ticker symbol
 * @param {number} data.sentiment - Sentiment score
 * @param {number} data.trend_action - Trend action indicator
 * @param {number} data.trend_value - Trend value
 */
export default function HedgeFundCard({ data }) {
  if (!data || data.error) {
    return (
      <Card>
        <CardContent>
          <Typography color="textSecondary">
            {data?.error || 'No hedge fund data available'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Extract with fallback to raw_data
  let sentiment = data.sentiment;
  let trendAction = data.trend_action;
  let trendValue = data.trend_value;
  
  // Fallback: Extract from raw_data.hedgeFundData if direct fields are null
  if ((sentiment === null || sentiment === undefined) && data.raw_data) {
    const rawHedgeFund = data.raw_data.hedgeFundData || {};
    sentiment = sentiment ?? rawHedgeFund.sentiment;
    trendAction = trendAction ?? rawHedgeFund.trendAction;
    trendValue = trendValue ?? rawHedgeFund.trendValue;
  }

  const getSentimentLabel = (sentiment) => {
    if (sentiment === null || sentiment === undefined) return { label: 'Unknown', color: 'default' };
    if (sentiment >= 0.6) return { label: 'Very Bullish', color: 'success' };
    if (sentiment >= 0.2) return { label: 'Bullish', color: 'success' };
    if (sentiment >= -0.2) return { label: 'Neutral', color: 'default' };
    if (sentiment >= -0.6) return { label: 'Bearish', color: 'error' };
    return { label: 'Very Bearish', color: 'error' };
  };

  const getTrendIcon = (trendAction) => {
    // Map trendAction values: 1=Increase, 2=New, 3=Decrease, 4=Sold Out, 5=No Change
    if (trendAction === 1 || trendAction === 2) return <TrendingUp color="success" />;
    if (trendAction === 3 || trendAction === 4) return <TrendingDown color="error" />;
    return <TrendingFlat color="action" />;
  };

  const getTrendLabel = (trendAction) => {
    const labels = {
      1: 'Increasing',
      2: 'New Positions',
      3: 'Decreasing',
      4: 'Sold Out',
      5: 'No Change'
    };
    return labels[trendAction] || 'Stable';
  };

  sentiment = sentiment ?? 0;
  const sentimentInfo = getSentimentLabel(sentiment);

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            Hedge Fund Confidence
          </Typography>
          <Chip 
            label={sentimentInfo.label} 
            color={sentimentInfo.color}
            size="small"
          />
        </Box>

        <Typography variant="body2" color="textSecondary" gutterBottom>
          {data.ticker}
        </Typography>

        {/* Sentiment Score */}
        <Box my={3}>
          <Typography variant="subtitle2" color="textSecondary" gutterBottom>
            Sentiment Score
          </Typography>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="h4" component="span">
              {(sentiment * 100).toFixed(1)}%
            </Typography>
            <Box 
              sx={{ 
                flex: 1, 
                height: 8, 
                bgcolor: 'grey.200', 
                borderRadius: 1,
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              <Box 
                sx={{ 
                  position: 'absolute',
                  left: '50%',
                  width: `${Math.abs(sentiment * 50)}%`,
                  height: '100%',
                  bgcolor: sentiment >= 0 ? 'success.main' : 'error.main',
                  transform: sentiment >= 0 ? 'none' : 'translateX(-100%)'
                }} 
              />
            </Box>
          </Box>
        </Box>

        {/* Trend */}
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box display="flex" alignItems="center" gap={1}>
            {getTrendIcon(trendAction)}
            <Typography variant="body2">
              Trend: {getTrendLabel(trendAction)}
            </Typography>
          </Box>
          {trendValue !== null && trendValue !== undefined && (
            <Typography variant="body2" color="textSecondary">
              Value: {trendValue.toLocaleString('en-US')}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
