import React from 'react';
import {
  Card, CardContent, Typography, Box, Chip, LinearProgress
} from '@mui/material';
import { Analytics } from '@mui/icons-material';

/**
 * TechnicalSummaryCard - Display technical analysis summary
 * 
 * @param {Object} data - Technical summary data
 * @param {string} data.ticker - Stock ticker symbol
 * @param {Array} data.summaries - Array of technical summaries
 */
export default function TechnicalSummaryCard({ data }) {
  if (!data || data.error) {
    return (
      <Card>
        <CardContent>
          <Typography color="textSecondary">
            {data?.error || 'No technical summary data available'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const summaries = data.summaries || [];
  const singleSummary = summaries.length === 0 ? data : summaries[0];

  const getRecommendationColor = (recommendation) => {
    const rec = (recommendation || '').toLowerCase();
    if (rec.includes('strong buy') || rec.includes('buy')) return 'success';
    if (rec.includes('strong sell') || rec.includes('sell')) return 'error';
    return 'warning';
  };

  const getSignalStrengthColor = (strength) => {
    if (strength >= 70) return 'success.main';
    if (strength >= 40) return 'warning.main';
    return 'error.main';
  };

  // If we have a single summary with direct fields
  if (singleSummary && (singleSummary.recommendation || singleSummary.signalStrength)) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" component="h3">
              Technical Analysis
            </Typography>
            {singleSummary.recommendation && (
              <Chip 
                label={singleSummary.recommendation}
                color={getRecommendationColor(singleSummary.recommendation)}
                size="small"
              />
            )}
          </Box>

          <Typography variant="body2" color="textSecondary" gutterBottom>
            {singleSummary.symbol || data.ticker} 
            {singleSummary.exchange && ` • ${singleSummary.exchange}`}
          </Typography>

          {singleSummary.name && (
            <Typography variant="body2" gutterBottom>
              {singleSummary.name}
            </Typography>
          )}

          {/* Signal Strength */}
          {singleSummary.signalStrength !== null && singleSummary.signalStrength !== undefined && (
            <Box my={3}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle2">
                  Signal Strength
                </Typography>
                <Typography 
                  variant="h6" 
                  color={getSignalStrengthColor(singleSummary.signalStrength)}
                >
                  {Number(singleSummary.signalStrength).toFixed(0)}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={singleSummary.signalStrength || 0}
                sx={{ 
                  height: 10, 
                  borderRadius: 1,
                  bgcolor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: getSignalStrengthColor(singleSummary.signalStrength),
                    borderRadius: 1
                  }
                }}
              />
            </Box>
          )}

          {/* Category */}
          {singleSummary.category && (
            <Box mt={2} p={1} bgcolor="grey.100" borderRadius={1}>
              <Typography variant="caption" color="textSecondary">
                Category: {singleSummary.category}
              </Typography>
            </Box>
          )}

          {/* ISIN */}
          {singleSummary.isin && (
            <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
              ISIN: {singleSummary.isin}
            </Typography>
          )}
        </CardContent>
      </Card>
    );
  }

  // Multiple summaries - show as list
  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            Technical Summaries
          </Typography>
          <Chip 
            label={`${summaries.length} Indicators`}
            size="small"
          />
        </Box>

        <Typography variant="body2" color="textSecondary" gutterBottom>
          {data.ticker}
        </Typography>

        {summaries.length === 0 ? (
          <Box textAlign="center" py={3}>
            <Analytics color="disabled" sx={{ fontSize: 48, mb: 1 }} />
            <Typography color="textSecondary">
              No technical summaries available
            </Typography>
          </Box>
        ) : (
          <Box>
            {summaries.slice(0, 6).map((summary, index) => (
              <Box 
                key={index}
                display="flex" 
                justifyContent="space-between" 
                alignItems="center"
                py={1}
                borderBottom={index < Math.min(summaries.length, 6) - 1 ? 1 : 0}
                borderColor="grey.200"
              >
                <Typography variant="body2">
                  {summary.category || 'Overall'}
                </Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  {summary.score !== null && summary.score !== undefined && (
                    <Typography variant="body2" fontWeight="medium">
                      {Number(summary.score).toFixed(1)}
                    </Typography>
                  )}
                  {summary.signal && (
                    <Chip 
                      label={summary.signal}
                      size="small"
                      color={getRecommendationColor(summary.signal)}
                      variant="outlined"
                    />
                  )}
                </Box>
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
