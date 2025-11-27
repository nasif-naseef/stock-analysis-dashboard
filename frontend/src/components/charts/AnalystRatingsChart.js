import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Box, Typography, Paper } from '@mui/material';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function AnalystRatingsChart({ data, title = 'Analyst Ratings' }) {
  if (!data) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography color="textSecondary">No analyst ratings data available</Typography>
      </Paper>
    );
  }

  const chartData = {
    labels: ['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'],
    datasets: [
      {
        label: 'Number of Analysts',
        data: [
          data.strong_buy || 0,
          data.buy || 0,
          data.hold || 0,
          data.sell || 0,
          data.strong_sell || 0,
        ],
        backgroundColor: [
          'rgba(76, 175, 80, 0.8)',   // Strong Buy - Green
          'rgba(139, 195, 74, 0.8)',  // Buy - Light Green
          'rgba(255, 193, 7, 0.8)',   // Hold - Yellow
          'rgba(255, 152, 0, 0.8)',   // Sell - Orange
          'rgba(244, 67, 54, 0.8)',   // Strong Sell - Red
        ],
        borderColor: [
          'rgba(76, 175, 80, 1)',
          'rgba(139, 195, 74, 1)',
          'rgba(255, 193, 7, 1)',
          'rgba(255, 152, 0, 1)',
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
        display: false,
      },
      title: {
        display: true,
        text: title,
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.parsed.y} analysts`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ height: 300 }}>
        <Bar data={chartData} options={options} />
      </Box>
      {data.consensus && (
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Consensus: <strong>{data.consensus}</strong>
        </Typography>
      )}
    </Paper>
  );
}
