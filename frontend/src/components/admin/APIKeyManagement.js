import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box, Paper, Typography, Button, IconButton, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Switch
} from '@mui/material';
import { Add, Edit } from '@mui/icons-material';
import adminApi from '../../api/adminApi';
import APIKeyForm from './APIKeyForm';
import LoadingSpinner from '../LoadingSpinner';
import ErrorMessage from '../ErrorMessage';

const maskKey = (key) => {
  if (!key || key.length < 8) return '********';
  return key.substring(0, 4) + '*'.repeat(Math.min(15, key.length - 8)) + key.substring(key.length - 4);
};

export default function APIKeyManagement({ onNotify }) {
  const queryClient = useQueryClient();
  const [formOpen, setFormOpen] = useState(false);
  const [selectedApiKey, setSelectedApiKey] = useState(null);

  const { data: apiKeysData, isLoading, error, refetch } = useQuery({
    queryKey: ['apiKeys'],
    queryFn: () => adminApi.getAPIKeys(true).then(res => res.data)
  });

  const updateMutation = useMutation({
    mutationFn: ({ serviceName, data }) => adminApi.updateAPIKey(serviceName, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
      onNotify('API key status updated successfully', 'success');
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Failed to update API key';
      onNotify(message, 'error');
    }
  });

  const handleAddClick = () => {
    setSelectedApiKey(null);
    setFormOpen(true);
  };

  const handleEditClick = (apiKey) => {
    setSelectedApiKey(apiKey);
    setFormOpen(true);
  };

  const handleToggleActive = (apiKey) => {
    updateMutation.mutate({
      serviceName: apiKey.service_name,
      data: { ...apiKey, active: !apiKey.active }
    });
  };

  const handleFormSuccess = (message) => {
    onNotify(message, 'success');
  };

  if (isLoading) return <LoadingSpinner message="Loading API keys..." />;
  if (error) return <ErrorMessage message="Failed to load API keys" onRetry={refetch} />;

  const apiKeys = apiKeysData?.api_keys || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">API Key Management</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAddClick}
        >
          Add API Key
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Service Name</TableCell>
              <TableCell>Key (Masked)</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Active</TableCell>
              <TableCell>Last Updated</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {apiKeys.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography color="textSecondary">No API keys configured</Typography>
                </TableCell>
              </TableRow>
            ) : (
              apiKeys.map((apiKey) => (
                <TableRow key={apiKey.service_name}>
                  <TableCell>
                    <Typography fontWeight="bold">{apiKey.service_name}</Typography>
                  </TableCell>
                  <TableCell>
                    <Typography sx={{ fontFamily: 'monospace' }}>
                      {maskKey(apiKey.masked_key || apiKey.api_key)}
                    </Typography>
                  </TableCell>
                  <TableCell>{apiKey.description || 'N/A'}</TableCell>
                  <TableCell>
                    <Switch
                      checked={apiKey.active}
                      onChange={() => handleToggleActive(apiKey)}
                      disabled={updateMutation.isPending}
                    />
                  </TableCell>
                  <TableCell>
                    {apiKey.updated_at 
                      ? new Date(apiKey.updated_at).toLocaleString() 
                      : 'N/A'}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleEditClick(apiKey)}
                      title="Edit API key"
                    >
                      <Edit />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <APIKeyForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={handleFormSuccess}
        apiKey={selectedApiKey}
      />
    </Box>
  );
}
