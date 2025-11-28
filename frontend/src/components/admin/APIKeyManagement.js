import React, { useState } from 'react';
import {
  Paper, Typography, Box, Button, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, IconButton, Chip, Switch,
  CircularProgress, Tooltip
} from '@mui/material';
import {
  Add as AddIcon, Edit as EditIcon, Refresh as RefreshIcon,
  Key as KeyIcon
} from '@mui/icons-material';
import APIKeyForm from './APIKeyForm';

export default function APIKeyManagement({
  apiKeys,
  isLoading,
  onRefresh,
  onCreate,
  onUpdate,
  isCreating,
  isUpdating
}) {
  const [formOpen, setFormOpen] = useState(false);
  const [editApiKey, setEditApiKey] = useState(null);
  
  const handleAdd = () => {
    setEditApiKey(null);
    setFormOpen(true);
  };
  
  const handleEdit = (apiKey) => {
    setEditApiKey(apiKey);
    setFormOpen(true);
  };
  
  const handleFormSubmit = async (data) => {
    if (editApiKey) {
      await onUpdate(editApiKey.service_name, data);
    } else {
      await onCreate(data);
    }
    setFormOpen(false);
    setEditApiKey(null);
  };
  
  const handleToggleActive = async (apiKey) => {
    await onUpdate(apiKey.service_name, { is_active: !apiKey.is_active });
  };
  
  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString();
  };
  
  return (
    <Paper sx={{ p: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">API Key Management</Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={onRefresh} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAdd}
            size="small"
          >
            Add API Key
          </Button>
        </Box>
      </Box>
      
      {isLoading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Service Name</TableCell>
                <TableCell>Key Value</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Active</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {apiKeys?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography color="textSecondary">No API keys configured</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                apiKeys?.map((apiKey) => (
                  <TableRow key={apiKey.service_name} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <KeyIcon fontSize="small" color="action" />
                        <Typography variant="body2" fontFamily="monospace">
                          {apiKey.service_name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={apiKey.api_key_masked} 
                        size="small" 
                        variant="outlined"
                        sx={{ fontFamily: 'monospace' }}
                      />
                    </TableCell>
                    <TableCell>
                      {apiKey.description || <Typography color="textSecondary" variant="body2">-</Typography>}
                    </TableCell>
                    <TableCell>
                      <Switch
                        size="small"
                        checked={apiKey.is_active}
                        onChange={() => handleToggleActive(apiKey)}
                        disabled={isUpdating}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {formatDate(apiKey.updated_at)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Edit">
                        <IconButton size="small" onClick={() => handleEdit(apiKey)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      
      <APIKeyForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditApiKey(null);
        }}
        onSubmit={handleFormSubmit}
        apiKey={editApiKey}
        isSubmitting={isCreating || isUpdating}
      />
    </Paper>
  );
}
