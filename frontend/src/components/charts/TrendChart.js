import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Box, Typography, Paper } from '@mui/material';
import { format } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function TrendChart({ 
  data, 
  title = 'Trend', 
  dataKey = 'value',
  labelKey = 'timestamp',
  color = '#1976d2',
  fill = true
}) {
  if (!data || data.length === 0) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography color="textSecondary">No trend data available</Typography>
      </Paper>
    );
  }

  const formatLabel = (label) => {
    if (!label) return '';
    try {
      const date = new Date(label);
      return format(date, 'MMM dd HH:mm');
    } catch {
      return label;
    }
  };

  const chartData = {
    labels: data.map(item => formatLabel(item[labelKey])),
    datasets: [
      {
        label: title,
        data: data.map(item => item[dataKey]),
        borderColor: color,
        backgroundColor: fill ? `${color}33` : 'transparent',
        fill: fill,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 6,
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
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: false,
        },
      },
      y: {
        display: true,
        beginAtZero: false,
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ height: 300 }}>
        <Line data={chartData} options={options} />
      </Box>
    </Paper>
  );
}
