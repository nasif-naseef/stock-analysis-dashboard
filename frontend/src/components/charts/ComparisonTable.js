import React from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Typography, Chip, Box
} from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

const getTrendIcon = (trend) => {
  if (trend === 'up' || trend > 0) return <TrendingUp color="success" />;
  if (trend === 'down' || trend < 0) return <TrendingDown color="error" />;
  return <TrendingFlat color="action" />;
};

const formatChange = (change, isPercent = false) => {
  if (change === null || change === undefined) return '-';
  const formatted = isPercent ? `${change.toFixed(2)}%` : change.toFixed(2);
  return change > 0 ? `+${formatted}` : formatted;
};

const getChangeColor = (change) => {
  if (change > 0) return 'success.main';
  if (change < 0) return 'error.main';
  return 'text.secondary';
};

export default function ComparisonTable({ data, columns, title = 'Comparison' }) {
  if (!data || data.length === 0) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography color="textSecondary">No comparison data available</Typography>
      </Paper>
    );
  }

  const defaultColumns = [
    { id: 'ticker', label: 'Ticker', align: 'left' },
    { id: 'current', label: 'Current', align: 'right' },
    { id: 'previous', label: 'Previous', align: 'right' },
    { id: 'change', label: 'Change', align: 'right', format: 'change' },
    { id: 'percentChange', label: '% Change', align: 'right', format: 'percent' },
    { id: 'trend', label: 'Trend', align: 'center', format: 'trend' },
  ];

  const tableColumns = columns || defaultColumns;

  const renderCell = (row, column) => {
    const value = row[column.id];
    
    if (column.format === 'trend') {
      return getTrendIcon(value);
    }
    
    if (column.format === 'change') {
      return (
        <Typography sx={{ color: getChangeColor(value) }}>
          {formatChange(value)}
        </Typography>
      );
    }
    
    if (column.format === 'percent') {
      return (
        <Typography sx={{ color: getChangeColor(value) }}>
          {formatChange(value, true)}
        </Typography>
      );
    }
    
    if (column.format === 'chip') {
      return <Chip label={value} size="small" />;
    }

    if (typeof value === 'number') {
      return value.toFixed(2);
    }

    return value ?? '-';
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>{title}</Typography>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              {tableColumns.map((column) => (
                <TableCell 
                  key={column.id} 
                  align={column.align || 'left'}
                  sx={{ fontWeight: 'bold' }}
                >
                  {column.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row, index) => (
              <TableRow key={row.ticker || index} hover>
                {tableColumns.map((column) => (
                  <TableCell key={column.id} align={column.align || 'left'}>
                    {renderCell(row, column)}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}
