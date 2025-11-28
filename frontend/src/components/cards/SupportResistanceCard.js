import React from 'react';
import {
  Card, CardContent, Typography, Box, Table, TableBody, TableCell, TableRow
} from '@mui/material';
import { Support, Height } from '@mui/icons-material';

/**
 * SupportResistanceCard - Display support and resistance price levels
 * 
 * @param {Object} data - Support/resistance data
 * @param {string} data.symbol - Stock symbol
 * @param {string} data.date - Data date
 * @param {string} data.exchange - Exchange
 * @param {number} data.support_10 - 10-day support
 * @param {number} data.resistance_10 - 10-day resistance
 * @param {number} data.support_20 - 20-day support
 * @param {number} data.resistance_20 - 20-day resistance
 * @param {number} data.support_40 - 40-day support
 * @param {number} data.resistance_40 - 40-day resistance
 * @param {number} data.support_100 - 100-day support
 * @param {number} data.resistance_100 - 100-day resistance
 */
export default function SupportResistanceCard({ data, currentPrice }) {
  if (!data || data.error) {
    return (
      <Card>
        <CardContent>
          <Typography color="textSecondary">
            {data?.error || 'No support/resistance data available'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const formatPrice = (price) => {
    if (price === null || price === undefined) return 'N/A';
    return `$${Number(price).toFixed(2)}`;
  };

  const getPriceProximity = (level, current) => {
    if (!current || !level) return null;
    const diff = ((level - current) / current) * 100;
    return diff.toFixed(1);
  };

  const levels = [
    { period: '10-Day', support: data.support_10, resistance: data.resistance_10 },
    { period: '20-Day', support: data.support_20, resistance: data.resistance_20 },
    { period: '40-Day', support: data.support_40, resistance: data.resistance_40 },
    { period: '100-Day', support: data.support_100, resistance: data.resistance_100 },
    { period: '250-Day', support: data.support_250, resistance: data.resistance_250 },
  ].filter(l => l.support !== null || l.resistance !== null);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" component="h3" gutterBottom>
          Support & Resistance Levels
        </Typography>
        
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="body2" color="textSecondary">
            {data.symbol} • {data.exchange}
          </Typography>
          <Typography variant="caption" color="textSecondary">
            {data.date}
          </Typography>
        </Box>

        <Table size="small">
          <TableBody>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Period</TableCell>
              <TableCell sx={{ fontWeight: 'bold', color: 'success.main' }}>Support</TableCell>
              <TableCell sx={{ fontWeight: 'bold', color: 'error.main' }}>Resistance</TableCell>
            </TableRow>
            {levels.map((level) => (
              <TableRow key={level.period}>
                <TableCell>{level.period}</TableCell>
                <TableCell>
                  <Typography variant="body2" color="success.main">
                    {formatPrice(level.support)}
                  </Typography>
                  {currentPrice && level.support && (
                    <Typography variant="caption" color="textSecondary">
                      ({getPriceProximity(level.support, currentPrice)}%)
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="error.main">
                    {formatPrice(level.resistance)}
                  </Typography>
                  {currentPrice && level.resistance && (
                    <Typography variant="caption" color="textSecondary">
                      ({getPriceProximity(level.resistance, currentPrice)}%)
                    </Typography>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {levels.length === 0 && (
          <Typography variant="body2" color="textSecondary" textAlign="center" py={2}>
            No support/resistance levels available
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
