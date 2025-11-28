import React from 'react';
import {
  Card, CardContent, Typography, Box, Grid, LinearProgress, Tooltip
} from '@mui/material';

/**
 * QuantamentalScoreCard - Display quantamental analysis scores
 * 
 * @param {Object} data - Quantamental score data
 * @param {string} data.ticker - Stock ticker symbol
 * @param {number} data.overall - Overall quantamental score
 * @param {number} data.growth - Growth score
 * @param {number} data.value - Value score
 * @param {number} data.income - Income score
 * @param {number} data.quality - Quality score
 * @param {number} data.momentum - Momentum score
 */
export default function QuantamentalScoreCard({ data }) {
  if (!data || data.error) {
    return (
      <Card>
        <CardContent>
          <Typography color="textSecondary">
            {data?.error || 'No quantamental score data available'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const getScoreColor = (score) => {
    if (score === null || score === undefined) return 'grey.400';
    if (score >= 70) return 'success.main';
    if (score >= 40) return 'warning.main';
    return 'error.main';
  };

  const getScoreLabel = (score) => {
    if (score === null || score === undefined) return 'N/A';
    if (score >= 80) return 'Very Strong';
    if (score >= 60) return 'Strong';
    if (score >= 40) return 'Moderate';
    if (score >= 20) return 'Weak';
    return 'Very Weak';
  };

  const ScoreBar = ({ label, score, tooltip }) => (
    <Tooltip title={tooltip || getScoreLabel(score)} arrow placement="top">
      <Box mb={2}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
          <Typography variant="body2">
            {label}
          </Typography>
          <Typography 
            variant="body2" 
            fontWeight="medium"
            color={getScoreColor(score)}
          >
            {score !== null && score !== undefined ? score : 'N/A'}
          </Typography>
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={score || 0}
          sx={{ 
            height: 10, 
            borderRadius: 1,
            bgcolor: 'grey.200',
            '& .MuiLinearProgress-bar': {
              bgcolor: getScoreColor(score),
              borderRadius: 1
            }
          }}
        />
      </Box>
    </Tooltip>
  );

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" component="h3" gutterBottom>
          Quantamental Scores
        </Typography>
        
        <Typography variant="body2" color="textSecondary" gutterBottom>
          {data.ticker}
        </Typography>

        {/* Overall Score */}
        <Box 
          textAlign="center" 
          my={3} 
          p={2} 
          bgcolor="grey.50" 
          borderRadius={2}
        >
          <Typography variant="caption" color="textSecondary">
            Overall Score
          </Typography>
          <Typography 
            variant="h2" 
            component="div"
            color={getScoreColor(data.overall)}
            fontWeight="bold"
          >
            {data.overall !== null && data.overall !== undefined ? data.overall : 'N/A'}
          </Typography>
          <Typography 
            variant="body2" 
            color={getScoreColor(data.overall)}
          >
            {getScoreLabel(data.overall)}
          </Typography>
        </Box>

        {/* Individual Scores */}
        <Box mt={3}>
          <ScoreBar 
            label="Growth" 
            score={data.growth} 
            tooltip="Measures earnings and revenue growth potential"
          />
          <ScoreBar 
            label="Value" 
            score={data.value} 
            tooltip="Measures valuation relative to fundamentals"
          />
          <ScoreBar 
            label="Quality" 
            score={data.quality} 
            tooltip="Measures financial health and stability"
          />
          <ScoreBar 
            label="Momentum" 
            score={data.momentum} 
            tooltip="Measures price and earnings momentum"
          />
          {data.income !== null && data.income !== undefined && (
            <ScoreBar 
              label="Income" 
              score={data.income} 
              tooltip="Measures dividend yield and sustainability"
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
