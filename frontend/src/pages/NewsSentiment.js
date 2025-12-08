import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Grid, Typography, Box, Paper, Divider, Chip } from '@mui/material';
import stockApi from '../api/stockApi';
import TickerSelector from '../components/TickerSelector';
import TimeRangeSelector from '../components/TimeRangeSelector';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import SentimentChart from '../components/charts/SentimentChart';

const DataCard = ({ title, value, subtitle, color }) => (
  <Paper sx={{ p: 2, height: '100%' }}>
    <Typography variant="body2" color="textSecondary">{title}</Typography>
    <Typography variant="h4" sx={{ color: color || 'inherit' }}>{value}</Typography>
    {subtitle && <Typography variant="body2" color="textSecondary">{subtitle}</Typography>}
  </Paper>
);

/**
 * Calculate sentiment score from bullish/bearish percentages
 * Returns value between -1 and 1
 */
const calculateSentimentScore = (bullish, bearish) => {
  if (bullish === null || bullish === undefined || bearish === null || bearish === undefined) {
    return null;
  }
  // Convert to -1 to 1 scale where bullish is positive and bearish is negative
  return (bullish - bearish) / 100;
};

const getSentimentLabel = (bullish, bearish) => {
  if (bullish === null || bullish === undefined) {
    return { label: 'Unknown', color: 'default' };
  }
  const diff = bullish - bearish;
  if (diff >= 30) return { label: 'Very Bullish', color: 'success' };
  if (diff >= 10) return { label: 'Bullish', color: 'success' };
  if (diff >= -10) return { label: 'Neutral', color: 'default' };
  if (diff >= -30) return { label: 'Bearish', color: 'error' };
  return { label: 'Very Bearish', color: 'error' };
};

const formatPercent = (value) => {
  if (value === null || value === undefined) return 'N/A';
  return `${value.toFixed(1)}%`;
};

export default function NewsSentiment() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');
  const [timeRange, setTimeRange] = useState('1d');

  const { data, isLoading, error, refetch } = useQuery(
    ['newsSentiment', selectedTicker],
    () => stockApi.getNewsSentiment(selectedTicker),
    { enabled: !!selectedTicker }
  );

  // Comparison data available for future use
  useQuery(
    ['sentimentComparison', selectedTicker, timeRange],
    () => stockApi.compareOverTime(selectedTicker, timeRange, 'news_sentiment'),
    { enabled: !!selectedTicker }
  );

  const sentiment = data?.data || {};
  
  // Extract notebook-style fields with fallback to raw_data
  let stockBullish = sentiment.stock_bullish_score;
  let stockBearish = sentiment.stock_bearish_score;
  let sectorBullish = sentiment.sector_bullish_score;
  let sectorBearish = sentiment.sector_bearish_score;
  
  // Fallback: Extract from raw_data if direct fields are null/undefined
  if ((stockBullish === null || stockBullish === undefined) && sentiment.raw_data) {
    const rawSentiment = sentiment.raw_data.newsSentimentScore || {};
    const stockData = rawSentiment.stock || {};
    const sectorData = rawSentiment.sector || {};
    
    // Extract and convert from decimal (0-1) to percentage (0-100) if needed
    stockBullish = stockData.bullishPercent;
    stockBearish = stockData.bearishPercent;
    sectorBullish = sectorData.bullishPercent;
    sectorBearish = sectorData.bearishPercent;
    
    // Convert to percentage if values are in decimal format
    if (stockBullish !== null && stockBullish !== undefined && stockBullish <= 1.0) {
      stockBullish = stockBullish * 100;
    }
    if (stockBearish !== null && stockBearish !== undefined && stockBearish <= 1.0) {
      stockBearish = stockBearish * 100;
    }
    if (sectorBullish !== null && sectorBullish !== undefined && sectorBullish <= 1.0) {
      sectorBullish = sectorBullish * 100;
    }
    if (sectorBearish !== null && sectorBearish !== undefined && sectorBearish <= 1.0) {
      sectorBearish = sectorBearish * 100;
    }
  }
  
  // Calculate sentiment score from bullish/bearish
  const sentimentScore = calculateSentimentScore(stockBullish, stockBearish);
  const sentimentInfo = getSentimentLabel(stockBullish, stockBearish);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Typography variant="h4">News Sentiment</Typography>
        <Box display="flex" gap={2}>
          <Box width={200}>
            <TickerSelector
              value={selectedTicker}
              onChange={setSelectedTicker}
              size="small"
            />
          </Box>
          <Box width={150}>
            <TimeRangeSelector
              value={timeRange}
              onChange={setTimeRange}
              size="small"
            />
          </Box>
        </Box>
      </Box>

      {isLoading ? (
        <LoadingSpinner message={`Loading news sentiment for ${selectedTicker}...`} />
      ) : error ? (
        <ErrorMessage message="Failed to load news sentiment" onRetry={refetch} />
      ) : (
        <Grid container spacing={3}>
          {/* Summary Cards - Using notebook-style fields */}
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Stock Bullish" 
              value={formatPercent(stockBullish)}
              color="#2e7d32"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Stock Bearish" 
              value={formatPercent(stockBearish)}
              color="#d32f2f"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Sector Bullish" 
              value={formatPercent(sectorBullish)}
              color="#2e7d32"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Sector Bearish" 
              value={formatPercent(sectorBearish)}
              color="#d32f2f"
            />
          </Grid>

          {/* Sentiment Gauge */}
          <Grid item xs={12} md={6}>
            <SentimentChart 
              data={{ 
                ...sentiment, 
                sentiment_score: sentimentScore,
                bullish_percent: stockBullish,
                bearish_percent: stockBearish
              }} 
              title={`${selectedTicker} Sentiment Gauge`}
              variant="gauge"
            />
          </Grid>

          {/* Sentiment Distribution */}
          <Grid item xs={12} md={6}>
            <SentimentChart 
              data={{ 
                ...sentiment,
                positive_percent: stockBullish,
                negative_percent: stockBearish,
                neutral_percent: stockBullish && stockBearish ? 100 - stockBullish - stockBearish : null
              }} 
              title={`${selectedTicker} Sentiment Distribution`}
              variant="doughnut"
            />
          </Grid>

          {/* Details */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Sentiment Details</Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">Overall Sentiment</Typography>
                  <Chip 
                    label={sentimentInfo.label} 
                    color={sentimentInfo.color}
                    sx={{ mt: 1 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">Stock Bullish Score</Typography>
                  <Typography variant="h6">{formatPercent(stockBullish)}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">Stock Bearish Score</Typography>
                  <Typography variant="h6">{formatPercent(stockBearish)}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">Sector Bullish Score</Typography>
                  <Typography variant="h6">{formatPercent(sectorBullish)}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">Sector Bearish Score</Typography>
                  <Typography variant="h6">{formatPercent(sectorBearish)}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">Net Sentiment</Typography>
                  <Typography variant="h6" sx={{ 
                    color: sentimentScore > 0 ? '#2e7d32' : sentimentScore < 0 ? '#d32f2f' : 'inherit' 
                  }}>
                    {sentimentScore !== null ? sentimentScore.toFixed(2) : 'N/A'}
                  </Typography>
                </Grid>
                {sentiment.timestamp && (
                  <Grid item xs={12}>
                    <Typography variant="caption" color="textSecondary">
                      Last updated: {new Date(sentiment.timestamp).toLocaleString()}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
