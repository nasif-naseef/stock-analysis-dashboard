import React, { useState, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box, AppBar, Toolbar, Typography, Drawer, List, ListItemButton,
  ListItemIcon, ListItemText, IconButton, Container, Divider
} from '@mui/material';
import {
  Menu as MenuIcon, Dashboard as DashboardIcon,
  TrendingUp, Newspaper, Analytics, AccountBalance,
  People, ShowChart, Compare, AdminPanelSettings
} from '@mui/icons-material';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Analyst Ratings', icon: <TrendingUp />, path: '/analyst-ratings' },
  { text: 'News Sentiment', icon: <Newspaper />, path: '/news-sentiment' },
  { text: 'Quantamental', icon: <Analytics />, path: '/quantamental' },
  { text: 'Hedge Fund', icon: <AccountBalance />, path: '/hedge-fund' },
  { text: 'Crowd Wisdom', icon: <People />, path: '/crowd' },
  { text: 'Technical', icon: <ShowChart />, path: '/technical' },
  { text: 'Comparison', icon: <Compare />, path: '/comparison' },
  { text: 'Admin', icon: <AdminPanelSettings />, path: '/admin' },
];

export default function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => setMobileOpen(!mobileOpen);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event, path, index) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      navigate(path);
      setMobileOpen(false);
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      const nextIndex = (index + 1) % menuItems.length;
      const nextElement = document.querySelector(`[data-menu-index="${nextIndex}"]`);
      nextElement?.focus();
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      const prevIndex = (index - 1 + menuItems.length) % menuItems.length;
      const prevElement = document.querySelector(`[data-menu-index="${prevIndex}"]`);
      prevElement?.focus();
    } else if (event.key === 'Home') {
      event.preventDefault();
      const firstElement = document.querySelector('[data-menu-index="0"]');
      firstElement?.focus();
    } else if (event.key === 'End') {
      event.preventDefault();
      const lastElement = document.querySelector(`[data-menu-index="${menuItems.length - 1}"]`);
      lastElement?.focus();
    }
  }, [navigate]);

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">Stock Analysis</Typography>
      </Toolbar>
      <Divider />
      <List 
        role="navigation" 
        aria-label="Main navigation"
        component="nav"
      >
        {menuItems.map((item, index) => {
          const isSelected = location.pathname === item.path;
          return (
            <ListItemButton 
              key={item.text} 
              onClick={() => {
                navigate(item.path);
                setMobileOpen(false);
              }}
              onKeyDown={(e) => handleKeyDown(e, item.path, index)}
              selected={isSelected}
              data-menu-index={index}
              tabIndex={0}
              role="menuitem"
              aria-current={isSelected ? 'page' : undefined}
              aria-label={`Navigate to ${item.text}`}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'primary.light',
                  '&:hover': {
                    backgroundColor: 'primary.light',
                  },
                },
                '&:focus': {
                  backgroundColor: 'action.focus',
                  outline: '2px solid',
                  outlineColor: 'primary.main',
                  outlineOffset: '-2px',
                },
              }}
            >
              <ListItemIcon 
                sx={{ color: isSelected ? 'primary.main' : 'inherit' }}
                aria-hidden="true"
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          );
        })}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton 
            color="inherit" 
            edge="start" 
            onClick={handleDrawerToggle} 
            sx={{ mr: 2, display: { sm: 'none' } }}
            aria-label="Open navigation menu"
            aria-expanded={mobileOpen}
            aria-controls="mobile-nav-drawer"
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="h1">
            Stock Analysis Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Box 
        component="nav" 
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="Navigation drawer"
      >
        <Drawer 
          id="mobile-nav-drawer"
          variant="temporary" 
          open={mobileOpen} 
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }} 
          sx={{ 
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer 
          variant="permanent" 
          sx={{ 
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }} 
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1, 
          p: 3, 
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          backgroundColor: '#f5f5f5'
        }}
        role="main"
        aria-label="Main content"
      >
        <Toolbar />
        <Container maxWidth="xl">{children}</Container>
      </Box>
    </Box>
  );
}
