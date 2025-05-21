import React, { useState, useEffect, useRef } from 'react';
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
  Grow,
  Alert,
  Snackbar,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AddIcon from '@mui/icons-material/Add';
import { Plant } from '../types/Plant';
import { API_ENDPOINTS, API_TIMEOUTS } from '../config';
import { api } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';
import { PlantDetails } from './Garden/PlantDetails';

interface PlantSearchProps {
  onPlantAdded: (plant: Plant) => void;
  gardenPlants?: Plant[];
}

export const PlantSearch: React.FC<PlantSearchProps> = ({ onPlantAdded, gardenPlants = [] }) => {
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<Plant[]>([]);
  const [userPlants, setUserPlants] = useState<Plant[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const popperContentRef = useRef<HTMLDivElement>(null);

  // Fetch user's plants on component mount
  const fetchUserPlants = async () => {
    if (!user?.id) return;
    try {
      const { data, error } = await api.get<Plant[]>(
        `${API_ENDPOINTS.USER_PLANTS(user.id)}?limit=50`
      );
      if (error) {
        console.error('Error fetching user plants:', error);
        return;
      }
      setUserPlants(data || []);
    } catch (error) {
      console.error('Error fetching user plants:', error);
    }
  };

  useEffect(() => {
    fetchUserPlants();
  }, [user?.id]);

  const handleSearch = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!searchTerm.trim()) return;
    try {
      const { data, error } = await api.get<{ items: Plant[] }>(
        `${API_ENDPOINTS.PLANTS_SEARCH}?query=${encodeURIComponent(searchTerm)}`,
        API_TIMEOUTS.SEARCH
      );
      if (error) {
        setError(error);
        setSearchResults([]);
        return;
      }
      setSearchResults(data?.items || []);
      setError(null);
    } catch (error) {
      console.error('Search error:', error);
      setError('An unexpected error occurred');
      setSearchResults([]);
    }
  };

  const handleAddPlant = async (plant: Plant) => {
    if (!user?.id) {
      setError('User not authenticated');
      return;
    }
    try {
      const { data, error } = await api.post<Plant>(
        `${API_ENDPOINTS.ADD_PLANT(user.id)}/${plant.id}`,
        {}  // Empty body since plant_id is in URL
      );
      if (error) {
        if (error.includes('already in garden')) {
          setSuccess('Plant is already in your garden!');
        } else {
          setError(error);
        }
        return;
      }
      if (data) {
        onPlantAdded(data);
        await fetchUserPlants();
        setError(null);
        setSuccess('Plant added to your garden!');
      }
    } catch (error) {
      console.error('Error adding plant:', error);
      setError('Failed to add plant to your garden');
    }
  };

  const isPlantInGarden = (plantId: number) => {
    return userPlants.some(p => p.id === plantId);
  };

  const handleSearchClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget.closest('form') || null);
  };

  // Modify click away handler to be less aggressive
  const handleClickAway = (event: MouseEvent | TouchEvent) => {
    // Don't close if clicking inside the search input or results
    if (
      (searchInputRef.current &&
        (searchInputRef.current === event.target || searchInputRef.current.contains(event.target as Node))) ||
      (popperContentRef.current &&
        (popperContentRef.current === event.target || popperContentRef.current.contains(event.target as Node)))
    ) {
      return;
    }
    // Only close if clicking outside both the input and results
    setAnchorEl(null);
    // Don't clear search results and term
    // setSearchResults([]);
    // setSearchTerm('');
    setError(null);
    setSuccess(null);
  };

  const open = Boolean(anchorEl) && searchResults.length > 0;

  // Fetch full plant details before opening dialog
  const handleOpenDetails = async (plant: Plant) => {
    setLoadingDetails(true);
    try {
      const { data, error } = await api.get<Plant>(`${API_ENDPOINTS.PLANTS}/${plant.id}`);
      console.log('Plant details fetch:', { data, error });
      if (error) {
        setError('Failed to fetch plant details');
        setLoadingDetails(false);
        return;
      }
      setSelectedPlant(data || plant);
      setDetailsOpen(true);
    } catch (err) {
      setError('Failed to fetch plant details');
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleCloseDetails = () => {
    setSelectedPlant(null);
    setDetailsOpen(false);
  };

  return (
    <ClickAwayListener onClickAway={handleClickAway}>
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
            inputRef={searchInputRef}
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
                ref={popperContentRef}
                sx={{ 
                  mt: 1,
                  maxHeight: '400px',
                  overflow: 'auto',
                  boxShadow: 3
                }}
              >
                <List>
                  {searchResults.map((plant) => {
                    const inGarden = isPlantInGarden(plant.id);
                    return (
                      <ListItem
                        key={plant.id}
                        secondaryAction={
                          inGarden ? (
                            <Chip
                              icon={<CheckCircleIcon sx={{ color: 'white' }}/>} 
                              label="In Garden"
                              color="success"
                              size="small"
                              sx={{ fontWeight: 'bold', color: 'white' }}
                            />
                          ) : (
                            <IconButton edge="end" color="primary" onClick={e => { e.stopPropagation(); handleAddPlant(plant); }}>
                              <AddIcon />
                            </IconButton>
                          )
                        }
                        sx={{
                          '&:hover': { bgcolor: 'action.hover' },
                          opacity: inGarden ? 0.7 : 1,
                          cursor: 'pointer'
                        }}
                        onClick={() => handleOpenDetails(plant)}
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
                    );
                  })}
                </List>
                {loadingDetails && (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 2 }}>
                    <CircularProgress size={28} />
                  </Box>
                )}
              </Paper>
            </Grow>
          )}
        </Popper>

        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </Snackbar>

        <Snackbar
          open={!!success}
          autoHideDuration={3000}
          onClose={() => setSuccess(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert onClose={() => setSuccess(null)} severity="success" sx={{ width: '100%' }}>
            {success}
          </Alert>
        </Snackbar>

        <PlantDetails
          plant={selectedPlant}
          open={detailsOpen}
          onClose={handleCloseDetails}
          sections={[]}
        />
      </Box>
    </ClickAwayListener>
  );
}; 