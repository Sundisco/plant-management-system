import React, { useState } from 'react';
import { 
  Paper, 
  InputBase, 
  IconButton, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemAvatar, 
  Avatar,
  Box,
  Popper,
  ClickAwayListener,
  Grow
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { Plant } from '../types/Plant';
import { API_ENDPOINTS } from '../config';

interface PlantSearchProps {
  onPlantAdded: (plant: Plant) => void;
}

export const PlantSearch: React.FC<PlantSearchProps> = ({ onPlantAdded }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<Plant[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleSearch = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!searchTerm.trim()) return;

    try {
      const response = await fetch(API_ENDPOINTS.PLANTS_SEARCH + `?query=${encodeURIComponent(searchTerm)}`);
      if (!response.ok) throw new Error('Search failed');
      
      const data = await response.json();
      setSearchResults(data.items || []);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    }
  };

  const handleAddPlant = async (plant: Plant) => {
    try {
      const userId = 1; // Replace with actual user ID
      const response = await fetch(API_ENDPOINTS.ADD_PLANT(userId, plant.id), {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to add plant');
      
      const addedPlant = await response.json();
      onPlantAdded(addedPlant);
      setSearchResults([]);
      setSearchTerm('');
      setAnchorEl(null);
    } catch (error) {
      console.error('Error adding plant:', error);
    }
  };

  const handleSearchClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget.closest('form') || null);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setSearchResults([]);
    setSearchTerm('');
  };

  const open = Boolean(anchorEl) && searchResults.length > 0;

  return (
    <ClickAwayListener onClickAway={handleClose}>
      <Box sx={{ width: '100%', position: 'relative' }}>
        <Paper
          component="form"
          onSubmit={handleSearch}
          sx={{
            p: '2px 4px',
            display: 'flex',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <InputBase
            sx={{ ml: 1, flex: 1 }}
            placeholder="Search Plants"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <IconButton type="submit" sx={{ p: '10px' }} onClick={handleSearchClick}>
            <SearchIcon />
          </IconButton>
        </Paper>

        <Popper
          open={open}
          anchorEl={anchorEl}
          placement="bottom-start"
          transition
          style={{
            width: anchorEl?.clientWidth,
            zIndex: 1300
          }}
        >
          {({ TransitionProps }) => (
            <Grow {...TransitionProps}>
              <Paper 
                sx={{ 
                  mt: 1,
                  maxHeight: '400px',
                  overflow: 'auto',
                  boxShadow: 3
                }}
              >
                <List>
                  {searchResults.map((plant) => (
                    <ListItem
                      key={plant.id}
                      button
                      onClick={() => handleAddPlant(plant)}
                      sx={{
                        '&:hover': {
                          bgcolor: 'action.hover',
                        },
                      }}
                    >
                      <ListItemAvatar>
                        <Avatar
                          src={plant.image_url}
                          alt={plant.common_name}
                          variant="rounded"
                          sx={{ width: 50, height: 50 }}
                        >
                          🌿
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={plant.common_name}
                        secondary={plant.scientific_name?.[0]}
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grow>
          )}
        </Popper>
      </Box>
    </ClickAwayListener>
  );
}; 