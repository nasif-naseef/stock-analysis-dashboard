import React from 'react';
import { Radar, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Box, Typography, Paper, Grid } from '@mui/material';

ChartJS.register(
  RadialLinearScale,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend
);

export default function QuantamentalChart({ data, title = 'Quantamental Scores' }) {
  if (!data) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography color="textSecondary">No quantamental data available</Typography>
      </Paper>
    );
  }

  const scores = {
    'Value': data.value_score || 0,
    'Growth': data.growth_score || 0,
    'Quality': data.quality_score || 0,
    'Momentum': data.momentum_score || 0,
    'Volatility': data.volatility_score || 0,
  };

  const radarData = {
    labels: Object.keys(scores),
    datasets: [
      {
        label: 'Scores',
        data: Object.values(scores),
        backgroundColor: 'rgba(25, 118, 210, 0.2)',
        borderColor: 'rgba(25, 118, 210, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(25, 118, 210, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(25, 118, 210, 1)',
      },
    ],
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: title,
      },
    },
    scales: {
      r: {
        angleLines: { display: true },
        suggestedMin: 0,
        suggestedMax: 100,
      },
    },
  };

  const barData = {
    labels: Object.keys(scores),
    datasets: [
      {
        label: 'Score',
        data: Object.values(scores),
        backgroundColor: Object.values(scores).map(score => {
          if (score >= 70) return 'rgba(76, 175, 80, 0.8)';
          if (score >= 40) return 'rgba(255, 193, 7, 0.8)';
          return 'rgba(244, 67, 54, 0.8)';
        }),
        borderColor: Object.values(scores).map(score => {
          if (score >= 70) return 'rgba(76, 175, 80, 1)';
          if (score >= 40) return 'rgba(255, 193, 7, 1)';
          return 'rgba(244, 67, 54, 1)';
        }),
        borderWidth: 1,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
      },
    },
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            <Radar data={radarData} options={radarOptions} />
          </Box>
        </Grid>
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            <Bar data={barData} options={barOptions} />
          </Box>
        </Grid>
      </Grid>
      {data.overall_score !== undefined && (
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Overall Score: <strong>{data.overall_score.toFixed(1)}</strong>
        </Typography>
      )}
    </Paper>
  );
}
