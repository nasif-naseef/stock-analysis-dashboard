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

const getSentimentLabel = (score) => {
  if (score >= 0.5) return { label: 'Very Bullish', color: 'success' };
  if (score >= 0.2) return { label: 'Bullish', color: 'success' };
  if (score >= -0.2) return { label: 'Neutral', color: 'default' };
  if (score >= -0.5) return { label: 'Bearish', color: 'error' };
  return { label: 'Very Bearish', color: 'error' };
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
  const sentimentInfo = getSentimentLabel(sentiment.sentiment_score || 0);

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
          {/* Summary Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Sentiment Score" 
              value={(sentiment.sentiment_score || 0).toFixed(2)}
              color={sentiment.sentiment_score > 0 ? '#2e7d32' : sentiment.sentiment_score < 0 ? '#d32f2f' : 'inherit'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Total Articles" 
              value={sentiment.total_articles || sentiment.article_count || 0}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Positive Articles" 
              value={sentiment.positive_articles || sentiment.bullish_count || 0}
              color="#2e7d32"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Negative Articles" 
              value={sentiment.negative_articles || sentiment.bearish_count || 0}
              color="#d32f2f"
            />
          </Grid>

          {/* Sentiment Gauge */}
          <Grid item xs={12} md={6}>
            <SentimentChart 
              data={sentiment} 
              title={`${selectedTicker} Sentiment Gauge`}
              variant="gauge"
            />
          </Grid>

          {/* Sentiment Distribution */}
          <Grid item xs={12} md={6}>
            <SentimentChart 
              data={sentiment} 
              title={`${selectedTicker} Article Distribution`}
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
                  <Typography variant="subtitle2" color="textSecondary">Buzz Score</Typography>
                  <Typography variant="h6">{sentiment.buzz_score?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">News Velocity</Typography>
                  <Typography variant="h6">{sentiment.news_velocity?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">Sector Avg Sentiment</Typography>
                  <Typography variant="h6">{sentiment.sector_average_sentiment?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Typography variant="subtitle2" color="textSecondary">Sector Avg Buzz</Typography>
                  <Typography variant="h6">{sentiment.sector_average_buzz?.toFixed(2) || 'N/A'}</Typography>
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
