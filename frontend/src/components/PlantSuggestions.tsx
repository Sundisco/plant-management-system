import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Card, 
  CardMedia, 
  CardContent, 
  IconButton, 
  List, 
  ListItem, 
  ListItemText,
  Chip,
  Avatar,
  ListItemIcon,
  Grid,
  TextField,
  Autocomplete,
  Button,
  CircularProgress,
  FormControlLabel,
  Switch
} from '@mui/material';
import { useGarden } from '../contexts/GardenContext';
import { Plant } from '../types/Plant';
import { API_ENDPOINTS } from '../config/api';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';
import Pagination from '@mui/material/Pagination';
import Stack from '@mui/material/Stack';
import Drawer from '@mui/material/Drawer';
import CloseIcon from '@mui/icons-material/Close';
import Badge from '@mui/material/Badge';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { PlantDetails } from './Garden/PlantDetails';

interface PlantSuggestionsProps {
  selectedSection: string | null;
  isFilterOpen: boolean;
  setIsFilterOpen: (val: boolean) => void;
  activeFilterCount: number;
}

interface InspirationFilter {
  attracts?: string[];
  type?: string;
  growthRate?: string;
  maintenance?: string;
  cycle?: string;
  watering?: string;
  is_evergreen?: boolean;
  edible_fruit?: boolean;
  sunlight?: string[];
}

const GROWTH_RATES = ['Low', 'Moderate', 'High'] as const;
const MAINTENANCE_LEVELS = ['Low', 'Moderate', 'High'] as const;
const SUNLIGHT_CONDITIONS = ['full sun', 'part shade', 'filtered shade', 'shade'] as const;
const WATERING_LEVELS = ['Minimum', 'Average', 'Frequent'] as const;
const LIFE_CYCLES = ['Perennial', 'Annual'] as const;
const PLANT_TYPES = [
  'tree',
  'shrub',
  'herbaceous plant',
  'perennial',
  'grass & grass-like plants',
  'vine & climber',
  'succulent & cactus',
  'fern',
  'aquatic & wetland plant',
  'palm & cycad'
] as const;
const ATTRACTS_OPTIONS = ['Butterflies', 'Birds', 'Squirrels', 'Bees'] as const;

