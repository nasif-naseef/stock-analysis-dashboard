import React from 'react';
import {
  Card, CardContent, Typography, Box, Chip, LinearProgress
} from '@mui/material';
import { Article } from '@mui/icons-material';

/**
 * BloggerSentimentCard - Display blogger sentiment analysis
 * 
 * @param {Object} data - Blogger sentiment data
 * @param {string} data.ticker - Stock ticker symbol
 * @param {number} data.bearish - Bearish percentage
 * @param {number} data.neutral - Neutral percentage
 * @param {number} data.bullish - Bullish percentage
 * @param {number} data.bearish_count - Number of bearish articles
 * @param {number} data.neutral_count - Number of neutral articles
 * @param {number} data.bullish_count - Number of bullish articles
 * @param {number} data.score - Overall score
 * @param {number} data.avg - Average score
 */
export default function BloggerSentimentCard({ data }) {
  if (!data || data.error) {
    return (
      <Card>
        <CardContent>
          <Typography color="textSecondary">
            {data?.error || 'No blogger sentiment data available'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const totalCount = (data.bullish_count || 0) + (data.neutral_count || 0) + (data.bearish_count || 0);
  
  const getSentimentLabel = () => {
    if ((data.bullish || 0) > (data.bearish || 0) + 10) return { label: 'Bullish', color: 'success' };
    if ((data.bearish || 0) > (data.bullish || 0) + 10) return { label: 'Bearish', color: 'error' };
    return { label: 'Mixed', color: 'warning' };
  };

  const sentimentInfo = getSentimentLabel();

  const SentimentBar = ({ label, value, count, color }) => (
    <Box mb={1.5}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
        <Typography variant="body2" color={color}>
          {label}: {(value || 0).toFixed(1)}%
        </Typography>
        <Typography variant="caption" color="textSecondary">
          {count || 0} articles
        </Typography>
      </Box>
      <LinearProgress 
        variant="determinate" 
        value={value || 0} 
        color={color === 'success.main' ? 'success' : color === 'error.main' ? 'error' : 'inherit'}
        sx={{ 
          height: 8, 
          borderRadius: 1,
          bgcolor: 'grey.200',
          '& .MuiLinearProgress-bar': {
            bgcolor: color
          }
        }}
      />
    </Box>
  );

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            Blogger Sentiment
          </Typography>
          <Chip 
            label={sentimentInfo.label} 
            color={sentimentInfo.color}
            size="small"
          />
        </Box>

        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Article color="action" fontSize="small" />
          <Typography variant="body2" color="textSecondary">
            {data.ticker} • {totalCount} articles analyzed
          </Typography>
        </Box>

        {/* Sentiment Bars */}
        <Box my={2}>
          <SentimentBar 
            label="Bullish" 
            value={data.bullish} 
            count={data.bullish_count}
            color="success.main"
          />
          <SentimentBar 
            label="Neutral" 
            value={data.neutral} 
            count={data.neutral_count}
            color="grey.500"
          />
          <SentimentBar 
            label="Bearish" 
            value={data.bearish} 
            count={data.bearish_count}
            color="error.main"
          />
        </Box>

        {/* Score */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mt={2} p={1} bgcolor="grey.100" borderRadius={1}>
          <Box>
            <Typography variant="caption" color="textSecondary">
              Score
            </Typography>
            <Typography variant="h6">
              {(data.score || 0).toFixed(1)}
            </Typography>
          </Box>
          <Box textAlign="right">
            <Typography variant="caption" color="textSecondary">
              Average
            </Typography>
            <Typography variant="h6">
              {(data.avg || 0).toFixed(1)}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
