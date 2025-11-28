import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  Grid, Typography, Box, Paper, Divider, Chip, 
  FormControl, InputLabel, Select, MenuItem, Button
} from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';
import stockApi from '../api/stockApi';
import TickerSelector from '../components/TickerSelector';
import TimeRangeSelector from '../components/TimeRangeSelector';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import ComparisonTable from '../components/charts/ComparisonTable';

const DATA_TYPES = [
  { value: 'analyst_ratings', label: 'Analyst Ratings' },
  { value: 'news_sentiment', label: 'News Sentiment' },
  { value: 'quantamental', label: 'Quantamental' },
  { value: 'hedge_fund', label: 'Hedge Fund' },
  { value: 'crowd', label: 'Crowd Sentiment' },
];

export default function Comparison() {
  const [selectedTickers, setSelectedTickers] = useState(['AAPL', 'TSLA']);
  const [timeRange, setTimeRange] = useState('1d');
  const [dataType, setDataType] = useState('analyst_ratings');
  const [comparisonMode, setComparisonMode] = useState('tickers'); // 'tickers' or 'periods'
  const [singleTicker, setSingleTicker] = useState('AAPL');

  // Compare multiple tickers
  const { data: tickersComparisonData, isLoading: tickersLoading, error: tickersError, refetch: refetchTickers } = useQuery(
    ['compareTickers', selectedTickers, timeRange, dataType],
    () => stockApi.compareTickers(selectedTickers.join(','), timeRange, dataType),
    { enabled: comparisonMode === 'tickers' && selectedTickers.length >= 2 }
  );

  // Compare across time periods
  const { data: periodsComparisonData, isLoading: periodsLoading, error: periodsError, refetch: refetchPeriods } = useQuery(
    ['comparePeriods', singleTicker, timeRange, dataType],
    () => stockApi.compareOverTime(singleTicker, '1h,4h,1d,1w', dataType),
    { enabled: comparisonMode === 'periods' }
  );

  const isLoading = comparisonMode === 'tickers' ? tickersLoading : periodsLoading;
  const error = comparisonMode === 'tickers' ? tickersError : periodsError;
  const refetch = comparisonMode === 'tickers' ? refetchTickers : refetchPeriods;

  const tickersComparison = tickersComparisonData?.data || {};
  const periodsComparison = periodsComparisonData?.data || {};
  
  // Safely get tickers array with proper null checking
  const tickersList = Array.isArray(tickersComparison?.tickers) ? tickersComparison.tickers : [];
  const comparisonsList = Array.isArray(periodsComparison?.comparisons) ? periodsComparison.comparisons : [];

  const handleExport = (format) => {
    const data = comparisonMode === 'tickers' ? tickersComparison : periodsComparison;
    const filename = `comparison_${comparisonMode}_${new Date().toISOString().split('T')[0]}.${format}`;
    
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } else if (format === 'csv') {
      // Simple CSV export with safe array access
      let csv = '';
      if (comparisonMode === 'tickers' && tickersList.length > 0) {
        csv = 'Ticker,Metric,Current,Previous,Change,% Change,Trend\n';
        tickersList.forEach(ticker => {
          const comparisons = Array.isArray(ticker?.comparisons) ? ticker.comparisons : [];
          comparisons.forEach(comp => {
            csv += `${ticker?.ticker || 'N/A'},${comp?.metric || 'N/A'},${comp?.current_value ?? 'N/A'},${comp?.previous_value ?? 'N/A'},${comp?.absolute_change ?? 'N/A'},${comp?.percent_change ?? 'N/A'},${comp?.trend || 'N/A'}\n`;
          });
        });
      } else if (comparisonsList.length > 0) {
        csv = 'Metric,Current,Previous,Change,% Change,Trend\n';
        comparisonsList.forEach(comp => {
          csv += `${comp?.metric || 'N/A'},${comp?.current_value ?? 'N/A'},${comp?.previous_value ?? 'N/A'},${comp?.absolute_change ?? 'N/A'},${comp?.percent_change ?? 'N/A'},${comp?.trend || 'N/A'}\n`;
        });
      }
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Typography variant="h4">Comparison</Typography>
        <Box display="flex" gap={1}>
          <Button 
            variant={comparisonMode === 'tickers' ? 'contained' : 'outlined'}
            onClick={() => setComparisonMode('tickers')}
          >
            Compare Tickers
          </Button>
          <Button 
            variant={comparisonMode === 'periods' ? 'contained' : 'outlined'}
            onClick={() => setComparisonMode('periods')}
          >
            Compare Periods
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          {comparisonMode === 'tickers' ? (
            <Grid item xs={12} md={4}>
              <TickerSelector
                value={selectedTickers}
                onChange={setSelectedTickers}
                multiple={true}
                label="Select Tickers (min 2)"
                size="small"
              />
            </Grid>
          ) : (
            <Grid item xs={12} md={4}>
              <TickerSelector
                value={singleTicker}
                onChange={setSingleTicker}
                label="Select Ticker"
                size="small"
              />
            </Grid>
          )}
          <Grid item xs={12} md={3}>
            <TimeRangeSelector
              value={timeRange}
              onChange={setTimeRange}
              size="small"
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Data Type</InputLabel>
              <Select
                value={dataType}
                label="Data Type"
                onChange={(e) => setDataType(e.target.value)}
              >
                {DATA_TYPES.map(type => (
                  <MenuItem key={type.value} value={type.value}>{type.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Box display="flex" gap={1}>
              <Button 
                variant="outlined" 
                size="small" 
                startIcon={<DownloadIcon />}
                onClick={() => handleExport('csv')}
              >
                CSV
              </Button>
              <Button 
                variant="outlined" 
                size="small" 
                startIcon={<DownloadIcon />}
                onClick={() => handleExport('json')}
              >
                JSON
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Results */}
      {isLoading ? (
        <LoadingSpinner message="Loading comparison data..." />
      ) : error ? (
        <ErrorMessage message="Failed to load comparison data" onRetry={refetch} />
      ) : comparisonMode === 'tickers' ? (
        // Tickers comparison view
        <Grid container spacing={3}>
          {selectedTickers.length < 2 ? (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography color="textSecondary">
                  Please select at least 2 tickers to compare
                </Typography>
              </Paper>
            </Grid>
          ) : tickersList.length > 0 ? (
            tickersList.map((ticker, index) => (
              <Grid item xs={12} key={ticker?.ticker || `ticker-${index}`}>
                <Paper sx={{ p: 2 }}>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Typography variant="h6">{ticker?.ticker || 'N/A'}</Typography>
                    <Chip 
                      label={ticker?.overall_trend || 'N/A'} 
                      color={
                        ticker?.overall_trend === 'up' ? 'success' : 
                        ticker?.overall_trend === 'down' ? 'error' : 'default'
                      }
                      size="small"
                    />
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  <ComparisonTable
                    data={(Array.isArray(ticker?.comparisons) ? ticker.comparisons : []).map(c => ({
                      metric: c?.metric || 'N/A',
                      current: c?.current_value,
                      previous: c?.previous_value,
                      change: c?.absolute_change,
                      percentChange: c?.percent_change,
                      trend: c?.trend
                    }))}
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
            ))
          ) : (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography color="textSecondary">
                  No comparison data available. Select tickers and ensure data has been collected.
                </Typography>
              </Paper>
            </Grid>
          )}

          {/* Side-by-side summary */}
          {tickersList.length >= 2 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Summary Comparison</Typography>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  {tickersList.map((ticker, index) => (
                    <Grid item xs={12} sm={6} md={12 / tickersList.length} key={ticker?.ticker || `summary-${index}`}>
                      <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                        <Typography variant="subtitle1" fontWeight="bold">{ticker?.ticker || 'N/A'}</Typography>
                        <Typography variant="body2">
                          Trend: {ticker?.overall_trend || 'N/A'}
                        </Typography>
                        <Typography variant="body2">
                          Changes: {ticker?.positive_changes || 0} positive, {ticker?.negative_changes || 0} negative
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          )}
        </Grid>
      ) : (
        // Periods comparison view
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Typography variant="h6">{singleTicker} - Historical Comparison</Typography>
                <Chip 
                  label={periodsComparison?.overall_trend || 'N/A'} 
                  color={
                    periodsComparison?.overall_trend === 'up' ? 'success' : 
                    periodsComparison?.overall_trend === 'down' ? 'error' : 'default'
                  }
                  size="small"
                />
              </Box>
              <Divider sx={{ mb: 2 }} />
              {comparisonsList.length > 0 ? (
                <ComparisonTable
                  data={comparisonsList.map(c => ({
                    metric: c?.metric || 'N/A',
                    current: c?.current_value,
                    previous: c?.previous_value,
                    change: c?.absolute_change,
                    percentChange: c?.percent_change,
                    trend: c?.trend
                  }))}
                  columns={[
                    { id: 'metric', label: 'Metric', align: 'left' },
                    { id: 'current', label: 'Current', align: 'right' },
                    { id: 'previous', label: `${timeRange} Ago`, align: 'right' },
                    { id: 'change', label: 'Change', align: 'right', format: 'change' },
                    { id: 'percentChange', label: '% Change', align: 'right', format: 'percent' },
                    { id: 'trend', label: 'Trend', align: 'center', format: 'trend' },
                  ]}
                  title=""
                />
              ) : (
                <Typography color="textSecondary" textAlign="center">
                  No comparison data available for the selected period
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
