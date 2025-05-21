import React from 'react';
import { Tabs, Tab, Box } from '@mui/material';

interface PlantGuidesTabsProps {
  value: number;
  onChange: (event: React.SyntheticEvent, newValue: number) => void;
}

const PlantGuidesTabs: React.FC<PlantGuidesTabsProps> = ({ value, onChange }) => {
  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
      <Tabs value={value} onChange={onChange}>
        <Tab label="Care Guide" />
        <Tab label="Plant Info" />
        <Tab label="Growing Tips" />
      </Tabs>
    </Box>
  );
};

export default PlantGuidesTabs; 