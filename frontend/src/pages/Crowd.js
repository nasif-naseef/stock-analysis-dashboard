import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Grid, Typography, Box, Paper, Divider, Chip } from '@mui/material';
import stockApi from '../api/stockApi';
import TickerSelector from '../components/TickerSelector';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import SentimentChart from '../components/charts/SentimentChart';
import { PLATFORM_DISTRIBUTION } from '../utils/constants';

const DataCard = ({ title, value, subtitle, color }) => (
  <Paper sx={{ p: 2, height: '100%' }}>
    <Typography variant="body2" color="textSecondary">{title}</Typography>
    <Typography variant="h4" sx={{ color: color || 'inherit' }}>{value}</Typography>
    {subtitle && <Typography variant="body2" color="textSecondary">{subtitle}</Typography>}
  </Paper>
);

const SentimentBar = ({ label, bullish, bearish }) => {
  const total = bullish + bearish;
  const bullishPercent = total > 0 ? (bullish / total) * 100 : 50;
  
  return (
    <Box mb={2}>
      <Box display="flex" justifyContent="space-between" mb={0.5}>
        <Typography variant="body2">{label}</Typography>
        <Typography variant="body2">
          <span style={{ color: '#4caf50' }}>{bullish}</span> / <span style={{ color: '#f44336' }}>{bearish}</span>
        </Typography>
      </Box>
      <Box display="flex" height={8} borderRadius={4} overflow="hidden">
        <Box sx={{ width: `${bullishPercent}%`, backgroundColor: '#4caf50' }} />
        <Box sx={{ width: `${100 - bullishPercent}%`, backgroundColor: '#f44336' }} />
      </Box>
    </Box>
  );
};

export default function Crowd() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');

  const { data, isLoading, error, refetch } = useQuery(
    ['crowd', selectedTicker],
    () => stockApi.getCrowd(selectedTicker),
    { enabled: !!selectedTicker }
  );

  const { data: bloggerData } = useQuery(
    ['blogger', selectedTicker],
    () => stockApi.getBloggerSentiment(selectedTicker),
    { enabled: !!selectedTicker }
  );

  const crowd = data?.data || {};
  const blogger = bloggerData?.data || {};

  // Extract values with fallback to raw_data if needed
  const getCrowdSentimentScore = () => {
    if (crowd.sentiment_score !== null && crowd.sentiment_score !== undefined) {
      return crowd.sentiment_score;
    }
    // Fallback to raw_data if available
    if (crowd.raw_data?.generalStatsAll?.score !== null && crowd.raw_data?.generalStatsAll?.score !== undefined) {
      return crowd.raw_data.generalStatsAll.score;
    }
    return 0;
  };

  const getCrowdMentions = () => {
    if (crowd.mentions_count) return crowd.mentions_count;
    if (crowd.total_posts) return crowd.total_posts;
    // Fallback to raw_data
    if (crowd.raw_data?.generalStatsAll?.portfoliosHolding) {
      return crowd.raw_data.generalStatsAll.portfoliosHolding;
    }
    return 0;
  };

  const sentimentScore = getCrowdSentimentScore();
  const mentionsCount = getCrowdMentions();

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Typography variant="h4">Crowd Wisdom</Typography>
        <Box width={200}>
          <TickerSelector
            value={selectedTicker}
            onChange={setSelectedTicker}
            size="small"
          />
        </Box>
      </Box>

      {isLoading ? (
        <LoadingSpinner message={`Loading crowd data for ${selectedTicker}...`} />
      ) : error ? (
        <ErrorMessage message="Failed to load crowd data" onRetry={refetch} />
      ) : (
        <Grid container spacing={3}>
          {/* Summary Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Crowd Sentiment" 
              value={sentimentScore.toFixed(2)}
              color={sentimentScore > 0 ? '#2e7d32' : sentimentScore < 0 ? '#d32f2f' : 'inherit'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Bullish %" 
              value={crowd.bullish_percent ? `${crowd.bullish_percent.toFixed(1)}%` : 'N/A'}
              color="#2e7d32"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Bearish %" 
              value={crowd.bearish_percent ? `${crowd.bearish_percent.toFixed(1)}%` : 'N/A'}
              color="#d32f2f"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Social Volume" 
              value={mentionsCount.toLocaleString()}
            />
          </Grid>

          {/* Crowd Sentiment Chart */}
          <Grid item xs={12} md={6}>
            <SentimentChart 
              data={{
                bullish_count: crowd.bullish_percent || 0,
                neutral_count: crowd.neutral_percent || 0,
                bearish_count: crowd.bearish_percent || 0,
                sentiment_score: sentimentScore
              }} 
              title={`${selectedTicker} Crowd Sentiment Distribution`}
            />
          </Grid>

          {/* Sentiment Gauge */}
          <Grid item xs={12} md={6}>
            <SentimentChart 
              data={{ sentiment_score: sentimentScore }} 
              title={`${selectedTicker} Sentiment Score`}
              variant="gauge"
            />
          </Grid>

          {/* Social Platform Breakdown */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Platform Analysis</Typography>
              <Divider sx={{ mb: 2 }} />
              {crowd.platform_breakdown ? (
                Object.entries(crowd.platform_breakdown).map(([platform, data]) => (
                  <SentimentBar 
                    key={platform}
                    label={platform.charAt(0).toUpperCase() + platform.slice(1)}
                    bullish={data.bullish || 0}
                    bearish={data.bearish || 0}
                  />
                ))
              ) : (
                <Typography variant="body2" color="textSecondary" align="center">
                  Platform-specific breakdown not available
                </Typography>
              )}
            </Paper>
          </Grid>

          {/* Blogger Sentiment */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Blogger Sentiment</Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Bullish Bloggers</Typography>
                  <Typography variant="h5" color="success.main">
                    {blogger.bullish_articles || blogger.bullish_count || 0}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {blogger.bullish_percent ? `${blogger.bullish_percent.toFixed(0)}%` : ''}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Bearish Bloggers</Typography>
                  <Typography variant="h5" color="error.main">
                    {blogger.bearish_articles || blogger.bearish_count || 0}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {blogger.bearish_percent ? `${blogger.bearish_percent.toFixed(0)}%` : ''}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Blogger Sentiment</Typography>
                  <Typography variant="h5">
                    {blogger.sentiment_score ? blogger.sentiment_score.toFixed(2) : 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Total Bloggers</Typography>
                  <Typography variant="h5">
                    {blogger.total_articles || 
                     (blogger.bullish_articles || 0) + (blogger.bearish_articles || 0) + (blogger.neutral_articles || 0)}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Overall Status */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Crowd Consensus</Typography>
              <Divider sx={{ mb: 2 }} />
              <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
                <Typography variant="body1">Overall Crowd Sentiment:</Typography>
                <Chip 
                  label={
                    sentimentScore > 0.5 ? 'Very Bullish' :
                    sentimentScore > 0.2 ? 'Bullish' :
                    sentimentScore > -0.2 ? 'Neutral' :
                    sentimentScore > -0.5 ? 'Bearish' : 'Very Bearish'
                  }
                  color={
                    sentimentScore > 0.2 ? 'success' :
                    sentimentScore < -0.2 ? 'error' : 'default'
                  }
                />
                <Typography variant="body2" color="textSecondary">
                  Based on {mentionsCount.toLocaleString()} portfolios holding
                </Typography>
              </Box>
              {crowd.timestamp && (
                <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
                  Last updated: {new Date(crowd.timestamp).toLocaleString()}
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
