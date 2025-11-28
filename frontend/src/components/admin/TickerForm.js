import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Box, FormControl, InputLabel, Select,
  MenuItem, FormControlLabel, Switch, CircularProgress
} from '@mui/material';
import adminApi from '../../api/adminApi';

const EXCHANGES = ['NASDAQ', 'NYSE', 'AMEX', 'OTHER'];

export default function TickerForm({ open, onClose, onSuccess, ticker }) {
  const isEditMode = !!ticker;
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState({
    symbol: '',
    exchange: 'NASDAQ',
    tr_v4_id: '',
    tr_v3_id: '',
    description: '',
    active: true
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (ticker) {
      setFormData({
        symbol: ticker.symbol || '',
        exchange: ticker.exchange || 'NASDAQ',
        tr_v4_id: ticker.tr_v4_id || '',
        tr_v3_id: ticker.tr_v3_id || '',
        description: ticker.description || '',
        active: ticker.active !== undefined ? ticker.active : true
      });
    } else {
      setFormData({
        symbol: '',
        exchange: 'NASDAQ',
        tr_v4_id: '',
        tr_v3_id: '',
        description: '',
        active: true
      });
    }
    setErrors({});
  }, [ticker, open]);

  const createMutation = useMutation({
    mutationFn: (data) => adminApi.createTicker(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickers'] });
      onSuccess('Ticker created successfully');
      onClose();
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Failed to create ticker';
      setErrors({ submit: message });
    }
  });

  const updateMutation = useMutation({
    mutationFn: (data) => adminApi.updateTicker(ticker.symbol, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickers'] });
      onSuccess('Ticker updated successfully');
      onClose();
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Failed to update ticker';
      setErrors({ submit: message });
    }
  });

  const handleChange = (e) => {
    const { name, value, checked } = e.target;
    if (name === 'active') {
      setFormData(prev => ({ ...prev, active: checked }));
    } else if (name === 'symbol') {
      setFormData(prev => ({ ...prev, symbol: value.toUpperCase() }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.symbol.trim()) {
      newErrors.symbol = 'Symbol is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;

    const submitData = {
      ...formData,
      symbol: formData.symbol.trim().toUpperCase(),
      tr_v4_id: formData.tr_v4_id.trim() || null,
      tr_v3_id: formData.tr_v3_id.trim() || null,
      description: formData.description.trim() || null
    };

    if (isEditMode) {
      updateMutation.mutate(submitData);
    } else {
      createMutation.mutate(submitData);
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{isEditMode ? 'Edit Ticker' : 'Add New Ticker'}</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            name="symbol"
            label="Symbol"
            value={formData.symbol}
            onChange={handleChange}
            error={!!errors.symbol}
            helperText={errors.symbol}
            required
            disabled={isEditMode}
            inputProps={{ style: { textTransform: 'uppercase' } }}
          />
          <FormControl fullWidth>
            <InputLabel>Exchange</InputLabel>
            <Select
              name="exchange"
              value={formData.exchange}
              onChange={handleChange}
              label="Exchange"
            >
              {EXCHANGES.map((exchange) => (
                <MenuItem key={exchange} value={exchange}>{exchange}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            name="tr_v4_id"
            label="TR V4 ID"
            value={formData.tr_v4_id}
            onChange={handleChange}
          />
          <TextField
            name="tr_v3_id"
            label="TR V3 ID"
            value={formData.tr_v3_id}
            onChange={handleChange}
          />
          <TextField
            name="description"
            label="Description"
            value={formData.description}
            onChange={handleChange}
            multiline
            rows={3}
          />
          <FormControlLabel
            control={
              <Switch
                name="active"
                checked={formData.active}
                onChange={handleChange}
              />
            }
            label="Active"
          />
          {errors.submit && (
            <Box sx={{ color: 'error.main', fontSize: '0.875rem' }}>
              {errors.submit}
            </Box>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isLoading}>Cancel</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={isLoading}
          startIcon={isLoading ? <CircularProgress size={20} /> : null}
        >
          {isLoading ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
