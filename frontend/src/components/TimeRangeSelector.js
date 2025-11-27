import React from 'react';
import { FormControl, InputLabel, Select, MenuItem, ToggleButtonGroup, ToggleButton } from '@mui/material';

const TIME_RANGES = [
  { value: '1h', label: '1 Hour' },
  { value: '2h', label: '2 Hours' },
  { value: '4h', label: '4 Hours' },
  { value: '6h', label: '6 Hours' },
  { value: '12h', label: '12 Hours' },
  { value: '1d', label: '1 Day' },
  { value: '1w', label: '1 Week' },
];

export default function TimeRangeSelector({ 
  value, 
  onChange, 
  variant = 'select',
  size = 'medium',
  label = 'Time Range'
}) {
  if (variant === 'toggle') {
    return (
      <ToggleButtonGroup
        value={value}
        exclusive
        onChange={(e, newValue) => newValue && onChange(newValue)}
        size={size}
        aria-label="time range"
      >
        {TIME_RANGES.map((range) => (
          <ToggleButton key={range.value} value={range.value}>
            {range.label}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    );
  }

  return (
    <FormControl fullWidth size={size}>
      <InputLabel id="time-range-selector-label">{label}</InputLabel>
      <Select
        labelId="time-range-selector-label"
        value={value}
        label={label}
        onChange={(e) => onChange(e.target.value)}
      >
        {TIME_RANGES.map((range) => (
          <MenuItem key={range.value} value={range.value}>
            {range.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
