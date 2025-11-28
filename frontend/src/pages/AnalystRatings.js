import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Grid, Typography, Box, Paper, Divider } from '@mui/material';
import stockApi from '../api/stockApi';
import TickerSelector from '../components/TickerSelector';
import TimeRangeSelector from '../components/TimeRangeSelector';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import AnalystRatingsChart from '../components/charts/AnalystRatingsChart';
import ComparisonTable from '../components/charts/ComparisonTable';

const DataCard = ({ title, value, subtitle }) => (
  <Paper sx={{ p: 2, height: '100%' }}>
    <Typography variant="body2" color="textSecondary">{title}</Typography>
    <Typography variant="h4">{value}</Typography>
    {subtitle && <Typography variant="body2" color="textSecondary">{subtitle}</Typography>}
  </Paper>
);

/**
 * Extract analyst ratings from API response with fallback to raw_data
 */
const extractRatings = (data) => {
  if (!data) return {};
  
  const rawData = data.raw_data || {};
  const consensus = rawData.analystConsensus || {};
  const priceTarget = rawData.analystPriceTarget || {};
  const prices = rawData.prices || [];
  
  // Get current price from prices array or from parsed data
  let currentPrice = data.current_price;
  if ((currentPrice === null || currentPrice === undefined) && prices.length > 0) {
    currentPrice = prices[prices.length - 1]?.p;
  }
  
  // Calculate upside potential if not available
  const avgPriceTarget = data.avg_price_target ?? priceTarget.average;
  let upsidePotential = data.upside_potential;
  if ((upsidePotential === null || upsidePotential === undefined) && avgPriceTarget && currentPrice && currentPrice > 0) {
    upsidePotential = ((avgPriceTarget - currentPrice) / currentPrice) * 100;
  }
  
  return {
    // Use parsed values first, fallback to raw_data
    strong_buy: data.strong_buy_count ?? 0,
    buy: data.buy_count || consensus.buy || 0,
    hold: data.hold_count || consensus.hold || 0,
    sell: data.sell_count || consensus.sell || 0,
    strong_sell: data.strong_sell_count ?? 0,
    total_analysts: data.total_analysts || consensus.numberOfAnalystRatings || 0,
    consensus: data.consensus_text || data.consensus_rating || consensus.consensus || 'N/A',
    consensus_score: data.consensus_score ?? consensus.consensusRating,
    avg_price_target: avgPriceTarget,
    high_price_target: data.high_price_target ?? priceTarget.high,
    low_price_target: data.low_price_target ?? priceTarget.low,
    current_price: currentPrice,
    upside_potential: upsidePotential,
    timestamp: data.timestamp,
  };
};

export default function AnalystRatings() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');
  const [timeRange, setTimeRange] = useState('1d');

  const { data, isLoading, error, refetch } = useQuery(
    ['analystRatings', selectedTicker],
    () => stockApi.getAnalystRatings(selectedTicker),
    { enabled: !!selectedTicker }
  );

  const { data: comparisonData, isLoading: comparisonLoading } = useQuery(
    ['analystComparison', selectedTicker, timeRange],
    () => stockApi.compareOverTime(selectedTicker, timeRange, 'analyst_ratings'),
    { enabled: !!selectedTicker }
  );

  const ratings = extractRatings(data?.data);
  const comparison = comparisonData?.data || {};

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Typography variant="h4">Analyst Ratings</Typography>
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
        <LoadingSpinner message={`Loading analyst ratings for ${selectedTicker}...`} />
      ) : error ? (
        <ErrorMessage message="Failed to load analyst ratings" onRetry={refetch} />
      ) : (
        <Grid container spacing={3}>
          {/* Summary Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Consensus" 
              value={ratings.consensus || 'N/A'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Total Analysts" 
              value={ratings.total_analysts || (ratings.strong_buy + ratings.buy + ratings.hold + ratings.sell + ratings.strong_sell)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Buy Signals" 
              value={(ratings.strong_buy || 0) + (ratings.buy || 0)}
              subtitle={`Strong Buy: ${ratings.strong_buy || 0}, Buy: ${ratings.buy || 0}`}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Sell Signals" 
              value={(ratings.strong_sell || 0) + (ratings.sell || 0)}
              subtitle={`Strong Sell: ${ratings.strong_sell || 0}, Sell: ${ratings.sell || 0}`}
            />
          </Grid>

          {/* Price Target Card */}
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Avg Price Target" 
              value={ratings.avg_price_target ? `$${ratings.avg_price_target.toFixed(2)}` : 'N/A'}
              subtitle={ratings.high_price_target && ratings.low_price_target 
                ? `High: $${ratings.high_price_target.toFixed(2)}, Low: $${ratings.low_price_target.toFixed(2)}` 
                : null}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Current Price" 
              value={ratings.current_price ? `$${ratings.current_price.toFixed(2)}` : 'N/A'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Upside Potential" 
              value={(ratings.upside_potential !== null && ratings.upside_potential !== undefined) ? `${ratings.upside_potential.toFixed(2)}%` : 'N/A'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Consensus Score" 
              value={ratings.consensus_score ?? 'N/A'}
            />
          </Grid>

          {/* Chart */}
          <Grid item xs={12} md={8}>
            <AnalystRatingsChart 
              data={ratings} 
              title={`${selectedTicker} Analyst Ratings Distribution`}
            />
          </Grid>

          {/* Details */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Rating Details</Typography>
              <Divider sx={{ mb: 2 }} />
              <Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography>Strong Buy</Typography>
                  <Typography color="success.main" fontWeight="bold">{ratings.strong_buy || 0}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography>Buy</Typography>
                  <Typography color="success.light" fontWeight="bold">{ratings.buy || 0}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography>Hold</Typography>
                  <Typography color="warning.main" fontWeight="bold">{ratings.hold || 0}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography>Sell</Typography>
                  <Typography color="error.light" fontWeight="bold">{ratings.sell || 0}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography>Strong Sell</Typography>
                  <Typography color="error.main" fontWeight="bold">{ratings.strong_sell || 0}</Typography>
                </Box>
              </Box>
              {ratings.timestamp && (
                <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
                  Last updated: {new Date(ratings.timestamp).toLocaleString()}
                </Typography>
              )}
            </Paper>
          </Grid>

          {/* Historical Comparison */}
          {comparisonLoading ? (
            <Grid item xs={12}>
              <LoadingSpinner message="Loading comparison data..." size={30} />
            </Grid>
          ) : comparison.comparisons && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Historical Comparison ({timeRange})</Typography>
                <Divider sx={{ mb: 2 }} />
                <ComparisonTable
                  data={comparison.comparisons?.map(c => ({
                    metric: c.metric,
                    current: c.current_value,
                    previous: c.previous_value,
                    change: c.absolute_change,
                    percentChange: c.percent_change,
                    trend: c.trend
                  })) || []}
                  columns={[
                    { id: 'metric', label: 'Metric', align: 'left' },
                    { id: 'current', label: 'Current', align: 'right' },
                    { id: 'previous', label: 'Previous', align: 'right' },
                    { id: 'change', label: 'Change', align: 'right', format: 'change' },
                    { id: 'percentChange', label: '% Change', align: 'right', format: 'percent' },
                    { id: 'trend', label: 'Trend', align: 'center', format: 'trend' },
                  ]}
                  title=""
                />
              </Paper>
            </Grid>
          )}
        </Grid>
      )}
    </Box>
  );
}
