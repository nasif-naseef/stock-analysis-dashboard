import React from 'react';
import {
  Card, CardContent, Typography, Box, Chip, Alert
} from '@mui/material';
import { Warning, TrendingDown, TrendingUp } from '@mui/icons-material';

/**
 * StopLossCard - Display stop loss recommendations
 * 
 * @param {Object} data - Stop loss data
 * @param {string} data.ticker - Stock ticker symbol
 * @param {number} data.recommended_stop_price - Recommended stop price
 * @param {string} data.calculation_timestamp - When calculated
 * @param {string} data.stop_type - Type of stop loss
 * @param {string} data.direction - Direction (long/short)
 * @param {string} data.tightness - Tightness level
 */
export default function StopLossCard({ data, currentPrice }) {
  if (!data || data.error) {
    return (
      <Card>
        <CardContent>
          <Typography color="textSecondary">
            {data?.error || 'No stop loss data available'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const formatPrice = (price) => {
    if (price === null || price === undefined) return 'N/A';
    return `$${Number(price).toFixed(2)}`;
  };

  const getStopDistance = () => {
    if (!currentPrice || !data.recommended_stop_price) return null;
    const distance = ((currentPrice - data.recommended_stop_price) / currentPrice) * 100;
    return distance.toFixed(1);
  };

  const isLongPosition = (data.direction || '').toLowerCase().includes('long') || 
                         (data.direction || '').toLowerCase().includes('below');

  const stopDistance = getStopDistance();

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            Stop Loss
          </Typography>
          <Chip 
            icon={<Warning />}
            label={data.tightness || 'Medium'} 
            color="warning"
            size="small"
          />
        </Box>

        <Typography variant="body2" color="textSecondary" gutterBottom>
          {data.ticker}
        </Typography>

        {/* Recommended Stop Price */}
        <Box 
          textAlign="center" 
          my={3} 
          p={2} 
          bgcolor="warning.light" 
          borderRadius={2}
          sx={{ bgcolor: 'rgba(255, 152, 0, 0.1)' }}
        >
          <Typography variant="caption" color="textSecondary">
            Recommended Stop Price
          </Typography>
          <Typography 
            variant="h3" 
            component="div"
            color="warning.dark"
            fontWeight="bold"
          >
            {formatPrice(data.recommended_stop_price)}
          </Typography>
          {stopDistance && (
            <Typography variant="body2" color="textSecondary">
              {stopDistance}% from current price
            </Typography>
          )}
        </Box>

        {/* Stop Details */}
        <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
          <Chip 
            size="small" 
            label={data.stop_type || 'Volatility-Based'}
            variant="outlined"
          />
          <Chip 
            size="small" 
            icon={isLongPosition ? <TrendingUp /> : <TrendingDown />}
            label={isLongPosition ? 'Long Position' : 'Short Position'}
            variant="outlined"
            color={isLongPosition ? 'success' : 'error'}
          />
        </Box>

        {/* Alert */}
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="caption">
            This stop loss is calculated using {data.stop_type || 'volatility-based'} analysis. 
            Consider your risk tolerance before setting stops.
          </Typography>
        </Alert>

        {data.calculation_timestamp && (
          <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
            Last calculated: {data.calculation_timestamp}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
