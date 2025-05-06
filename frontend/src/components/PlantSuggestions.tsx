import React from 'react';
import { Box, Paper, Typography, Card, CardMedia, CardContent, IconButton } from '@mui/material';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';

interface PlantSuggestionsProps {
  selectedSection: string | null;
}

export const PlantSuggestions: React.FC<PlantSuggestionsProps> = ({ selectedSection }) => {
  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Suggestions</Typography>
        <Box>
          <IconButton>
            <NavigateBeforeIcon />
          </IconButton>
          <IconButton>
            <NavigateNextIcon />
          </IconButton>
        </Box>
      </Box>

      <Box sx={{ 
        display: 'flex',
        gap: 2,
        overflowX: 'auto',
        pb: 1
      }}>
        {/* Placeholder suggestion cards */}
        {[1, 2, 3].map((i) => (
          <Card key={i} sx={{ minWidth: 200 }}>
            <CardMedia
              component="div"
              sx={{ height: 140, bgcolor: 'grey.300' }}
            />
            <CardContent>
              <Typography variant="body2">Suggested Plant {i}</Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Paper>
  );
}; 