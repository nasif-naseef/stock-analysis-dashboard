import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import AnalystRatings from './pages/AnalystRatings';
import NewsSentiment from './pages/NewsSentiment';
import Quantamental from './pages/Quantamental';
import HedgeFund from './pages/HedgeFund';
import Crowd from './pages/Crowd';
import Technical from './pages/Technical';
import Comparison from './pages/Comparison';
import Admin from './pages/Admin';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    success: { main: '#2e7d32' },
    error: { main: '#d32f2f' },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analyst-ratings" element={<AnalystRatings />} />
              <Route path="/news-sentiment" element={<NewsSentiment />} />
              <Route path="/quantamental" element={<Quantamental />} />
              <Route path="/hedge-fund" element={<HedgeFund />} />
              <Route path="/crowd" element={<Crowd />} />
              <Route path="/technical" element={<Technical />} />
              <Route path="/comparison" element={<Comparison />} />
              <Route path="/admin" element={<Admin />} />
            </Routes>
          </Layout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
