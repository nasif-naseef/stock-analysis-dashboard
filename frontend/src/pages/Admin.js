import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Box, Typography, Snackbar, Alert, Tabs, Tab } from '@mui/material';
import adminApi from '../api/adminApi';
import ConfigStatus from '../components/admin/ConfigStatus';
import TickerManagement from '../components/admin/TickerManagement';
import APIKeyManagement from '../components/admin/APIKeyManagement';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  );
}

export default function Admin() {
  const [tabValue, setTabValue] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const queryClient = useQueryClient();

  const showNotification = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Config Status Query
  const { 
    data: statusData, 
    isLoading: statusLoading,
    refetch: refetchStatus
  } = useQuery(
    'configStatus',
    () => adminApi.getConfigStatus(),
    { refetchInterval: 30000 }
  );

  // Reload Config Mutation
  const reloadConfigMutation = useMutation(
    () => adminApi.reloadConfig(),
    {
      onSuccess: () => {
        showNotification('Configuration reloaded successfully');
        queryClient.invalidateQueries('configStatus');
        queryClient.invalidateQueries('tickers');
        queryClient.invalidateQueries('apiKeys');
      },
      onError: (error) => {
        showNotification(
          error.response?.data?.detail || 'Failed to reload configuration',
          'error'
        );
      }
    }
  );

  // Tickers Query
  const {
    data: tickersData,
    isLoading: tickersLoading,
    refetch: refetchTickers
  } = useQuery(
    'tickers',
    () => adminApi.getTickers(true),
    { enabled: tabValue === 0 }
  );

  // API Keys Query
  const {
    data: apiKeysData,
    isLoading: apiKeysLoading,
    refetch: refetchApiKeys
  } = useQuery(
    'apiKeys',
    () => adminApi.getAPIKeys(true),
    { enabled: tabValue === 1 }
  );

  // Ticker Mutations
  const createTickerMutation = useMutation(
    (data) => adminApi.createTicker(data),
    {
      onSuccess: () => {
        showNotification('Ticker created successfully');
        queryClient.invalidateQueries('tickers');
        queryClient.invalidateQueries('configStatus');
      },
      onError: (error) => {
        showNotification(
          error.response?.data?.detail || 'Failed to create ticker',
          'error'
        );
      }
    }
  );

  const updateTickerMutation = useMutation(
    ({ symbol, data }) => adminApi.updateTicker(symbol, data),
    {
      onSuccess: () => {
        showNotification('Ticker updated successfully');
        queryClient.invalidateQueries('tickers');
        queryClient.invalidateQueries('configStatus');
      },
      onError: (error) => {
        showNotification(
          error.response?.data?.detail || 'Failed to update ticker',
          'error'
        );
      }
    }
  );

  const deleteTickerMutation = useMutation(
    (symbol) => adminApi.deleteTicker(symbol),
    {
      onSuccess: () => {
        showNotification('Ticker deleted successfully');
        queryClient.invalidateQueries('tickers');
        queryClient.invalidateQueries('configStatus');
      },
      onError: (error) => {
        showNotification(
          error.response?.data?.detail || 'Failed to delete ticker',
          'error'
        );
      }
    }
  );

  // API Key Mutations
  const createApiKeyMutation = useMutation(
    (data) => adminApi.createAPIKey(data),
    {
      onSuccess: () => {
        showNotification('API key created successfully');
        queryClient.invalidateQueries('apiKeys');
        queryClient.invalidateQueries('configStatus');
      },
      onError: (error) => {
        showNotification(
          error.response?.data?.detail || 'Failed to create API key',
          'error'
        );
      }
    }
  );

  const updateApiKeyMutation = useMutation(
    ({ serviceName, data }) => adminApi.updateAPIKey(serviceName, data),
    {
      onSuccess: () => {
        showNotification('API key updated successfully');
        queryClient.invalidateQueries('apiKeys');
        queryClient.invalidateQueries('configStatus');
      },
      onError: (error) => {
        showNotification(
          error.response?.data?.detail || 'Failed to update API key',
          'error'
        );
      }
    }
  );

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Admin Panel
      </Typography>

      <ConfigStatus
        status={statusData?.data}
        isLoading={statusLoading}
        onReload={() => reloadConfigMutation.mutate()}
        isReloading={reloadConfigMutation.isLoading}
      />

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="admin tabs">
          <Tab label="Tickers" id="admin-tab-0" aria-controls="admin-tabpanel-0" />
          <Tab label="API Keys" id="admin-tab-1" aria-controls="admin-tabpanel-1" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <TickerManagement
          tickers={tickersData?.data?.tickers}
          isLoading={tickersLoading}
          onRefresh={() => {
            refetchTickers();
            refetchStatus();
          }}
          onCreate={(data) => createTickerMutation.mutateAsync(data)}
          onUpdate={(symbol, data) => updateTickerMutation.mutateAsync({ symbol, data })}
          onDelete={(symbol) => deleteTickerMutation.mutateAsync(symbol)}
          isCreating={createTickerMutation.isLoading}
          isUpdating={updateTickerMutation.isLoading}
          isDeleting={deleteTickerMutation.isLoading}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <APIKeyManagement
          apiKeys={apiKeysData?.data?.api_keys}
          isLoading={apiKeysLoading}
          onRefresh={() => {
            refetchApiKeys();
            refetchStatus();
          }}
          onCreate={(data) => createApiKeyMutation.mutateAsync(data)}
          onUpdate={(serviceName, data) => updateApiKeyMutation.mutateAsync({ serviceName, data })}
          isCreating={createApiKeyMutation.isLoading}
          isUpdating={updateApiKeyMutation.isLoading}
        />
      </TabPanel>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
