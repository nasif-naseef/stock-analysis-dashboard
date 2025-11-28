import React, { useState } from 'react';
import { Box, Paper, Tabs, Tab, Typography, Snackbar, Alert } from '@mui/material';
import TickerManagement from '../components/admin/TickerManagement';
import APIKeyManagement from '../components/admin/APIKeyManagement';
import ConfigStatus from '../components/admin/ConfigStatus';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `admin-tab-${index}`,
    'aria-controls': `admin-tabpanel-${index}`,
  };
}

export default function Admin() {
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleNotify = (message, severity = 'success') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const handleSnackbarClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Admin Panel
      </Typography>

      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange} 
            aria-label="admin panel tabs"
          >
            <Tab label="Tickers" {...a11yProps(0)} />
            <Tab label="API Keys" {...a11yProps(1)} />
            <Tab label="Status" {...a11yProps(2)} />
          </Tabs>
        </Box>
        <TabPanel value={activeTab} index={0}>
          <TickerManagement onNotify={handleNotify} />
        </TabPanel>
        <TabPanel value={activeTab} index={1}>
          <APIKeyManagement onNotify={handleNotify} />
        </TabPanel>
        <TabPanel value={activeTab} index={2}>
          <ConfigStatus onNotify={handleNotify} />
        </TabPanel>
      </Paper>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
