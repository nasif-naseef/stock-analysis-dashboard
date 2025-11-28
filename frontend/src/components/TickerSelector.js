import React from 'react';
import { 
  FormControl, InputLabel, Select, MenuItem, Chip, Box, 
  CircularProgress, Typography, TextField, InputAdornment 
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import PropTypes from 'prop-types';

const DEFAULT_TICKERS = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META'];

export default function TickerSelector({ 
  value, 
  onChange, 
  multiple = false,
  tickers = DEFAULT_TICKERS,
  label = 'Select Ticker',
  size = 'medium',
  loading = false,
  error = false,
  helperText = '',
  disabled = false,
  showSearch = false,
}) {
  const [searchTerm, setSearchTerm] = React.useState('');
  const [open, setOpen] = React.useState(false);
  const searchTimeoutRef = React.useRef(null);

  const handleChange = (event) => {
    const newValue = event.target.value;
    onChange(newValue);
  };

  // Debounced search handler
  const handleSearchChange = React.useCallback((e) => {
    const value = e.target.value;
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    searchTimeoutRef.current = setTimeout(() => {
      setSearchTerm(value);
    }, 200);
  }, []);

  // Cleanup timeout on unmount
  React.useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);

  // Filter tickers based on search term
  const filteredTickers = React.useMemo(() => {
    if (!searchTerm || !showSearch) return tickers;
    const searchLower = searchTerm.toLowerCase();
    return tickers.filter(ticker => 
      ticker.toLowerCase().includes(searchLower)
    );
  }, [tickers, searchTerm, showSearch]);

  // Handle empty ticker list
  const hasTickers = tickers && tickers.length > 0;

  // Render loading state
  if (loading) {
    return (
      <FormControl fullWidth size={size}>
        <InputLabel id="ticker-selector-label">{label}</InputLabel>
        <Select
          labelId="ticker-selector-label"
          value=""
          label={label}
          disabled
          endAdornment={
            <InputAdornment position="end" sx={{ mr: 2 }}>
              <CircularProgress size={20} />
            </InputAdornment>
          }
        >
          <MenuItem value="" disabled>
            <Typography color="textSecondary">Loading tickers...</Typography>
          </MenuItem>
        </Select>
      </FormControl>
    );
  }

  // Render empty state
  if (!hasTickers) {
    return (
      <FormControl fullWidth size={size} error>
        <InputLabel id="ticker-selector-label">{label}</InputLabel>
        <Select
          labelId="ticker-selector-label"
          value=""
          label={label}
          disabled
        >
          <MenuItem value="" disabled>
            <Typography color="error">No tickers available</Typography>
          </MenuItem>
        </Select>
      </FormControl>
    );
  }

  return (
    <FormControl fullWidth size={size} error={error} disabled={disabled}>
      <InputLabel id="ticker-selector-label">{label}</InputLabel>
      <Select
        labelId="ticker-selector-label"
        id="ticker-selector"
        value={value}
        label={label}
        onChange={handleChange}
        multiple={multiple}
        open={open}
        onOpen={() => setOpen(true)}
        onClose={() => {
          setOpen(false);
          setSearchTerm('');
        }}
        renderValue={multiple ? (selected) => (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {selected.map((ticker) => (
              <Chip 
                key={ticker} 
                label={ticker} 
                size="small" 
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>
        ) : undefined}
        MenuProps={{
          PaperProps: {
            sx: { maxHeight: 300 },
          },
        }}
        aria-describedby={helperText ? 'ticker-helper-text' : undefined}
      >
        {showSearch && (
          <Box sx={{ p: 1, position: 'sticky', top: 0, bgcolor: 'background.paper', zIndex: 1 }}>
            <TextField
              size="small"
              placeholder="Search tickers..."
              defaultValue=""
              onChange={handleSearchChange}
              onKeyDown={(e) => e.stopPropagation()}
              onClick={(e) => e.stopPropagation()}
              fullWidth
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon fontSize="small" />
                  </InputAdornment>
                ),
              }}
              aria-label="Search tickers"
            />
          </Box>
        )}
        {filteredTickers.length === 0 ? (
          <MenuItem disabled>
            <Typography color="textSecondary">No matches found</Typography>
          </MenuItem>
        ) : (
          filteredTickers.map((ticker) => (
            <MenuItem 
              key={ticker} 
              value={ticker}
              aria-label={`Select ${ticker}`}
            >
              {ticker}
            </MenuItem>
          ))
        )}
      </Select>
      {helperText && (
        <Typography 
          variant="caption" 
          color={error ? 'error' : 'textSecondary'}
          id="ticker-helper-text"
          sx={{ mt: 0.5, ml: 1.5 }}
        >
          {helperText}
        </Typography>
      )}
    </FormControl>
  );
}

TickerSelector.propTypes = {
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string),
  ]).isRequired,
  onChange: PropTypes.func.isRequired,
  multiple: PropTypes.bool,
  tickers: PropTypes.arrayOf(PropTypes.string),
  label: PropTypes.string,
  size: PropTypes.oneOf(['small', 'medium']),
  loading: PropTypes.bool,
  error: PropTypes.bool,
  helperText: PropTypes.string,
  disabled: PropTypes.bool,
  showSearch: PropTypes.bool,
};
