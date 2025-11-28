import React from 'react';
import {
  Card, CardContent, Typography, Box, LinearProgress
} from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

/**
 * NewsSentimentCard - Display news sentiment scores for stock and sector
 * 
 * @param {Object} data - News sentiment data
 * @param {string} data.ticker - Stock ticker symbol
 * @param {number} data.stock_bullish_score - Stock bullish percentage
 * @param {number} data.stock_bearish_score - Stock bearish percentage
 * @param {number} data.sector_bullish_score - Sector bullish percentage
 * @param {number} data.sector_bearish_score - Sector bearish percentage
 */
export default function NewsSentimentCard({ data }) {
  if (!data || data.error) {
    return (
      <Card>
        <CardContent>
          <Typography color="textSecondary">
            {data?.error || 'No news sentiment data available'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const SentimentBar = ({ label, bullish, bearish }) => {
    const bullishPct = bullish || 0;
    const bearishPct = bearish || 0;
    const neutralPct = Math.max(0, 100 - bullishPct - bearishPct);

    return (
      <Box mb={2}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
          <Typography variant="body2" fontWeight="medium">
            {label}
          </Typography>
          <Box display="flex" gap={2}>
            <Box display="flex" alignItems="center" gap={0.5}>
              <TrendingUp color="success" fontSize="small" />
              <Typography variant="caption" color="success.main">
                {bullishPct.toFixed(1)}%
              </Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={0.5}>
              <TrendingDown color="error" fontSize="small" />
              <Typography variant="caption" color="error.main">
                {bearishPct.toFixed(1)}%
              </Typography>
            </Box>
          </Box>
        </Box>
        <Box display="flex" height={12} borderRadius={1} overflow="hidden">
          <Box 
            sx={{ 
              width: `${bullishPct}%`, 
              bgcolor: 'success.main',
              transition: 'width 0.3s ease'
            }} 
          />
          <Box 
            sx={{ 
              width: `${neutralPct}%`, 
              bgcolor: 'grey.300',
              transition: 'width 0.3s ease'
            }} 
          />
          <Box 
            sx={{ 
              width: `${bearishPct}%`, 
              bgcolor: 'error.main',
              transition: 'width 0.3s ease'
            }} 
          />
        </Box>
      </Box>
    );
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" component="h3" gutterBottom>
          News Sentiment
        </Typography>
        
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          {data.ticker}
        </Typography>

        <SentimentBar 
          label="Stock" 
          bullish={data.stock_bullish_score} 
          bearish={data.stock_bearish_score} 
        />
        
        <SentimentBar 
          label="Sector" 
          bullish={data.sector_bullish_score} 
          bearish={data.sector_bearish_score} 
        />

        {/* Summary */}
        <Box mt={2} p={1} bgcolor="grey.100" borderRadius={1}>
          <Typography variant="caption" color="textSecondary">
            Stock sentiment is{' '}
            <strong>
              {(data.stock_bullish_score || 0) > (data.stock_bearish_score || 0) 
                ? 'Bullish' 
                : (data.stock_bullish_score || 0) < (data.stock_bearish_score || 0) 
                  ? 'Bearish' 
                  : 'Neutral'}
            </strong>
            {' '}compared to sector average
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
