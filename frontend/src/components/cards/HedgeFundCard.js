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

  const getSentimentLabel = (sentiment) => {
    if (sentiment >= 0.6) return { label: 'Very Bullish', color: 'success' };
    if (sentiment >= 0.2) return { label: 'Bullish', color: 'success' };
    if (sentiment >= -0.2) return { label: 'Neutral', color: 'default' };
    if (sentiment >= -0.6) return { label: 'Bearish', color: 'error' };
    return { label: 'Very Bearish', color: 'error' };
  };

  const getTrendIcon = (trendAction) => {
    if (trendAction > 0) return <TrendingUp color="success" />;
    if (trendAction < 0) return <TrendingDown color="error" />;
    return <TrendingFlat color="action" />;
  };

  const getTrendLabel = (trendAction) => {
    if (trendAction > 0) return 'Increasing';
    if (trendAction < 0) return 'Decreasing';
    return 'Stable';
  };

  const sentiment = data.sentiment || 0;
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
            {getTrendIcon(data.trend_action)}
            <Typography variant="body2">
              Trend: {getTrendLabel(data.trend_action)}
            </Typography>
          </Box>
          {data.trend_value !== null && data.trend_value !== undefined && (
            <Typography variant="body2" color="textSecondary">
              Value: {data.trend_value}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
