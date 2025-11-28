import React from 'react';
import {
  Card, CardContent, Typography, Box, Chip, List, ListItem, ListItemText, Divider
} from '@mui/material';
import { Event, TrendingUp, TrendingDown } from '@mui/icons-material';

/**
 * ChartEventsCard - Display technical chart events and patterns
 * 
 * @param {Object} data - Chart events data
 * @param {string} data.ticker - Stock ticker symbol
 * @param {Array} data.events - Array of chart events
 */
export default function ChartEventsCard({ data }) {
  if (!data || data.error) {
    return (
      <Card>
        <CardContent>
          <Typography color="textSecondary">
            {data?.error || 'No chart events data available'}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const events = data.events || [];

  const getEventColor = (eventType) => {
    const type = (eventType || '').toLowerCase();
    if (type.includes('bullish') || type.includes('breakout') || type.includes('support')) {
      return 'success';
    }
    if (type.includes('bearish') || type.includes('breakdown') || type.includes('resistance')) {
      return 'error';
    }
    return 'default';
  };

  const formatPrice = (price) => {
    if (price === null || price === undefined) return 'N/A';
    return `$${Number(price).toFixed(2)}`;
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            Chart Events
          </Typography>
          <Chip 
            label={`${events.length} Events`}
            size="small"
            color={events.length > 0 ? 'primary' : 'default'}
          />
        </Box>

        <Typography variant="body2" color="textSecondary" gutterBottom>
          {data.ticker}
        </Typography>

        {events.length === 0 ? (
          <Box textAlign="center" py={3}>
            <Event color="disabled" sx={{ fontSize: 48, mb: 1 }} />
            <Typography color="textSecondary">
              No active chart events
            </Typography>
          </Box>
        ) : (
          <List disablePadding>
            {events.slice(0, 5).map((event, index) => (
              <React.Fragment key={event.event_id || index}>
                <ListItem 
                  sx={{ 
                    px: 0,
                    flexDirection: 'column',
                    alignItems: 'flex-start'
                  }}
                >
                  <Box display="flex" justifyContent="space-between" width="100%" mb={0.5}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Chip 
                        label={event.event_type || 'Unknown'}
                        size="small"
                        color={getEventColor(event.event_type)}
                        variant="outlined"
                      />
                      {event.is_active && (
                        <Chip label="Active" size="small" color="success" />
                      )}
                    </Box>
                    <Typography variant="caption" color="textSecondary">
                      {event.price_period || 'Daily'}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" fontWeight="medium">
                    {event.event_name || 'Chart Pattern'}
                  </Typography>
                  
                  <Box display="flex" gap={2} mt={0.5}>
                    {event.target_price && (
                      <Typography variant="caption" color="primary">
                        Target: {formatPrice(event.target_price)}
                      </Typography>
                    )}
                    {event.start_date && (
                      <Typography variant="caption" color="textSecondary">
                        From: {event.start_date}
                      </Typography>
                    )}
                  </Box>
                </ListItem>
                {index < events.length - 1 && index < 4 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        )}

        {events.length > 5 && (
          <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
            +{events.length - 5} more events
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
