import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box, Paper, Typography, Button, IconButton, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Switch,
  Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions,
  CircularProgress
} from '@mui/material';
import { Add, Edit, Delete } from '@mui/icons-material';
import adminApi from '../../api/adminApi';
import TickerForm from './TickerForm';
import LoadingSpinner from '../LoadingSpinner';
import ErrorMessage from '../ErrorMessage';

export default function TickerManagement({ onNotify }) {
  const queryClient = useQueryClient();
  const [formOpen, setFormOpen] = useState(false);
  const [selectedTicker, setSelectedTicker] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [tickerToDelete, setTickerToDelete] = useState(null);

  const { data: tickersData, isLoading, error, refetch } = useQuery({
    queryKey: ['tickers'],
    queryFn: () => adminApi.getTickers(true).then(res => res.data)
  });

  const deleteMutation = useMutation({
    mutationFn: (symbol) => adminApi.deleteTicker(symbol),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickers'] });
      onNotify('Ticker deleted successfully', 'success');
      setDeleteDialogOpen(false);
      setTickerToDelete(null);
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Failed to delete ticker';
      onNotify(message, 'error');
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ symbol, data }) => adminApi.updateTicker(symbol, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickers'] });
      onNotify('Ticker status updated successfully', 'success');
    },
    onError: (error) => {
      const message = error.response?.data?.detail || 'Failed to update ticker';
      onNotify(message, 'error');
    }
  });

  const handleAddClick = () => {
    setSelectedTicker(null);
    setFormOpen(true);
  };

  const handleEditClick = (ticker) => {
    setSelectedTicker(ticker);
    setFormOpen(true);
  };

  const handleDeleteClick = (ticker) => {
    setTickerToDelete(ticker);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (tickerToDelete) {
      deleteMutation.mutate(tickerToDelete.symbol);
    }
  };

  const handleToggleActive = (ticker) => {
    updateMutation.mutate({
      symbol: ticker.symbol,
      data: { ...ticker, active: !ticker.active }
    });
  };

  const handleFormSuccess = (message) => {
    onNotify(message, 'success');
  };

  if (isLoading) return <LoadingSpinner message="Loading tickers..." />;
  if (error) return <ErrorMessage message="Failed to load tickers" onRetry={refetch} />;

  const tickers = tickersData?.tickers || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Ticker Management</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAddClick}
        >
          Add Ticker
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Exchange</TableCell>
              <TableCell>TR V4 ID</TableCell>
              <TableCell>TR V3 ID</TableCell>
              <TableCell>Active</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tickers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography color="textSecondary">No tickers configured</Typography>
                </TableCell>
              </TableRow>
            ) : (
              tickers.map((ticker) => (
                <TableRow key={ticker.symbol}>
                  <TableCell>
                    <Typography fontWeight="bold">{ticker.symbol}</Typography>
                  </TableCell>
                  <TableCell>{ticker.exchange || 'N/A'}</TableCell>
                  <TableCell>{ticker.tr_v4_id || 'N/A'}</TableCell>
                  <TableCell>{ticker.tr_v3_id || 'N/A'}</TableCell>
                  <TableCell>
                    <Switch
                      checked={ticker.active}
                      onChange={() => handleToggleActive(ticker)}
                      disabled={updateMutation.isPending}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleEditClick(ticker)}
                      title="Edit ticker"
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteClick(ticker)}
                      color="error"
                      title="Delete ticker"
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <TickerForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={handleFormSuccess}
        ticker={selectedTicker}
      />

      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the ticker "{tickerToDelete?.symbol}"?
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={deleteMutation.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            disabled={deleteMutation.isPending}
            startIcon={deleteMutation.isPending ? <CircularProgress size={20} /> : null}
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
