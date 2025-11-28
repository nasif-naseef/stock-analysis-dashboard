import React from 'react';
import {
  Card, CardContent, Typography, Box, Grid, Chip
} from '@mui/material';
import { People, TrendingUp, TrendingDown } from '@mui/icons-material';

/**
 * CrowdStatsCard - Display crowd wisdom statistics
 * 
 * @param {Object} data - Crowd stats data
 * @param {string} data.ticker - Stock ticker symbol
 * @param {number} data.portfolio_holding - Number of portfolios holding
 * @param {number} data.amount_of_portfolios - Total portfolios analyzed
 * @param {number} data.percent_allocated - Average percent allocated
 * @param {number} data.percent_over_last_7d - Change over last 7 days
 * @param {number} data.percent_over_last_30d - Change over last 30 days
 * @param {number} data.score - Overall crowd score
 * @param {number} data.frequency - Trading frequency
 */
export default function CrowdStatsCard({ data }) {
  if (!data || data.error) {
    return (
      <Card>
        <CardContent>
          <Typography color="textSecondary">
            {data?.error || 'No crowd statistics available'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 70) return 'success';
    if (score >= 40) return 'warning';
    return 'error';
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined) return 'N/A';
    const formatted = Number(value).toFixed(1);
    return value >= 0 ? `+${formatted}%` : `${formatted}%`;
  };

  const StatItem = ({ label, value, icon, color }) => (
    <Box display="flex" alignItems="center" gap={1} mb={1}>
      {icon}
      <Box>
        <Typography variant="caption" color="textSecondary">
          {label}
        </Typography>
        <Typography variant="body2" fontWeight="medium" color={color}>
          {value}
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            Crowd Wisdom
          </Typography>
          <Chip 
            label={`Score: ${(data.score || 0).toFixed(0)}`}
            color={getScoreColor(data.score || 0)}
            size="small"
          />
        </Box>

        <Typography variant="body2" color="textSecondary" gutterBottom>
          {data.ticker}
        </Typography>

        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Portfolio Holdings */}
          <Grid item xs={6}>
            <Box textAlign="center" p={1} bgcolor="grey.50" borderRadius={1}>
              <People color="primary" />
              <Typography variant="h5">
                {(data.portfolio_holding || 0).toLocaleString()}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Portfolios Holding
              </Typography>
            </Box>
          </Grid>

          {/* Allocation */}
          <Grid item xs={6}>
            <Box textAlign="center" p={1} bgcolor="grey.50" borderRadius={1}>
              <Typography variant="h5">
                {(data.percent_allocated || 0).toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Avg Allocation
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Trend Changes */}
        <Box mt={2}>
          <Typography variant="subtitle2" gutterBottom>
            Recent Changes
          </Typography>
          <Box display="flex" justifyContent="space-around">
            <Box textAlign="center">
              <Typography 
                variant="body2" 
                color={(data.percent_over_last_7d || 0) >= 0 ? 'success.main' : 'error.main'}
                fontWeight="medium"
              >
                {formatPercent(data.percent_over_last_7d)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                7 Days
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography 
                variant="body2" 
                color={(data.percent_over_last_30d || 0) >= 0 ? 'success.main' : 'error.main'}
                fontWeight="medium"
              >
                {formatPercent(data.percent_over_last_30d)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                30 Days
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Additional Stats */}
        {data.frequency !== null && data.frequency !== undefined && (
          <Box mt={2} p={1} bgcolor="grey.100" borderRadius={1}>
            <Typography variant="caption" color="textSecondary">
              Trading Frequency: {(data.frequency || 0).toFixed(2)}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
