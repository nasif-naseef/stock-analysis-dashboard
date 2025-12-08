import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Grid, Typography, Box, Paper, Divider, LinearProgress } from '@mui/material';
import stockApi from '../api/stockApi';
import TickerSelector from '../components/TickerSelector';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import QuantamentalChart from '../components/charts/QuantamentalChart';

const ScoreBar = ({ label, value, maxValue = 100 }) => (
  <Box mb={2}>
    <Box display="flex" justifyContent="space-between" mb={0.5}>
      <Typography variant="body2">{label}</Typography>
      <Typography variant="body2" fontWeight="bold">
        {value?.toFixed(1) || 'N/A'}
      </Typography>
    </Box>
    <LinearProgress 
      variant="determinate" 
      value={Math.min((value || 0) / maxValue * 100, 100)} 
      sx={{
        height: 8,
        borderRadius: 4,
        backgroundColor: '#e0e0e0',
        '& .MuiLinearProgress-bar': {
          backgroundColor: 
            (value || 0) >= 70 ? '#4caf50' : 
            (value || 0) >= 40 ? '#ff9800' : '#f44336',
          borderRadius: 4,
        },
      }}
    />
  </Box>
);

const DataCard = ({ title, value, subtitle, color }) => (
  <Paper sx={{ p: 2, height: '100%' }}>
    <Typography variant="body2" color="textSecondary">{title}</Typography>
    <Typography variant="h4" sx={{ color: color || 'inherit' }}>{value}</Typography>
    {subtitle && <Typography variant="body2" color="textSecondary">{subtitle}</Typography>}
  </Paper>
);

export default function Quantamental() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');

  const { data, isLoading, error, refetch } = useQuery(
    ['quantamental', selectedTicker],
    () => stockApi.getQuantamental(selectedTicker),
    { enabled: !!selectedTicker }
  );

  // Extract scores with fallback to raw_data
  const extractScores = (responseData) => {
    const scores = responseData?.data || {};
    
    // If direct score fields are present and not null, use them
    if (scores.overall_score !== null && scores.overall_score !== undefined) {
      return scores;
    }
    
    // Fallback: extract from raw_data if available
    if (scores.raw_data) {
      const rawList = Array.isArray(scores.raw_data) ? scores.raw_data : [scores.raw_data];
      if (rawList.length > 0) {
        const rawItem = rawList[0];
        return {
          ...scores,
          overall_score: rawItem.quantamental ?? scores.overall_score,
          value_score: rawItem.valuation ?? scores.value_score,
          growth_score: rawItem.growth ?? scores.growth_score,
          quality_score: rawItem.quality ?? scores.quality_score,
          momentum_score: rawItem.momentum ?? scores.momentum_score,
          income_score: rawItem.income ?? scores.income_score,
          // Extract labels
          overall_label: rawItem.quantamentalLabel?.name,
          value_label: rawItem.valuationLabel?.name,
          growth_label: rawItem.growthLabel?.name,
          quality_label: rawItem.qualityLabel?.name,
          momentum_label: rawItem.momentumLabel?.name,
          income_label: rawItem.incomeLabel?.name,
        };
      }
    }
    
    return scores;
  };

  const scores = extractScores(data);

  const getOverallColor = (score) => {
    if (score >= 70) return '#2e7d32';
    if (score >= 40) return '#ff9800';
    return '#d32f2f';
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Typography variant="h4">Quantamental Analysis</Typography>
        <Box width={200}>
          <TickerSelector
            value={selectedTicker}
            onChange={setSelectedTicker}
            size="small"
          />
        </Box>
      </Box>

      {isLoading ? (
        <LoadingSpinner message={`Loading quantamental data for ${selectedTicker}...`} />
      ) : error ? (
        <ErrorMessage message="Failed to load quantamental data" onRetry={refetch} />
      ) : (
        <Grid container spacing={3}>
          {/* Summary Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Overall Score" 
              value={(scores.overall_score || 0).toFixed(1)}
              color={getOverallColor(scores.overall_score)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Value Score" 
              value={(scores.value_score || 0).toFixed(1)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Growth Score" 
              value={(scores.growth_score || 0).toFixed(1)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Quality Score" 
              value={(scores.quality_score || 0).toFixed(1)}
            />
          </Grid>

          {/* Charts */}
          <Grid item xs={12}>
            <QuantamentalChart 
              data={scores} 
              title={`${selectedTicker} Quantamental Scores`}
            />
          </Grid>

          {/* Score Details */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Score Breakdown</Typography>
              <Divider sx={{ mb: 2 }} />
              <ScoreBar label="Value Score" value={scores.value_score} />
              <ScoreBar label="Growth Score" value={scores.growth_score} />
              <ScoreBar label="Quality Score" value={scores.quality_score} />
              <ScoreBar label="Momentum Score" value={scores.momentum_score} />
              <ScoreBar label="Volatility Score" value={scores.volatility_score} />
            </Paper>
          </Grid>

          {/* Additional Metrics */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Additional Metrics</Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">P/E Ratio</Typography>
                  <Typography variant="h6">{scores.pe_ratio?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">P/B Ratio</Typography>
                  <Typography variant="h6">{scores.pb_ratio?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">ROE</Typography>
                  <Typography variant="h6">{scores.roe ? `${(scores.roe * 100).toFixed(2)}%` : 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Debt/Equity</Typography>
                  <Typography variant="h6">{scores.debt_to_equity?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Revenue Growth</Typography>
                  <Typography variant="h6">{scores.revenue_growth ? `${(scores.revenue_growth * 100).toFixed(2)}%` : 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">EPS Growth</Typography>
                  <Typography variant="h6">{scores.eps_growth ? `${(scores.eps_growth * 100).toFixed(2)}%` : 'N/A'}</Typography>
                </Grid>
              </Grid>
              {scores.timestamp && (
                <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
                  Last updated: {new Date(scores.timestamp).toLocaleString()}
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
