import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Grid, Typography, Box, Paper, Divider, Chip, ToggleButtonGroup, ToggleButton } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';
import stockApi from '../api/stockApi';
import TickerSelector from '../components/TickerSelector';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const DataCard = ({ title, value, subtitle, color, signal }) => (
  <Paper sx={{ p: 2, height: '100%' }}>
    <Typography variant="body2" color="textSecondary">{title}</Typography>
    <Box display="flex" alignItems="center" gap={1}>
      <Typography variant="h4" sx={{ color: color || 'inherit' }}>{value}</Typography>
      {signal && (
        <Chip 
          size="small" 
          label={signal} 
          color={signal === 'Buy' ? 'success' : signal === 'Sell' ? 'error' : 'default'}
        />
      )}
    </Box>
    {subtitle && <Typography variant="body2" color="textSecondary">{subtitle}</Typography>}
  </Paper>
);

const IndicatorRow = ({ name, value, signal }) => (
  <Box display="flex" justifyContent="space-between" alignItems="center" py={1} borderBottom="1px solid #eee">
    <Typography variant="body2">{name}</Typography>
    <Box display="flex" alignItems="center" gap={1}>
      <Typography variant="body2" fontWeight="bold">{value?.toFixed(2) || 'N/A'}</Typography>
      {signal && (
        <Chip 
          size="small" 
          label={signal} 
          color={signal === 'Buy' ? 'success' : signal === 'Sell' ? 'error' : 'default'}
          sx={{ minWidth: 60 }}
        />
      )}
    </Box>
  </Box>
);

