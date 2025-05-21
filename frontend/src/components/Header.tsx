import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';

export const GrowlyticsLogo = () => (
  <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
    <svg width="36" height="36" viewBox="0 0 40 40" fill="none">
      <circle cx="20" cy="20" r="18" fill="#a5d6a7" />
      <path d="M20 30c-5-3-8-7-8-12a8 8 0 1 1 16 0c0 5-3 9-8 12z" fill="#388e3c" />
      <path d="M20 22v-8" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
      <ellipse cx="20" cy="14" rx="2" ry="3" fill="#fff" />
    </svg>
  </Box>
);

const Header: React.FC = () => (
  <AppBar position="static" color="primary" elevation={0} sx={{ zIndex: 1201 }}>
    <Toolbar sx={{ minHeight: 64, display: 'flex', alignItems: 'center', px: { xs: 2, sm: 4 } }}>
      <GrowlyticsLogo />
      <Typography variant="h5" sx={{ fontWeight: 700, letterSpacing: 1, color: 'white', mr: 2 }}>
        Growlytics
      </Typography>
      <Typography
        variant="subtitle1"
        sx={{
          color: 'rgba(255,255,255,0.85)',
          fontWeight: 400,
          fontSize: '1.1rem',
          letterSpacing: 0.2,
          ml: 0,
          pr: 2,
          borderLeft: '1.5px solid rgba(255,255,255,0.25)',
          pl: 2,
        }}
      >
        Smart Plant Management & Analytics
      </Typography>
      {/* Add user/account info or nav here if needed */}
    </Toolbar>
  </AppBar>
);

export default Header; 