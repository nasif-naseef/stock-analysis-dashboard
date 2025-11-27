import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  Grid, Paper, Typography, Box, Card, CardContent, 
  Chip, Alert, Divider
} from '@mui/material';
import { 
  TrendingUp, TrendingDown, Warning 
} from '@mui/icons-material';
import stockApi from '../api/stockApi';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import TickerSelector from '../components/TickerSelector';

const StatCard = ({ title, value, trend, subtitle, color }) => (
  <Card>
    <CardContent>
      <Typography color="textSecondary" gutterBottom variant="body2">
        {title}
      </Typography>
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="h4" component="div" sx={{ color: color || 'inherit' }}>
          {value}
        </Typography>
        {trend === 'up' && <TrendingUp color="success" />}
        {trend === 'down' && <TrendingDown color="error" />}
      </Box>
      {subtitle && (
        <Typography variant="body2" color="textSecondary">
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
);

export default function Dashboard() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');

  const { data: overviewData, isLoading: overviewLoading, error: overviewError, refetch: refetchOverview } = useQuery(
    'dashboardOverview',
    () => stockApi.getDashboardOverview(),
    { refetchInterval: 60000 }
  );

  const { data: alertsData, isLoading: alertsLoading } = useQuery(
    'dashboardAlerts',
    () => stockApi.getDashboardAlerts(24),
    { refetchInterval: 60000 }
  );

  const { data: tickerData, isLoading: tickerLoading } = useQuery(
    ['tickerOverview', selectedTicker],
    () => stockApi.getTickerOverview(selectedTicker),
    { enabled: !!selectedTicker }
  );

  if (overviewLoading) return <LoadingSpinner message="Loading dashboard..." />;
  if (overviewError) return <ErrorMessage message="Failed to load dashboard data" onRetry={refetchOverview} />;

  const overview = overviewData?.data || {};
  const alerts = alertsData?.data?.alerts || [];
  const ticker = tickerData?.data || {};

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Dashboard Overview</Typography>
        <Box width={200}>
          <TickerSelector
            value={selectedTicker}
            onChange={setSelectedTicker}
            size="small"
            label="Focus Ticker"
          />
        </Box>
      </Box>

      {/* Summary Statistics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Tickers"
            value={overview.total_tickers || 0}
            subtitle="Being tracked"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Bullish Signals"
            value={overview.bullish_count || 0}
            trend="up"
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Bearish Signals"
            value={overview.bearish_count || 0}
            trend="down"
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Sentiment"
            value={(overview.avg_sentiment || 0).toFixed(2)}
            subtitle="Overall market"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Selected Ticker Overview */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {selectedTicker} Overview
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {tickerLoading ? (
              <LoadingSpinner message={`Loading ${selectedTicker} data...`} size={30} />
            ) : (
              <Grid container spacing={2}>
                {/* Analyst Ratings */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="textSecondary">Analyst Rating</Typography>
                  <Typography variant="h6">
                    {ticker.analyst_ratings?.consensus || 'N/A'}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {ticker.analyst_ratings ? 
                      `${ticker.analyst_ratings.strong_buy || 0} Strong Buy, ${ticker.analyst_ratings.buy || 0} Buy` : 
                      'No data'}
                  </Typography>
                </Grid>

                {/* News Sentiment */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="textSecondary">News Sentiment</Typography>
                  <Typography variant="h6">
                    {ticker.news_sentiment?.sentiment_score?.toFixed(2) || 'N/A'}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {ticker.news_sentiment?.total_articles || 0} articles analyzed
                  </Typography>
                </Grid>

                {/* Quantamental */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="textSecondary">Quantamental Score</Typography>
                  <Typography variant="h6">
                    {ticker.quantamental?.overall_score?.toFixed(1) || 'N/A'}
                  </Typography>
                </Grid>

                {/* Target Price */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="textSecondary">Target Price</Typography>
                  <Typography variant="h6">
                    ${ticker.target_price?.target_mean?.toFixed(2) || 'N/A'}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Range: ${ticker.target_price?.target_low?.toFixed(2) || 'N/A'} - ${ticker.target_price?.target_high?.toFixed(2) || 'N/A'}
                  </Typography>
                </Grid>
              </Grid>
            )}
          </Paper>
        </Grid>

        {/* Alerts */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, maxHeight: 400, overflow: 'auto' }}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <Warning color="warning" />
              <Typography variant="h6">Recent Alerts</Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />

            {alertsLoading ? (
              <LoadingSpinner message="Loading alerts..." size={30} />
            ) : alerts.length === 0 ? (
              <Typography color="textSecondary">No alerts in the last 24 hours</Typography>
            ) : (
              alerts.slice(0, 10).map((alert, index) => (
                <Alert 
                  key={index} 
                  severity={alert.severity === 'critical' ? 'error' : alert.severity === 'high' ? 'warning' : 'info'}
                  sx={{ mb: 1 }}
                >
                  <Typography variant="body2">
                    <strong>{alert.ticker}</strong>: {alert.message}
                  </Typography>
                </Alert>
              ))
            )}
          </Paper>
        </Grid>

        {/* Tickers Overview */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>All Tickers Status</Typography>
            <Divider sx={{ mb: 2 }} />
            <Box display="flex" flexWrap="wrap" gap={1}>
              {(overview.tickers || []).map((tickerInfo) => (
                <Chip
                  key={tickerInfo.ticker}
                  label={`${tickerInfo.ticker}: ${tickerInfo.consensus || 'N/A'}`}
                  color={
                    tickerInfo.consensus === 'Strong Buy' || tickerInfo.consensus === 'Buy' ? 'success' :
                    tickerInfo.consensus === 'Strong Sell' || tickerInfo.consensus === 'Sell' ? 'error' :
                    'default'
                  }
                  variant="outlined"
                  onClick={() => setSelectedTicker(tickerInfo.ticker)}
                />
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