export default function Technical() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');
  const [timeframe, setTimeframe] = useState('1d');

  const { data, isLoading, error, refetch } = useQuery(
    ['technical', selectedTicker, timeframe],
    () => stockApi.getTechnical(selectedTicker, timeframe),
    { enabled: !!selectedTicker }
  );

  const { data: targetData } = useQuery(
    ['targetPrice', selectedTicker],
    () => stockApi.getTargetPrice(selectedTicker),
    { enabled: !!selectedTicker }
  );

  const technical = data?.data || {};
  const targetPrice = targetData?.data || {};

  const getOverallSignal = () => {
    const buySignals = (technical.ma_buy_signals || 0) + (technical.oscillator_buy_signals || 0);
    const sellSignals = (technical.ma_sell_signals || 0) + (technical.oscillator_sell_signals || 0);
    
    if (buySignals > sellSignals + 2) return { text: 'Strong Buy', color: 'success' };
    if (buySignals > sellSignals) return { text: 'Buy', color: 'success' };
    if (sellSignals > buySignals + 2) return { text: 'Strong Sell', color: 'error' };
    if (sellSignals > buySignals) return { text: 'Sell', color: 'error' };
    return { text: 'Neutral', color: 'default' };
  };

  const overallSignal = getOverallSignal();

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Typography variant="h4">Technical Analysis</Typography>
        <Box display="flex" gap={2} alignItems="center">
          <ToggleButtonGroup
            value={timeframe}
            exclusive
            onChange={(e, newValue) => newValue && setTimeframe(newValue)}
            size="small"
          >
            <ToggleButton value="1h">1H</ToggleButton>
            <ToggleButton value="4h">4H</ToggleButton>
            <ToggleButton value="1d">1D</ToggleButton>
            <ToggleButton value="1w">1W</ToggleButton>
          </ToggleButtonGroup>
          <Box width={200}>
            <TickerSelector
              value={selectedTicker}
              onChange={setSelectedTicker}
              size="small"
            />
          </Box>
        </Box>
      </Box>

      {isLoading ? (
        <LoadingSpinner message={`Loading technical data for ${selectedTicker}...`} />
      ) : error ? (
        <ErrorMessage message="Failed to load technical data" onRetry={refetch} />
      ) : (
        <Grid container spacing={3}>
          {/* Summary Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Overall Signal" 
              value={overallSignal.text}
              color={overallSignal.color === 'success' ? '#2e7d32' : overallSignal.color === 'error' ? '#d32f2f' : 'inherit'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="RSI (14)" 
              value={(technical.rsi || 0).toFixed(2)}
              signal={technical.rsi > 70 ? 'Sell' : technical.rsi < 30 ? 'Buy' : 'Neutral'}
              subtitle={technical.rsi > 70 ? 'Overbought' : technical.rsi < 30 ? 'Oversold' : 'Normal'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="MACD" 
              value={(technical.macd || 0).toFixed(4)}
              signal={technical.macd_signal === 'bullish' ? 'Buy' : technical.macd_signal === 'bearish' ? 'Sell' : 'Neutral'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <DataCard 
              title="Target Price" 
              value={targetPrice.target_mean ? `$${targetPrice.target_mean.toFixed(2)}` : 'N/A'}
              subtitle={targetPrice.target_low && targetPrice.target_high ? 
                `Range: $${targetPrice.target_low.toFixed(2)} - $${targetPrice.target_high.toFixed(2)}` : ''}
            />
          </Grid>

          {/* Moving Averages */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Moving Averages</Typography>
              <Divider sx={{ mb: 2 }} />
              <IndicatorRow name="SMA 20" value={technical.sma_20} signal={technical.sma_20_signal} />
              <IndicatorRow name="SMA 50" value={technical.sma_50} signal={technical.sma_50_signal} />
              <IndicatorRow name="SMA 100" value={technical.sma_100} signal={technical.sma_100_signal} />
              <IndicatorRow name="SMA 200" value={technical.sma_200} signal={technical.sma_200_signal} />
              <IndicatorRow name="EMA 20" value={technical.ema_20} signal={technical.ema_20_signal} />
              <IndicatorRow name="EMA 50" value={technical.ema_50} signal={technical.ema_50_signal} />
              <Box display="flex" justifyContent="space-between" mt={2}>
                <Chip label={`Buy: ${technical.ma_buy_signals || 0}`} color="success" size="small" />
                <Chip label={`Sell: ${technical.ma_sell_signals || 0}`} color="error" size="small" />
                <Chip label={`Neutral: ${technical.ma_neutral_signals || 0}`} size="small" />
              </Box>
            </Paper>
          </Grid>

          {/* Oscillators */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Oscillators</Typography>
              <Divider sx={{ mb: 2 }} />
              <IndicatorRow name="RSI (14)" value={technical.rsi} signal={technical.rsi > 70 ? 'Sell' : technical.rsi < 30 ? 'Buy' : 'Neutral'} />
              <IndicatorRow name="Stochastic %K" value={technical.stoch_k} signal={technical.stoch_signal} />
              <IndicatorRow name="CCI (20)" value={technical.cci} signal={technical.cci_signal} />
              <IndicatorRow name="ADX (14)" value={technical.adx} />
              <IndicatorRow name="Williams %R" value={technical.williams_r} signal={technical.williams_signal} />
              <IndicatorRow name="MACD" value={technical.macd} signal={technical.macd_signal === 'bullish' ? 'Buy' : technical.macd_signal === 'bearish' ? 'Sell' : 'Neutral'} />
              <Box display="flex" justifyContent="space-between" mt={2}>
                <Chip label={`Buy: ${technical.oscillator_buy_signals || 0}`} color="success" size="small" />
                <Chip label={`Sell: ${technical.oscillator_sell_signals || 0}`} color="error" size="small" />
                <Chip label={`Neutral: ${technical.oscillator_neutral_signals || 0}`} size="small" />
              </Box>
            </Paper>
          </Grid>

          {/* Pivot Points */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Pivot Points</Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="subtitle2" color="error.main">Resistance</Typography>
                  <Typography>R3: {technical.r3?.toFixed(2) || 'N/A'}</Typography>
                  <Typography>R2: {technical.r2?.toFixed(2) || 'N/A'}</Typography>
                  <Typography>R1: {technical.r1?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="subtitle2" color="primary.main">Pivot</Typography>
                  <Typography variant="h6" sx={{ mt: 2 }}>{technical.pivot?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="subtitle2" color="success.main">Support</Typography>
                  <Typography>S1: {technical.s1?.toFixed(2) || 'N/A'}</Typography>
                  <Typography>S2: {technical.s2?.toFixed(2) || 'N/A'}</Typography>
                  <Typography>S3: {technical.s3?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Additional Info */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Additional Indicators</Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">ATR (14)</Typography>
                  <Typography variant="h6">{technical.atr?.toFixed(4) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Bollinger Upper</Typography>
                  <Typography variant="h6">{technical.bb_upper?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Bollinger Lower</Typography>
                  <Typography variant="h6">{technical.bb_lower?.toFixed(2) || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="textSecondary">Volume</Typography>
                  <Typography variant="h6">{technical.volume?.toLocaleString() || 'N/A'}</Typography>
                </Grid>
              </Grid>
              {technical.timestamp && (
                <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
                  Last updated: {new Date(technical.timestamp).toLocaleString()}
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
