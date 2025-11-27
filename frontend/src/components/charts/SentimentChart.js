import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Box, Typography, Paper } from '@mui/material';

ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function SentimentChart({ data, title = 'News Sentiment', variant = 'doughnut' }) {
  if (!data) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography color="textSecondary">No sentiment data available</Typography>
      </Paper>
    );
  }

  const getSentimentColor = (sentiment) => {
    if (sentiment >= 0.5) return '#4caf50';  // Positive - Green
    if (sentiment >= 0) return '#8bc34a';    // Slightly Positive
    if (sentiment >= -0.5) return '#ff9800'; // Slightly Negative
    return '#f44336';                         // Negative - Red
  };

  if (variant === 'gauge') {
    const sentimentValue = data.sentiment_score || data.overall_sentiment || 0;
    const gaugeData = {
      labels: ['Sentiment'],
      datasets: [
        {
          data: [sentimentValue + 1, 2 - (sentimentValue + 1)], // Normalize to 0-2 range
          backgroundColor: [getSentimentColor(sentimentValue), '#e0e0e0'],
          borderWidth: 0,
        },
      ],
    };

    return (
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>{title}</Typography>
        <Box sx={{ height: 200, position: 'relative' }}>
          <Doughnut
            data={gaugeData}
            options={{
              circumference: 180,
              rotation: 270,
              cutout: '70%',
              plugins: {
                legend: { display: false },
                tooltip: { enabled: false },
              },
            }}
          />
          <Box
            sx={{
              position: 'absolute',
              bottom: '20%',
              left: '50%',
              transform: 'translateX(-50%)',
              textAlign: 'center',
            }}
          >
            <Typography variant="h4">{sentimentValue.toFixed(2)}</Typography>
            <Typography color="textSecondary" variant="body2">
              {sentimentValue > 0 ? 'Bullish' : sentimentValue < 0 ? 'Bearish' : 'Neutral'}
            </Typography>
          </Box>
        </Box>
      </Paper>
    );
  }

  // Default doughnut chart showing positive/negative/neutral breakdown
  const chartData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        data: [
          data.positive_articles || data.bullish_count || 0,
          data.neutral_articles || data.neutral_count || 0,
          data.negative_articles || data.bearish_count || 0,
        ],
        backgroundColor: [
          'rgba(76, 175, 80, 0.8)',   // Positive - Green
          'rgba(158, 158, 158, 0.8)', // Neutral - Grey
          'rgba(244, 67, 54, 0.8)',   // Negative - Red
        ],
        borderColor: [
          'rgba(76, 175, 80, 1)',
          'rgba(158, 158, 158, 1)',
          'rgba(244, 67, 54, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
      title: {
        display: true,
        text: title,
      },
    },
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ height: 300 }}>
        <Doughnut data={chartData} options={options} />
      </Box>
      {(data.sentiment_score !== undefined || data.overall_sentiment !== undefined) && (
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Overall Score: <strong>{(data.sentiment_score || data.overall_sentiment || 0).toFixed(2)}</strong>
        </Typography>
      )}
    </Paper>
  );
}
