import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Box, FormControlLabel, Switch, CircularProgress
} from '@mui/material';
import adminApi from '../../api/adminApi';

export default function APIKeyForm({ open, onClose, onSuccess, apiKey }) {
  const isEditMode = !!apiKey;
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState({
    service_name: '',
    api_key: '',
    description: '',
    active: true
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (apiKey) {
      setFormData({
        service_name: apiKey.service_name || '',
        api_key: '',
        description: apiKey.description || '',
        active: apiKey.active !== undefined ? apiKey.active : true
      });
    } else {
      setFormData({
        service_name: '',
        api_key: '',
        description: '',
        active: true
      });
    }
    setErrors({});
  }, [apiKey, open]);

  const createMutation = useMutation({
    mutationFn: (data) => adminApi.createAPIKey(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
      onSuccess('API Key created successfully');
      onClose();
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Failed to create API key';
      setErrors({ submit: message });
    }
  });

  const updateMutation = useMutation({
    mutationFn: (data) => adminApi.updateAPIKey(apiKey.service_name, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
      onSuccess('API Key updated successfully');
      onClose();
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Failed to update API key';
      setErrors({ submit: message });
    }
  });

  const handleChange = (e) => {
    const { name, value, checked } = e.target;
    if (name === 'active') {
      setFormData(prev => ({ ...prev, active: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.service_name.trim()) {
      newErrors.service_name = 'Service name is required';
    }
    if (!isEditMode && !formData.api_key.trim()) {
      newErrors.api_key = 'API key is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;

    const submitData = {
      service_name: formData.service_name.trim(),
      description: formData.description.trim() || null,
      active: formData.active
    };

    if (formData.api_key.trim()) {
      submitData.api_key = formData.api_key.trim();
    }

    if (isEditMode) {
      updateMutation.mutate(submitData);
    } else {
      createMutation.mutate(submitData);
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{isEditMode ? 'Edit API Key' : 'Add New API Key'}</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            name="service_name"
            label="Service Name"
            value={formData.service_name}
            onChange={handleChange}
            error={!!errors.service_name}
            helperText={errors.service_name}
            required
            disabled={isEditMode}
            placeholder="e.g., trading_central"
          />
          <TextField
            name="api_key"
            label={isEditMode ? "API Key (leave blank to keep current)" : "API Key"}
            value={formData.api_key}
            onChange={handleChange}
            error={!!errors.api_key}
            helperText={errors.api_key}
            required={!isEditMode}
            type="password"
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
