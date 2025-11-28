import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, FormControlLabel, Checkbox,
  Box, CircularProgress, InputAdornment, IconButton
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';

export default function APIKeyForm({ 
  open, 
  onClose, 
  onSubmit, 
  apiKey = null,
  isSubmitting = false 
}) {
  const isEdit = !!apiKey;
  
  const [formData, setFormData] = useState({
    service_name: '',
    api_key: '',
    description: '',
    is_active: true
  });
  
  const [errors, setErrors] = useState({});
  const [showApiKey, setShowApiKey] = useState(false);
  
  useEffect(() => {
    if (apiKey) {
      setFormData({
        service_name: apiKey.service_name || '',
        api_key: '',
        description: apiKey.description || '',
        is_active: apiKey.is_active !== undefined ? apiKey.is_active : true
      });
    } else {
      setFormData({
        service_name: '',
        api_key: '',
        description: '',
        is_active: true
      });
    }
    setErrors({});
    setShowApiKey(false);
  }, [apiKey, open]);
  
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
    
    if (!formData.service_name.trim()) {
      newErrors.service_name = 'Service name is required';
    } else if (!/^[A-Za-z0-9_\s]+$/.test(formData.service_name)) {
      newErrors.service_name = 'Service name must be alphanumeric with underscores only';
    }
    
    if (!isEdit && !formData.api_key.trim()) {
      newErrors.api_key = 'API key is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    const submitData = {
      service_name: formData.service_name.trim().toLowerCase().replace(/\s+/g, '_'),
      description: formData.description || null,
      is_active: formData.is_active
    };
    
    if (formData.api_key.trim()) {
      submitData.api_key = formData.api_key.trim();
    }
    
    onSubmit(submitData);
  };
  
  const handleClose = () => {
    setFormData({
      service_name: '',
      api_key: '',
      description: '',
      is_active: true
    });
    setErrors({});
    setShowApiKey(false);
    onClose();
  };
  
  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>{isEdit ? 'Edit API Key' : 'Add New API Key'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              name="service_name"
              label="Service Name"
              value={formData.service_name}
              onChange={handleChange}
              error={!!errors.service_name}
              helperText={errors.service_name || 'e.g., TRADING_CENTRAL_TOKEN'}
              required
              disabled={isEdit}
              fullWidth
            />
            
            <TextField
              name="api_key"
              label="API Key"
              value={formData.api_key}
              onChange={handleChange}
              error={!!errors.api_key}
              helperText={
                errors.api_key || 
                (isEdit ? 'Leave blank to keep existing key' : 'Enter the API key value')
              }
              required={!isEdit}
              type={showApiKey ? 'text' : 'password'}
              fullWidth
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowApiKey(!showApiKey)}
                      edge="end"
                    >
                      {showApiKey ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            
            <TextField
              name="description"
              label="Description"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={2}
              helperText="Optional description for this API key"
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
