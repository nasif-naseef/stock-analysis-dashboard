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

  // Extract scores with fallback to raw_data
  let value_score = data.value_score;
  let growth_score = data.growth_score;
  let quality_score = data.quality_score;
  let momentum_score = data.momentum_score;
  let volatility_score = data.volatility_score;

  // Fallback to raw_data if direct fields are null/undefined
  if (value_score == null && data.raw_data) {
    const rawList = Array.isArray(data.raw_data) ? data.raw_data : [data.raw_data];
    if (rawList.length > 0) {
      const rawItem = rawList[0];
      value_score = rawItem.valuation ?? value_score;
      growth_score = rawItem.growth ?? growth_score;
      quality_score = rawItem.quality ?? quality_score;
      momentum_score = rawItem.momentum ?? momentum_score;
      // volatility is not in the Trading Central API response, keep it as is
    }
  }

  const scores = {
    'Value': value_score || 0,
    'Growth': growth_score || 0,
    'Quality': quality_score || 0,
    'Momentum': momentum_score || 0,
    'Volatility': volatility_score || 0,
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
      {data.overall_score !== null && data.overall_score !== undefined && (
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Overall Score: <strong>{data.overall_score.toFixed(1)}</strong>
        </Typography>
      )}
    </Paper>
  );
}
