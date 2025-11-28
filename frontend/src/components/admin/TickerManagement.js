import React, { useState } from 'react';
import {
  Paper, Typography, Box, Button, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, IconButton, Chip, Switch,
  Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions,
  CircularProgress, Tooltip
} from '@mui/material';
import {
  Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import TickerForm from './TickerForm';

export default function TickerManagement({
  tickers,
  isLoading,
  onRefresh,
  onCreate,
  onUpdate,
  onDelete,
  isCreating,
  isUpdating,
  isDeleting
}) {
  const [formOpen, setFormOpen] = useState(false);
  const [editTicker, setEditTicker] = useState(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [tickerToDelete, setTickerToDelete] = useState(null);
  
  const handleAdd = () => {
    setEditTicker(null);
    setFormOpen(true);
  };
  
  const handleEdit = (ticker) => {
    setEditTicker(ticker);
    setFormOpen(true);
  };
  
  const handleFormSubmit = async (data) => {
    if (editTicker) {
      await onUpdate(editTicker.ticker, data);
    } else {
      await onCreate(data);
    }
    setFormOpen(false);
    setEditTicker(null);
  };
  
  const handleDeleteClick = (ticker) => {
    setTickerToDelete(ticker);
    setDeleteConfirmOpen(true);
  };
  
  const handleDeleteConfirm = async () => {
    if (tickerToDelete) {
      await onDelete(tickerToDelete.ticker);
    }
    setDeleteConfirmOpen(false);
    setTickerToDelete(null);
  };
  
  const handleToggleActive = async (ticker) => {
    await onUpdate(ticker.ticker, { is_active: !ticker.is_active });
  };
  
  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Ticker Management</Typography>
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
            Add Ticker
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
                <TableCell>Symbol</TableCell>
                <TableCell>Exchange</TableCell>
                <TableCell>TC V4 ID</TableCell>
                <TableCell>TC V3 ID</TableCell>
                <TableCell>Active</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tickers?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography color="textSecondary">No tickers configured</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                tickers?.map((ticker) => (
                  <TableRow key={ticker.ticker} hover>
                    <TableCell>
                      <Chip label={ticker.ticker} size="small" color="primary" />
                    </TableCell>
                    <TableCell>{ticker.exchange}</TableCell>
                    <TableCell>
                      {ticker.tr_v4_id || <Typography color="textSecondary" variant="body2">-</Typography>}
                    </TableCell>
                    <TableCell>
                      {ticker.tr_v3_id || <Typography color="textSecondary" variant="body2">-</Typography>}
                    </TableCell>
                    <TableCell>
                      <Switch
                        size="small"
                        checked={ticker.is_active}
                        onChange={() => handleToggleActive(ticker)}
                        disabled={isUpdating}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Edit">
                        <IconButton size="small" onClick={() => handleEdit(ticker)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteClick(ticker)}
                          color="error"
                        >
                          <DeleteIcon fontSize="small" />
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
      
      <TickerForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditTicker(null);
        }}
        onSubmit={handleFormSubmit}
        ticker={editTicker}
        isSubmitting={isCreating || isUpdating}
      />
      
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete ticker <strong>{tickerToDelete?.ticker}</strong>?
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleDeleteConfirm} 
            color="error" 
            variant="contained"
            disabled={isDeleting}
            startIcon={isDeleting ? <CircularProgress size={20} /> : null}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}
