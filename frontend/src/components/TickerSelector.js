import React from 'react';
import { FormControl, InputLabel, Select, MenuItem, Chip, Box } from '@mui/material';

const DEFAULT_TICKERS = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META'];

export default function TickerSelector({ 
  value, 
  onChange, 
  multiple = false,
  tickers = DEFAULT_TICKERS,
  label = 'Select Ticker',
  size = 'medium'
}) {
  const handleChange = (event) => {
    const newValue = event.target.value;
    onChange(newValue);
  };

  return (
    <FormControl fullWidth size={size}>
      <InputLabel id="ticker-selector-label">{label}</InputLabel>
      <Select
        labelId="ticker-selector-label"
        value={value}
        label={label}
        onChange={handleChange}
        multiple={multiple}
        renderValue={multiple ? (selected) => (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {selected.map((ticker) => (
              <Chip key={ticker} label={ticker} size="small" />
            ))}
          </Box>
        ) : undefined}
      >
        {tickers.map((ticker) => (
          <MenuItem key={ticker} value={ticker}>
            {ticker}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
