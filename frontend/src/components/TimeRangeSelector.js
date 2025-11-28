import React from 'react';
import { FormControl, InputLabel, Select, MenuItem, ToggleButtonGroup, ToggleButton, Typography } from '@mui/material';
import PropTypes from 'prop-types';

const TIME_RANGES = [
  { value: '1h', label: '1 Hour', shortLabel: '1H' },
  { value: '2h', label: '2 Hours', shortLabel: '2H' },
  { value: '4h', label: '4 Hours', shortLabel: '4H' },
  { value: '6h', label: '6 Hours', shortLabel: '6H' },
  { value: '12h', label: '12 Hours', shortLabel: '12H' },
  { value: '1d', label: '1 Day', shortLabel: '1D' },
  { value: '1w', label: '1 Week', shortLabel: '1W' },
];

export default function TimeRangeSelector({ 
  value, 
  onChange, 
  variant = 'select',
  size = 'medium',
  label = 'Time Range',
  ranges = TIME_RANGES,
  disabled = false,
  error = false,
  helperText = '',
}) {
  if (variant === 'toggle') {
    return (
      <ToggleButtonGroup
        value={value}
        exclusive
        onChange={(e, newValue) => newValue && onChange(newValue)}
        size={size}
        aria-label="Select time range"
        disabled={disabled}
        sx={{
          '& .Mui-selected': {
            backgroundColor: 'primary.main',
            color: 'primary.contrastText',
            '&:hover': {
              backgroundColor: 'primary.dark',
            },
          },
        }}
      >
        {ranges.map((range) => (
          <ToggleButton 
            key={range.value} 
            value={range.value}
            aria-label={`Select ${range.label}`}
            aria-pressed={value === range.value}
          >
            {range.shortLabel || range.label}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    );
  }

  return (
    <FormControl fullWidth size={size} error={error} disabled={disabled}>
      <InputLabel id="time-range-selector-label">{label}</InputLabel>
      <Select
        labelId="time-range-selector-label"
        id="time-range-selector"
        value={value}
        label={label}
        onChange={(e) => onChange(e.target.value)}
        aria-describedby={helperText ? 'time-range-helper-text' : undefined}
      >
        {ranges.map((range) => (
          <MenuItem 
            key={range.value} 
            value={range.value}
            aria-label={`Select ${range.label}`}
          >
            {range.label}
          </MenuItem>
        ))}
      </Select>
      {helperText && (
        <Typography 
          variant="caption" 
          color={error ? 'error' : 'textSecondary'}
          id="time-range-helper-text"
          sx={{ mt: 0.5, ml: 1.5 }}
        >
          {helperText}
        </Typography>
      )}
    </FormControl>
  );
}

TimeRangeSelector.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  variant: PropTypes.oneOf(['select', 'toggle']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  label: PropTypes.string,
  ranges: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    shortLabel: PropTypes.string,
  })),
  disabled: PropTypes.bool,
  error: PropTypes.bool,
  helperText: PropTypes.string,
};
