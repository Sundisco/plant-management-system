import React from 'react';
import { Box, Typography, Paper, SxProps, Theme } from '@mui/material';
import { WateringSchedule as WateringScheduleType } from '../../types/Plant';

interface WateringScheduleProps {
  schedule: WateringScheduleType;
  onWater: (date: string) => void;
}

const WateringSchedule: React.FC<WateringScheduleProps> = ({ schedule, onWater }) => {
  const boxStyle: SxProps<Theme> = {
    position: 'relative',
    height: 24,
    borderRadius: 1.5,
    cursor: 'pointer',
    overflow: 'hidden',
    transition: 'all 0.2s ease',
    '&:hover': {
      opacity: 0.9,
      transform: 'scale(1.02)',
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        Watering Schedule
      </Typography>
      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        {Object.entries(schedule).map(([date, count]) => (
          <Box
            key={date}
            onClick={() => onWater(date)}
            sx={{
              ...boxStyle,
              bgcolor: count === 0 ? 'grey.100' : 'info.main',
            }}
          >
            <Typography
              variant="caption"
              sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                color: count === 0 ? 'text.secondary' : 'white',
                fontWeight: 'bold',
              }}
            >
              {count}
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
};

export default WateringSchedule; 