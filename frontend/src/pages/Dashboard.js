import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  Grid, Paper, Typography, Box, Card, CardContent, 
  Chip, Alert, Divider
} from '@mui/material';
import { 
  TrendingUp, TrendingDown, Warning, Info 
} from '@mui/icons-material';
import stockApi from '../api/stockApi';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage, { EmptyState } from '../components/ErrorMessage';
import TickerSelector from '../components/TickerSelector';
import { hasData, isValidScore, safeParseNumber } from '../utils/validators';

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

/**
 * Safe number formatting with fallback
 */
const formatNumber = (value, decimals = 2, fallback = 'N/A') => {
  if (value === null || value === undefined || isNaN(value)) return fallback;
  return Number(value).toFixed(decimals);
};

/**
 * Safe price formatting
 */
const formatPrice = (value, fallback = 'N/A') => {
  if (value === null || value === undefined || isNaN(value)) return fallback;
  return `$${Number(value).toFixed(2)}`;
};

export default function Dashboard() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');

  const { 
    data: overviewData, 
    isLoading: overviewLoading, 
    error: overviewError, 
    refetch: refetchOverview 
  } = useQuery(
    ['dashboard', 'overview'],
    () => stockApi.getDashboardOverview(),
    { 
      refetchInterval: 60000,
      staleTime: 30000,
      retry: 2,
    }
  );

  const { 
    data: alertsData, 
    isLoading: alertsLoading,
    error: alertsError 
  } = useQuery(
    ['dashboard', 'alerts', 24],
    () => stockApi.getDashboardAlerts(24),
    { 
      refetchInterval: 60000,
      staleTime: 30000,
      retry: 2,
    }
  );

  const { 
    data: tickerData, 
    isLoading: tickerLoading,
    error: tickerError,
    refetch: refetchTicker
  } = useQuery(
    ['dashboard', 'ticker', selectedTicker],
    () => stockApi.getTickerOverview(selectedTicker),
    { 
      enabled: !!selectedTicker,
      staleTime: 30000,
      retry: 2,
    }
  );

  // Show loading state
  if (overviewLoading) {
    return <LoadingSpinner message="Loading dashboard..." size="large" />;
  }

  // Show error state with retry option
  if (overviewError) {
    return (
      <ErrorMessage 
        title="Dashboard Error"
        message="Failed to load dashboard data. Please check your connection and try again." 
        onRetry={refetchOverview}
        severity="error"
        suggestion="The server may be temporarily unavailable."
      />
    );
  }

  const overview = overviewData?.data || {};
  const summary = overview.summary || {};
  const alerts = alertsData?.data?.alerts || [];
  const ticker = tickerData?.data || {};

  // Validate and sanitize data
  const totalTickers = safeParseNumber(overview.total_tickers, 0);
  const bullishCount = safeParseNumber(summary.bullish_count, 0);
  const bearishCount = safeParseNumber(summary.bearish_count, 0);
  const avgSentiment = safeParseNumber(summary.avg_sentiment, null);

  // Check if we have valid data to display
  const hasOverviewData = totalTickers > 0 || bullishCount > 0 || bearishCount > 0;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Typography variant="h4" component="h1">Dashboard Overview</Typography>
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
            value={totalTickers}
            subtitle="Being tracked"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Bullish Signals"
            value={bullishCount}
            trend={bullishCount > 0 ? 'up' : undefined}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Bearish Signals"
            value={bearishCount}
            trend={bearishCount > 0 ? 'down' : undefined}
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Sentiment"
            value={avgSentiment !== null ? formatNumber(avgSentiment, 2) : 'N/A'}
            subtitle="Overall market"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Selected Ticker Overview */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom component="h2">
              {selectedTicker} Overview
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {tickerLoading ? (
              <LoadingSpinner message={`Loading ${selectedTicker} data...`} size="small" />
            ) : tickerError ? (
              <ErrorMessage 
                message={`Failed to load data for ${selectedTicker}`}
                onRetry={refetchTicker}
                severity="warning"
              />
            ) : !hasData(ticker) ? (
              <EmptyState 
                message={`No data available for ${selectedTicker}`}
                onAction={refetchTicker}
                actionLabel="Refresh"
              />
            ) : (
              <Grid container spacing={2}>
                {/* Analyst Ratings */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="textSecondary">Analyst Rating</Typography>
                  <Typography variant="h6">
                    {ticker.analyst_rating?.consensus_rating || 'N/A'}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {ticker.analyst_rating?.total_analysts 
                      ? `${ticker.analyst_rating.total_analysts} analysts` 
                      : 'No analyst data'}
                  </Typography>
                </Grid>

                {/* News Sentiment */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="textSecondary">News Sentiment</Typography>
                  <Typography variant="h6">
                    {formatNumber(ticker.news_sentiment?.sentiment_score, 2)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {safeParseNumber(ticker.news_sentiment?.total_articles, 0)} articles analyzed
                  </Typography>
                </Grid>

                {/* Quantamental */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="textSecondary">Quantamental Score</Typography>
                  <Typography variant="h6">
                    {formatNumber(ticker.quantamental_score?.overall_score, 1)}
                  </Typography>
                  {isValidScore(ticker.quantamental_score?.overall_score) && (
                    <Typography variant="body2" color="textSecondary">
                      {ticker.quantamental_score.overall_score >= 70 ? 'Strong' : 
                       ticker.quantamental_score.overall_score >= 40 ? 'Moderate' : 'Weak'}
                    </Typography>
                  )}
                </Grid>

                {/* Price Target */}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="textSecondary">Avg Price Target</Typography>
                  <Typography variant="h6">
                    {formatPrice(ticker.analyst_rating?.avg_price_target)}
                  </Typography>
                  {ticker.analyst_rating?.upside_potential !== null && (
                    <Typography variant="body2" color="textSecondary">
                      {formatNumber(ticker.analyst_rating?.upside_potential, 1)}% upside
                    </Typography>
                  )}
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
              <Typography variant="h6" component="h2">Recent Alerts</Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />

            {alertsLoading ? (
              <LoadingSpinner message="Loading alerts..." size="small" />
            ) : alertsError ? (
              <ErrorMessage 
                message="Failed to load alerts"
                severity="warning"
              />
            ) : alerts.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <Info color="action" sx={{ fontSize: 40, mb: 1 }} />
                <Typography color="textSecondary">
                  No alerts in the last 24 hours
                </Typography>
              </Box>
            ) : (
              alerts.slice(0, 10).map((alert, index) => (
                <Alert 
                  key={`alert-${index}-${alert.ticker}`} 
                  severity={
                    alert.severity === 'critical' ? 'error' : 
                    alert.severity === 'high' ? 'warning' : 'info'
                  }
                  sx={{ mb: 1 }}
                >
                  <Typography variant="body2">
                    <strong>{alert.ticker}</strong>: {alert.message || 'Alert details not available'}
                  </Typography>
                </Alert>
              ))
            )}
          </Paper>
        </Grid>

        {/* Tickers Overview */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom component="h2">All Tickers Status</Typography>
            <Divider sx={{ mb: 2 }} />
            
            {!hasOverviewData ? (
              <EmptyState message="No ticker data available" />
            ) : (
              <Box display="flex" flexWrap="wrap" gap={1} role="list" aria-label="Ticker status list">
                {Object.entries(overview.tickers || {}).map(([tickerSymbol, tickerInfo]) => {
                  const consensus = tickerInfo?.analyst_rating?.consensus_rating;
                  const chipColor = 
                    consensus === 'strong_buy' || consensus === 'buy' ? 'success' :
                    consensus === 'strong_sell' || consensus === 'sell' ? 'error' :
                    'default';
                  
                  return (
                    <Chip
                      key={tickerSymbol}
                      label={`${tickerSymbol}: ${consensus || 'N/A'}`}
                      color={chipColor}
                      variant="outlined"
                      onClick={() => setSelectedTicker(tickerSymbol)}
                      clickable
                      role="listitem"
                      aria-label={`View ${tickerSymbol} details, rating: ${consensus || 'not available'}`}
                    />
                  );
                })}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
