import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, FormControlLabel, Checkbox, MenuItem,
  Box, CircularProgress
} from '@mui/material';

const EXCHANGES = ['NASDAQ', 'NYSE', 'AMEX', 'BATS', 'CBOE', 'OTHER'];

export default function TickerForm({ 
  open, 
  onClose, 
  onSubmit, 
  ticker = null,
  isSubmitting = false 
}) {
  const isEdit = !!ticker;
  
  const [formData, setFormData] = useState({
    ticker: '',
    exchange: 'NASDAQ',
    tr_v4_id: '',
    tr_v3_id: '',
    is_active: true,
    description: ''
  });
  
  const [errors, setErrors] = useState({});
  
  useEffect(() => {
    if (ticker) {
      setFormData({
        ticker: ticker.ticker || '',
        exchange: ticker.exchange || 'NASDAQ',
        tr_v4_id: ticker.tr_v4_id || '',
        tr_v3_id: ticker.tr_v3_id || '',
        is_active: ticker.is_active !== undefined ? ticker.is_active : true,
        description: ticker.description || ''
      });
    } else {
      setFormData({
        ticker: '',
        exchange: 'NASDAQ',
        tr_v4_id: '',
        tr_v3_id: '',
        is_active: true,
        description: ''
      });
    }
    setErrors({});
  }, [ticker, open]);
  
  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };
  
  const validate = () => {
    const newErrors = {};
    
    if (!formData.ticker.trim()) {
      newErrors.ticker = 'Symbol is required';
    } else if (formData.ticker.length > 10) {
      newErrors.ticker = 'Symbol must be 10 characters or less';
    } else if (!/^[A-Za-z0-9]+$/.test(formData.ticker)) {
      newErrors.ticker = 'Symbol must be alphanumeric';
    }
    
    if (!formData.exchange) {
      newErrors.exchange = 'Exchange is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    const submitData = {
      ...formData,
      ticker: formData.ticker.toUpperCase().trim(),
      tr_v4_id: formData.tr_v4_id || null,
      tr_v3_id: formData.tr_v3_id || null,
      description: formData.description || null
    };
    
    onSubmit(submitData);
  };
  
  const handleClose = () => {
    setFormData({
      ticker: '',
      exchange: 'NASDAQ',
      tr_v4_id: '',
      tr_v3_id: '',
      is_active: true,
      description: ''
    });
    setErrors({});
    onClose();
  };
  
  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>{isEdit ? 'Edit Ticker' : 'Add New Ticker'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              name="ticker"
              label="Symbol"
              value={formData.ticker}
              onChange={handleChange}
              error={!!errors.ticker}
              helperText={errors.ticker}
              required
              disabled={isEdit}
              inputProps={{ maxLength: 10, style: { textTransform: 'uppercase' } }}
              fullWidth
            />
            
            <TextField
              name="exchange"
              label="Exchange"
              value={formData.exchange}
              onChange={handleChange}
              error={!!errors.exchange}
              helperText={errors.exchange}
              required
              select
              fullWidth
            >
              {EXCHANGES.map(ex => (
                <MenuItem key={ex} value={ex}>{ex}</MenuItem>
              ))}
            </TextField>
            
            <TextField
              name="tr_v4_id"
              label="Trading Central V4 ID"
              value={formData.tr_v4_id}
              onChange={handleChange}
              helperText="Optional identifier for Trading Central V4 API"
              fullWidth
            />
            
            <TextField
              name="tr_v3_id"
              label="Trading Central V3 ID"
              value={formData.tr_v3_id}
              onChange={handleChange}
              helperText="Optional identifier for Trading Central V3 API"
              fullWidth
            />
            
            <TextField
              name="description"
              label="Description"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={2}
              helperText="Optional description for this ticker"
              fullWidth
            />
            
            <FormControlLabel
              control={
                <Checkbox
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleChange}
                />
              }
              label="Active"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="contained" 
            disabled={isSubmitting}
            startIcon={isSubmitting ? <CircularProgress size={20} /> : null}
          >
            {isSubmitting ? 'Saving...' : (isEdit ? 'Update' : 'Create')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
