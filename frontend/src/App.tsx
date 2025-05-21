import React from 'react';
import { ThemeProvider, CssBaseline, Paper, Box } from '@mui/material';
import theme from './theme';
import Header from './components/Header';
import { Garden } from './components/Garden/Garden';
import { AuthProvider } from './contexts/AuthContext';
import { GardenProvider } from './contexts/GardenContext';

// Default user ID for the supervisor
const DEFAULT_USER_ID = 1;

const App = () => (
  <ThemeProvider theme={theme}>
    <CssBaseline />
    <Header />
    <Box
      sx={{
        height: '100vh',
        width: '100vw',
        bgcolor: 'background.default',
        background: 'linear-gradient(120deg, #f8f9fa 0%, #e8f5e9 100%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'stretch',
        py: 0,
        px: 0,
        overflow: 'hidden',
        margin: 0,
        boxSizing: 'border-box',
      }}
    >
      <Paper
        elevation={0}
        sx={{
          width: '100%',
          height: 'calc(100vh - 64px)', // 64px header
          minHeight: 0,
          p: 0,
          borderRadius: 0,
          boxShadow: '0 4px 32px rgba(56, 142, 60, 0.10)',
          display: 'flex',
          flexDirection: 'column',
          gap: 0,
          bgcolor: 'background.paper',
          flex: 1,
          overflow: 'hidden',
          margin: 0,
          boxSizing: 'border-box',
        }}
      >
        <AuthProvider>
          <GardenProvider>
            <Box sx={{ flex: 1, width: '100%', minHeight: 0, height: '100%', overflow: 'hidden', p: 0, m: 0, boxSizing: 'border-box' }}>
              <Garden userId={DEFAULT_USER_ID} />
            </Box>
          </GardenProvider>
        </AuthProvider>
      </Paper>
    </Box>
  </ThemeProvider>
);

export default App; 