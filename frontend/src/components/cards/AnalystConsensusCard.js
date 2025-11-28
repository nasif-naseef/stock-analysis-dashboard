import React from 'react';
import {
  Card, CardContent, Typography, Box, Chip, LinearProgress, Divider
} from '@mui/material';
import { TrendingUp, TrendingDown, ShowChart } from '@mui/icons-material';

/**
 * AnalystConsensusCard - Display analyst consensus ratings with visual indicators
 * 
 * @param {Object} data - Analyst consensus data
 * @param {string} data.ticker - Stock ticker symbol
 * @param {number} data.total_ratings - Total number of analyst ratings
 * @param {number} data.buy_ratings - Number of buy ratings
 * @param {number} data.hold_ratings - Number of hold ratings  
 * @param {number} data.sell_ratings - Number of sell ratings
 * @param {string} data.consensus_recommendation - Overall recommendation (e.g., "Moderate Buy")
 * @param {number} data.consensus_rating_score - Numeric score
 * @param {number} data.price_target_high - Highest price target
 * @param {number} data.price_target_low - Lowest price target
 * @param {number} data.price_target_average - Average price target
 */
export default function AnalystConsensusCard({ data }) {
  if (!data || data.error) {
    return (
      <Card>
        <CardContent>
          <Typography color="textSecondary">
            {data?.error || 'No analyst consensus data available'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const total = data.total_ratings || 0;
  const buyPct = total > 0 ? ((data.buy_ratings || 0) / total) * 100 : 0;
  const holdPct = total > 0 ? ((data.hold_ratings || 0) / total) * 100 : 0;
  const sellPct = total > 0 ? ((data.sell_ratings || 0) / total) * 100 : 0;

  const getRecommendationColor = (recommendation) => {
    const rec = (recommendation || '').toLowerCase();
    if (rec.includes('strong buy') || rec.includes('buy')) return 'success';
    if (rec.includes('sell')) return 'error';
    return 'warning';
  };

  const formatPrice = (price) => {
    if (price === null || price === undefined) return 'N/A';
    return `$${Number(price).toFixed(2)}`;
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            Analyst Consensus
          </Typography>
          <Chip 
            label={data.consensus_recommendation || 'N/A'} 
            color={getRecommendationColor(data.consensus_recommendation)}
            size="small"
          />
        </Box>

        <Typography variant="body2" color="textSecondary" gutterBottom>
          Based on {total} analyst{total !== 1 ? 's' : ''}
        </Typography>

        {/* Rating Distribution */}
        <Box my={2}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="success.main">
              Buy: {data.buy_ratings || 0} ({buyPct.toFixed(0)}%)
            </Typography>
            <Typography variant="body2" color="warning.main">
              Hold: {data.hold_ratings || 0} ({holdPct.toFixed(0)}%)
            </Typography>
            <Typography variant="body2" color="error.main">
              Sell: {data.sell_ratings || 0} ({sellPct.toFixed(0)}%)
            </Typography>
          </Box>
          
          <Box display="flex" height={8} borderRadius={1} overflow="hidden">
            <Box sx={{ width: `${buyPct}%`, bgcolor: 'success.main' }} />
            <Box sx={{ width: `${holdPct}%`, bgcolor: 'warning.main' }} />
            <Box sx={{ width: `${sellPct}%`, bgcolor: 'error.main' }} />
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Price Targets */}
        <Typography variant="subtitle2" gutterBottom>
          Price Targets
        </Typography>
        <Box display="flex" justifyContent="space-between" flexWrap="wrap" gap={1}>
          <Box textAlign="center">
            <Typography variant="caption" color="textSecondary">Low</Typography>
            <Typography variant="body2">{formatPrice(data.price_target_low)}</Typography>
          </Box>
          <Box textAlign="center">
            <Typography variant="caption" color="textSecondary">Average</Typography>
            <Typography variant="body1" fontWeight="bold">
              {formatPrice(data.price_target_average)}
            </Typography>
          </Box>
          <Box textAlign="center">
            <Typography variant="caption" color="textSecondary">High</Typography>
            <Typography variant="body2">{formatPrice(data.price_target_high)}</Typography>
          </Box>
        </Box>

        {data.consensus_rating_score && (
          <Box mt={2} textAlign="center">
            <Typography variant="caption" color="textSecondary">
              Rating Score: {Number(data.consensus_rating_score).toFixed(2)}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