export const PlantSuggestions: React.FC<PlantSuggestionsProps> = ({ selectedSection, isFilterOpen, setIsFilterOpen, activeFilterCount }) => {
  const [inspirationPlants, setInspirationPlants] = useState<Plant[]>([]);
  const [filter, setFilter] = useState<InspirationFilter>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableFilters, setAvailableFilters] = useState({
    attracts: ATTRACTS_OPTIONS,
    types: PLANT_TYPES,
    growthRates: GROWTH_RATES,
    maintenance: MAINTENANCE_LEVELS,
    cycles: LIFE_CYCLES,
    watering: WATERING_LEVELS,
    sunlight: SUNLIGHT_CONDITIONS
  });
  const [page, setPage] = useState(1);
  const RESULTS_PER_PAGE = 3;
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  const handleSearch = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching inspiration plants with filters:', filter);
      
      const response = await fetch(`${API_ENDPOINTS.PLANTS}/filtered`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(filter)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Response:', data);
      
      if (!data) {
        setInspirationPlants([]);
        return;
      }
      
      setInspirationPlants(data);
    } catch (error) {
      console.error('Error fetching inspiration plants:', error);
      setError('Failed to load plant suggestions');
      setInspirationPlants([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field: keyof InspirationFilter, value: any) => {
    if (field === 'is_evergreen' || field === 'edible_fruit') {
      // If the value is false, remove the filter entirely
      if (!value) {
        setFilter(prev => {
          const newFilter = { ...prev };
          delete newFilter[field];
          return newFilter;
        });
      } else {
        // If the value is true, set the filter
        setFilter(prev => ({ ...prev, [field]: true }));
      }
    } else {
      setFilter(prev => ({ ...prev, [field]: value }));
    }
  };

  const handleClearFilters = () => {
    setFilter({});
    setInspirationPlants([]);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  // Calculate pagination
  const totalPages = Math.ceil(inspirationPlants.length / RESULTS_PER_PAGE);
  const startIndex = (page - 1) * RESULTS_PER_PAGE;
  const displayedPlants = inspirationPlants.slice(startIndex, startIndex + RESULTS_PER_PAGE);

  const handlePrevPage = () => {
    setPage(prev => Math.max(1, prev - 1));
  };

  const handleNextPage = () => {
    setPage(prev => Math.min(totalPages, prev + 1));
  };

  const getActiveFilterChips = () => {
    const chips: JSX.Element[] = [];
    
    Object.entries(filter).forEach(([key, value]) => {
      if (Array.isArray(value) && value.length > 0) {
        value.forEach(v => {
          chips.push(
            <Chip
              key={`${key}-${v}`}
              label={`${key}: ${v}`}
              size="small"
              onDelete={() => {
                const newValue = value.filter(item => item !== v);
                handleFilterChange(key as keyof InspirationFilter, newValue.length ? newValue : null);
              }}
              sx={{ mr: 0.5, mb: 0.5 }}
            />
          );
        });
      } else if (value !== null && value !== undefined) {
        chips.push(
          <Chip
            key={key}
            label={`${key}: ${value}`}
            size="small"
            onDelete={() => handleFilterChange(key as keyof InspirationFilter, null)}
            sx={{ mr: 0.5, mb: 0.5 }}
          />
        );
      }
    });
    
    return chips;
  };

  const handlePlantClick = (plant: Plant) => {
    setSelectedPlant(plant);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setSelectedPlant(null);
    setDetailsOpen(false);
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      height: '100%',
      overflow: 'hidden',
      minHeight: 0,
      mb: 0
    }}>
      <Paper elevation={2} sx={{ 
        p: 2,
        flex: 1,
        minHeight: 0,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        mb: 0
      }}>
        {/* Header and Filters Section removed; now handled by parent */}

        {/* Content Section */}
        <Box sx={{
          flex: 1,
          minHeight: 0,
          display: 'flex',
          flexDirection: 'column',
          mb: 0
        }}>
          {/* Active Filters */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {getActiveFilterChips()}
            </Box>
          </Box>

          {error && (
            <Typography color="error" sx={{ mt: 1, textAlign: 'center' }}>
              {error}
            </Typography>
          )}

          {loading ? (
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              minHeight: '300px',
              flexDirection: 'column',
              gap: 2
            }}>
              <CircularProgress size={40} thickness={4} />
              <Typography color="textSecondary" variant="subtitle1">
                Finding the perfect plants for you...
              </Typography>
            </Box>
          ) : (
            <>
              {/* Results Section */}
              {inspirationPlants.length === 0 ? (
                <Box sx={{ 
                  textAlign: 'center', 
                  py: 4,
                  px: 2,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 2
                }}>
                  <Typography color="textSecondary" variant="h6" sx={{ fontWeight: 500 }}>
                    {Object.keys(filter).length > 0 
                      ? "No plants found matching your criteria"
                      : "Start exploring plants"}
                  </Typography>
                  <Typography color="textSecondary" variant="body1">
                    {Object.keys(filter).length > 0 
                      ? "Try adjusting your filters to find more plants"
                      : "Use the filters above to discover plants that match your preferences"}
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ position: 'relative', flex: 1, minHeight: 0, display: 'flex', flexDirection: 'row', alignItems: 'stretch', mb: 0 }}>
                  {/* Navigation Arrows - outside scrollable grid, vertically centered */}
                  {totalPages > 1 && (
                    <IconButton
                      onClick={handlePrevPage}
                      disabled={page === 1}
                      sx={{
                        position: 'relative',
                        alignSelf: 'center',
                        mr: 1,
                        zIndex: 2,
                        bgcolor: 'background.paper',
                        boxShadow: 2,
                        '&:hover': { 
                          bgcolor: 'background.paper',
                          transform: 'scale(1.1)'
                        },
                        transition: 'all 0.2s ease',
                        width: 40,
                        height: 40
                      }}
                    >
                      <ChevronLeftIcon />
                    </IconButton>
                  )}
                  {/* Results Grid - no longer scrollable */}
                  <Grid container spacing={2} sx={{ 
                    flex: 1,
                    minHeight: 0,
                    px: 0,
                    mx: 0,
                    pb: 0
                  }}>
                    {displayedPlants.map((plant) => (
                      <Grid item xs={12} sm={6} md={4} key={plant.id} sx={{ display: 'flex', minHeight: 0 }}>
                        <Card 
                          elevation={1}
                          sx={{ 
                            width: '100%',
                            position: 'relative',
                            transition: 'all 0.3s ease',
                            '&:hover': {
                              transform: 'translateY(-4px)',
                              boxShadow: '0 12px 24px rgba(0,0,0,0.15)',
                              cursor: 'pointer',
                              '& .MuiCardMedia-root': {
                                transform: 'scale(1.05)'
                              }
                            },
                            borderRadius: '16px',
                            overflow: 'hidden',
                            flex: 1,
                            minHeight: 0,
                            bgcolor: 'background.paper',
                            border: '1px solid',
                            borderColor: 'divider'
                          }}
                          onClick={() => handlePlantClick(plant)}
                        >
                          {plant.image_url && (
                            <Box sx={{ position: 'relative' }}>
                              <CardMedia
                                component="img"
                                height="280"
                                image={plant.image_url}
                                alt={plant.common_name}
                                sx={{ 
                                  objectFit: 'cover',
                                  transition: 'transform 0.5s ease',
                                  width: '100%'
                                }}
                              />
                              {/* Subtle Gradient Overlay */}
                              <Box sx={{
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                right: 0,
                                bottom: 0,
                                background: 'linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.5))',
                                display: 'flex',
                                flexDirection: 'column',
                                justifyContent: 'flex-end',
                                p: 2
                              }}>
                                <Typography 
                                  variant="h6" 
                                  sx={{ 
                                    fontWeight: 600,
                                    color: 'white',
                                    fontSize: '1.1rem',
                                    lineHeight: 1.2,
                                    mb: 1,
                                    textShadow: '0 1px 2px rgba(0,0,0,0.2)'
                                  }}
                                >
                                  {plant.common_name}
                                </Typography>
                                <Box sx={{ 
                                  display: 'flex', 
                                  flexWrap: 'wrap', 
                                  gap: 0.75
                                }}>
                                  <Chip 
                                    label={plant.type} 
                                    size="small"
                                    sx={{ 
                                      bgcolor: 'rgba(76, 175, 80, 0.85)', 
                                      color: 'white',
                                      fontWeight: 500,
                                      fontSize: '0.75rem',
                                      height: '24px',
                                      backdropFilter: 'blur(4px)',
                                      '& .MuiChip-label': {
                                        px: 1
                                      }
                                    }}
                                  />
                                  {plant.is_evergreen && (
                                    <Chip 
                                      label="Evergreen" 
                                      size="small"
                                      sx={{ 
                                        bgcolor: 'rgba(25, 118, 210, 0.85)', 
                                        color: 'white',
                                        fontWeight: 500,
                                        fontSize: '0.75rem',
                                        height: '24px',
                                        backdropFilter: 'blur(4px)',
                                        '& .MuiChip-label': {
                                          px: 1
                                        }
                                      }}
                                    />
                                  )}
                                  {plant.edible_fruit && (
                                    <Chip 
                                      label="Edible Fruit" 
                                      size="small"
                                      sx={{ 
                                        bgcolor: 'rgba(211, 47, 47, 0.85)', 
                                        color: 'white',
                                        fontWeight: 500,
                                        fontSize: '0.75rem',
                                        height: '24px',
                                        backdropFilter: 'blur(4px)',
                                        '& .MuiChip-label': {
                                          px: 1
                                        }
                                      }}
                                    />
                                  )}
                                  {plant.cycle && (
                                    <Chip 
                                      label={plant.cycle} 
                                      size="small"
                                      sx={{ 
                                        bgcolor: 'rgba(156, 39, 176, 0.85)', 
                                        color: 'white',
                                        fontWeight: 500,
                                        fontSize: '0.75rem',
                                        height: '24px',
                                        backdropFilter: 'blur(4px)',
                                        '& .MuiChip-label': {
                                          px: 1
                                        }
                                      }}
                                    />
                                  )}
                                  {plant.attracts && plant.attracts.length > 0 && (
                                    <Chip
                                      label={plant.attracts[0]}
                                      size="small"
                                      sx={{ 
                                        bgcolor: 'rgba(237, 108, 2, 0.85)',
                                        color: 'white',
                                        fontWeight: 500,
                                        fontSize: '0.75rem',
                                        height: '24px',
                                        backdropFilter: 'blur(4px)',
                                        '& .MuiChip-label': {
                                          px: 1
                                        }
                                      }}
                                    />
                                  )}
                                </Box>
                              </Box>
                            </Box>
                          )}
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                  {/* Navigation Arrows - right side */}
                  {totalPages > 1 && (
                    <IconButton
                      onClick={handleNextPage}
                      disabled={page === totalPages}
                      sx={{
                        position: 'relative',
                        alignSelf: 'center',
                        ml: 1,
                        zIndex: 2,
                        bgcolor: 'background.paper',
                        boxShadow: 2,
                        '&:hover': { 
                          bgcolor: 'background.paper',
                          transform: 'scale(1.1)'
                        },
                        transition: 'all 0.2s ease',
                        width: 40,
                        height: 40
                      }}
                    >
                      <ChevronRightIcon />
                    </IconButton>
                  )}
                </Box>
              )}
            </>
          )}
        </Box>
      </Paper>

      {/* Filter Drawer */}
      <Drawer
        anchor="right"
        open={isFilterOpen}
        onClose={() => setIsFilterOpen(false)}
        PaperProps={{
          sx: {
            width: { xs: '100%', sm: 400 },
            bgcolor: 'background.paper',
            boxShadow: '-4px 0 24px rgba(0,0,0,0.1)'
          }
        }}
      >
        <Box sx={{ 
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          height: '100%'
        }}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            mb: 3
          }}>
            <Typography variant="h6" sx={{ 
              fontWeight: 600,
              color: 'text.primary'
            }}>
              Filter Plants
            </Typography>
            <IconButton 
              onClick={() => setIsFilterOpen(false)}
              sx={{
                color: 'text.secondary',
                '&:hover': {
                  bgcolor: 'action.hover'
                }
              }}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          <Box sx={{ 
            display: 'flex',
            flexDirection: 'column',
            gap: 3,
            flex: 1,
            overflowY: 'auto',
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              background: '#f1f1f1',
              borderRadius: '4px',
            },
            '&::-webkit-scrollbar-thumb': {
              background: '#888',
              borderRadius: '4px',
              '&:hover': {
                background: '#666',
              },
            },
          }}>
            <Stack spacing={3}>
              <Autocomplete
                multiple
                size="small"
                options={availableFilters.attracts}
                value={filter.attracts || []}
                onChange={(_, value) => handleFilterChange('attracts', value)}
                renderInput={(params) => (
                  <TextField 
                    {...params} 
                    label="Attracts" 
                    variant="outlined" 
                    size="small"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: '8px',
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  />
                )}
              />
              <Autocomplete
                size="small"
                options={availableFilters.types}
                value={filter.type || null}
                onChange={(_, value) => handleFilterChange('type', value)}
                renderInput={(params) => (
                  <TextField 
                    {...params} 
                    label="Plant Type" 
                    variant="outlined" 
                    size="small"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: '8px',
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  />
                )}
              />
              <Autocomplete
                size="small"
                options={availableFilters.growthRates}
                value={filter.growthRate || null}
                onChange={(_, value) => handleFilterChange('growthRate', value)}
                renderInput={(params) => (
                  <TextField 
                    {...params} 
                    label="Growth Rate" 
                    variant="outlined" 
                    size="small"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: '8px',
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  />
                )}
              />
              <Autocomplete
                size="small"
                options={availableFilters.maintenance}
                value={filter.maintenance || null}
                onChange={(_, value) => handleFilterChange('maintenance', value)}
                renderInput={(params) => (
                  <TextField 
                    {...params} 
                    label="Maintenance" 
                    variant="outlined" 
                    size="small"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: '8px',
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  />
                )}
              />
              <Autocomplete
                size="small"
                options={availableFilters.cycles}
                value={filter.cycle || null}
                onChange={(_, value) => handleFilterChange('cycle', value)}
                renderInput={(params) => (
                  <TextField 
                    {...params} 
                    label="Life Cycle" 
                    variant="outlined" 
                    size="small"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: '8px',
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  />
                )}
              />
              <Autocomplete
                size="small"
                options={availableFilters.watering}
                value={filter.watering || null}
                onChange={(_, value) => handleFilterChange('watering', value)}
                renderInput={(params) => (
                  <TextField 
                    {...params} 
                    label="Watering Needs" 
                    variant="outlined" 
                    size="small"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: '8px',
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  />
                )}
              />
              <Autocomplete
                multiple
                size="small"
                options={availableFilters.sunlight}
                value={filter.sunlight || []}
                onChange={(_, value) => handleFilterChange('sunlight', value)}
                renderInput={(params) => (
                  <TextField 
                    {...params} 
                    label="Sunlight Requirements" 
                    variant="outlined" 
                    size="small"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: '8px',
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  />
                )}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={filter.is_evergreen || false}
                    onChange={(e) => handleFilterChange('is_evergreen', e.target.checked)}
                    color="primary"
                  />
                }
                label="Evergreen"
                sx={{
                  '& .MuiFormControlLabel-label': {
                    fontWeight: 500,
                    color: 'text.primary'
                  }
                }}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={filter.edible_fruit || false}
                    onChange={(e) => handleFilterChange('edible_fruit', e.target.checked)}
                    color="primary"
                  />
                }
                label="Edible Fruit"
                sx={{
                  '& .MuiFormControlLabel-label': {
                    fontWeight: 500,
                    color: 'text.primary'
                  }
                }}
              />
            </Stack>
          </Box>

          <Box sx={{ 
            mt: 3,
            pt: 2,
            borderTop: '1px solid',
            borderColor: 'divider',
            display: 'flex',
            gap: 2
          }}>
            <Button
              fullWidth
              variant="outlined"
              onClick={handleClearFilters}
              startIcon={<ClearIcon />}
              sx={{
                borderRadius: '8px',
                textTransform: 'none',
                fontWeight: 600
              }}
            >
              Clear All
            </Button>
            <Button
              fullWidth
              variant="contained"
              onClick={() => {
                handleSearch();
                setIsFilterOpen(false);
              }}
              startIcon={<SearchIcon />}
              sx={{
                borderRadius: '8px',
                textTransform: 'none',
                fontWeight: 600
              }}
            >
              Apply Filters
            </Button>
          </Box>
        </Box>
      </Drawer>

      {/* Plant Details Dialog */}
      <PlantDetails
        plant={selectedPlant}
        open={detailsOpen}
        onClose={handleCloseDetails}
        sections={[]}
      />
    </Box>
  );
};

export default PlantSuggestions; 