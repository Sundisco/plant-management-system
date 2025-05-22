import React, { useState, useEffect, useMemo } from 'react';
import { Box, Paper, Typography, Tooltip, CircularProgress, Table, TableBody, TableCell, TableHead, TableRow, Select, MenuItem, Dialog, DialogTitle, DialogContent, IconButton, List, ListItem, ListItemText, ListItemAvatar, Avatar } from '@mui/material';
import { Plant } from '../types/Plant';
import { API_ENDPOINTS } from '../config';
import { api } from '../utils/api';
import CloseIcon from '@mui/icons-material/Close';
import { PlantDetails } from './Garden/PlantDetails';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';

interface Section {
  id: number;
  section_id: string;
  name: string;
  glyph: string;
  user_id: number;
  created_at?: string;
  updated_at?: string;
}

interface PruningScheduleProps {
  selectedSection: string | null;
  userPlants: Plant[];
  onPlantClick: (plant: Plant) => void;
  sections: Section[];
  sectionFilter: string;
  setSectionFilter: (val: string) => void;
}

interface PlantDetail {
  id: number;
  name: string;
}

interface PruningData {
  section: string;
  months: {
    [key: string]: number;
  };
  details: {
    [key: string]: PlantDetail[];
  };
}

interface PruningScheduleResponse {
  pruning_schedule: PruningData[];
}

const SEASON_COLORS = {
  winter: '#E3F2FD', // Light blue
  spring: '#E8F5E9', // Light green
  summer: '#FFF3E0', // Light orange
  autumn: '#FFEBEE'  // Light red
};

const getSeason = (month: string): keyof typeof SEASON_COLORS => {
  const monthIndex = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].indexOf(month);
  if (monthIndex <= 1 || monthIndex === 11) return 'winter';
  if (monthIndex <= 4) return 'spring';
  if (monthIndex <= 7) return 'summer';
  return 'autumn';
};

const getMostCommonType = (plants: Plant[]): string => {
  if (!plants || plants.length === 0) return 'None';
  
  const types = plants.map(p => p.type || 'Other');
  const counts = types.reduce((acc, type) => {
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const sortedTypes = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  return sortedTypes.length > 0 ? sortedTypes[0][0] : 'None';
};

const estimatePruningTime = (plants: Plant[]): string => {
  const totalTime = plants.reduce((acc, plant) => {
    // Assuming each plant takes 15-30 minutes to prune
    return acc + (Math.random() * 15 + 15);
  }, 0);
  const hours = Math.floor(totalTime / 60);
  const minutes = Math.round(totalTime % 60);
  return hours > 0 
    ? `${hours}h ${minutes}m`
    : `${minutes}m`;
};

export const PruningSchedule: React.FC<PruningScheduleProps> = ({ 
  selectedSection, 
  userPlants,
  onPlantClick,
  sections,
  sectionFilter,
  setSectionFilter
}) => {
  const [pruningData, setPruningData] = useState<PruningData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCell, setSelectedCell] = useState<{ type: string; monthIdx: number; plants: Plant[] } | null>(null);
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null);
  const [prunedMap, setPrunedMap] = useState<{ [plantId: number]: boolean }>({});

  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  // Get all unique sections from userPlants
  const allSections = [
    { id: 'unassigned', name: 'Unassigned' },
    ...sections.map(section => ({
      id: section.section_id,
      name: section.name
    }))
  ];

  useEffect(() => {
    const fetchPruningSchedule = async () => {
      try {
        setLoading(true);
        const userId = 1;
        const { data, error } = await api.get<PruningScheduleResponse>(API_ENDPOINTS.PRUNING(userId));
        
        if (error) {
          throw new Error(error);
        }
        
        if (!data?.pruning_schedule) {
          throw new Error('No pruning schedule data received');
        }
        
        console.log('[PruningSchedule] Fetched data:', data.pruning_schedule);
        setPruningData(data.pruning_schedule);
        setError(null);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchPruningSchedule();
  }, [userPlants]);

  // First, create a map of all plants with their pruning months
  const plantPruningMap = new Map<number, string[]>();
  
  // Debug log for initial data
  console.log('[PruningSchedule] Initial userPlants:', userPlants.map(p => ({
    id: p.id,
    name: p.common_name,
    section: p.section
  })));
  
  console.log('[PruningSchedule] Initial pruningData:', pruningData);

  // Process all pruning data first
  pruningData.forEach(section => {
    console.log('[PruningSchedule] Processing section:', section.section);
    Object.entries(section.details || {}).forEach(([month, plants]) => {
      console.log(`[PruningSchedule] Month ${month} plants:`, plants);
      plants.forEach(plant => {
        const currentMonths = plantPruningMap.get(plant.id) || [];
        if (!currentMonths.includes(month)) {
          plantPruningMap.set(plant.id, [...currentMonths, month]);
        }
      });
    });
  });

  // Debug log for plant pruning map
  console.log('[PruningSchedule] Plant pruning map:', 
    Array.from(plantPruningMap.entries()).map(([id, months]) => ({
      id,
      months
    }))
  );

  // Then merge with user plants
  const mergedPlants = userPlants.map(plant => {
    // Get pruning months directly from the pruning data
    const pruningMonths = plantPruningMap.get(plant.id) || [];
    
    console.log('[PruningSchedule] Processing plant:', {
      id: plant.id,
      name: plant.common_name,
      section: plant.section,
      pruningMonths
    });

    return { ...plant, pruningMonths };
  });

  // Debug log for merged plants
  console.log('[PruningSchedule] Merged plants:', 
    mergedPlants.map(p => ({
      id: p.id,
      name: p.common_name,
      section: p.section,
      pruningMonths: (p as any).pruningMonths
    }))
  );

  // Group plants by type, then by month
  const matrix: { [type: string]: typeof mergedPlants[] } = {};
  const filteredPlants = mergedPlants.filter(p => {
    const matches = !sectionFilter || 
      (sectionFilter === 'unassigned' ? !p.section : p.section === sectionFilter);
    
    console.log('[PruningSchedule] Filtering plant:', {
      id: p.id,
      name: p.common_name,
      section: p.section,
      sectionFilter,
      matches,
      pruningMonths: (p as any).pruningMonths
    });
    
    return matches;
  });

  console.log('[PruningSchedule] Filtered plants:', 
    filteredPlants.map(p => ({
      id: p.id,
      name: p.common_name,
      section: p.section,
      pruningMonths: (p as any).pruningMonths
    }))
  );

  filteredPlants.forEach(plant => {
    const type = plant.type || 'Other';
    if (!matrix[type]) matrix[type] = Array(12).fill(null).map(() => []);
    
    // Convert pruning months to 0-based indices
    const pruningMonths: number[] = (plant as any).pruningMonths
      .map((m: string | number) => Number(m) - 1)
      .filter((m: number) => Number.isInteger(m) && m >= 0 && m < 12);

    pruningMonths.forEach((monthIdx: number) => {
      matrix[type][monthIdx].push(plant);
    });
  });

  // Find max for color scaling
  const max = Math.max(1, ...Object.values(matrix).flatMap(arr => arr.map(plants => plants.length)));

  // Calculate monthly totals
  const monthlyTotals = useMemo(() => {
    const totals = Array(12).fill(0);
    
    Object.values(matrix).forEach(monthArr => {
      monthArr.forEach((plants, monthIdx) => {
        totals[monthIdx] += plants.length;
      });
    });

    return {
      totalTasks: totals,
      maxTasks: Math.max(...totals)
    };
  }, [matrix]);

  const handleCellClick = (type: string, monthIdx: number, plants: Plant[]) => {
    if (plants.length > 0) {
      setSelectedCell({ type, monthIdx, plants });
    }
  };

  const handleMonthlyWorkloadClick = (monthIdx: number) => {
    // Get all plants that need pruning in this month
    const plantsInMonth = Object.values(matrix)
      .map(monthArr => monthArr[monthIdx])
      .flat()
      .filter(Boolean);
    
    if (plantsInMonth.length > 0) {
      setSelectedCell({ type: 'Monthly Workload', monthIdx, plants: plantsInMonth });
    }
  };

  const handlePlantClick = (plant: Plant) => {
    onPlantClick(plant);
    setSelectedCell(null);
  };

  const handleCloseDetails = () => {
    setSelectedPlant(null);
  };

  // Helper to get section name from id
  const getSectionName = (sectionId: string | null | undefined) => {
    if (!sectionId) return 'Unassigned';
    const section = sections.find(s => s.section_id === sectionId);
    return section ? section.name : sectionId;
  };

  if (loading) return <Paper sx={{ p: 2, display: 'flex', justifyContent: 'center' }}><CircularProgress /></Paper>;
  if (error) return <Paper sx={{ p: 2 }}><Typography color="error">{error}</Typography></Paper>;
  if (!pruningData.length) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>Pruning Schedule</Typography>
        <Typography color="textSecondary">No pruning data available</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ 
      p: 2,
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      background: 'linear-gradient(to bottom, #ffffff, #f8f9fa)',
      boxShadow: '0 2px 12px rgba(0,0,0,0.08)'
    }}>
      <Box sx={{ 
        flex: 1,
        overflow: 'auto',
        '&::-webkit-scrollbar': {
          width: '8px',
          height: '8px'
        },
        '&::-webkit-scrollbar-track': {
          background: '#f1f1f1',
          borderRadius: '4px'
        },
        '&::-webkit-scrollbar-thumb': {
          background: '#888',
          borderRadius: '4px',
          '&:hover': {
            background: '#666'
          }
        }
      }}>
        <Table size="small" sx={{ 
          tableLayout: 'fixed',
          minWidth: 'max-content'
        }}>
        <TableHead>
          <TableRow>
              <TableCell sx={{ 
                position: 'sticky',
                left: 0,
                bgcolor: 'background.paper',
                zIndex: 2,
                borderRight: '1px solid rgba(224, 224, 224, 1)',
                width: '140px',
                fontWeight: 600,
                fontSize: '0.95rem'
              }}>Plant Type</TableCell>
            {MONTHS.map(month => (
                <TableCell 
                  key={month} 
                  align="center" 
                  sx={{ 
                    width: '70px',
                    fontWeight: 600,
                    color: 'primary.main',
                    bgcolor: SEASON_COLORS[getSeason(month)],
                    borderBottom: '2px solid',
                    borderColor: 'divider',
                    fontSize: '0.9rem',
                    py: 1.5
                  }}
                >
                  {month}
                </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {Object.entries(matrix).map(([type, monthArr]) => (
            <TableRow key={type}>
                <TableCell sx={{ 
                  position: 'sticky',
                  left: 0,
                  bgcolor: 'background.paper',
                  zIndex: 1,
                  borderRight: '1px solid rgba(224, 224, 224, 1)',
                  fontWeight: 500,
                  fontSize: '0.9rem'
                }}>{type}</TableCell>
              {monthArr.map((plants, monthIdx) => (
                <TableCell
                  key={monthIdx}
                  align="center"
                  onClick={() => handleCellClick(type, monthIdx, plants)}
                  sx={{
                    bgcolor: plants.length
                      ? `rgba(46, 125, 50, ${0.1 + 0.7 * (plants.length / max)})`
                      : 'background.paper',
                    color: plants.length ? '#1b5e20' : 'text.secondary',
                    cursor: plants.length ? 'pointer' : 'default',
                    fontWeight: plants.length ? 600 : 400,
                    borderRadius: 1,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    height: 40,
                    fontSize: '0.9rem',
                    '&:hover': plants.length ? {
                      transform: 'scale(1.1)',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                      zIndex: 1,
                      bgcolor: `rgba(46, 125, 50, ${0.2 + 0.7 * (plants.length / max)})`
                    } : {}
                  }}
                >
                  {plants.length > 0 ? (
                    <Tooltip
                      title={
                        <Box sx={{ p: 1.5 }}>
                            <Typography variant="subtitle2" sx={{ 
                              mb: 1,
                              fontWeight: 600,
                              color: '#1b5e20'
                            }}>
                              {`${plants.length} plants need pruning`}
                            </Typography>
                            <Typography variant="caption" display="block" sx={{ mb: 0.5 }}>
                              {`Most common type: ${getMostCommonType(plants)}`}
                            </Typography>
                            <Typography variant="caption" display="block" sx={{ color: 'text.secondary' }}>
                              {`Estimated time: ${estimatePruningTime(plants)}`}
                            </Typography>
                        </Box>
                      }
                      arrow
                      placement="top"
                      componentsProps={{
                        tooltip: {
                          sx: {
                            bgcolor: 'white',
                            color: 'text.primary',
                            boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                            '& .MuiTooltip-arrow': {
                              color: 'white'
                            }
                          }
                        }
                      }}
                    >
                      <span>{plants.length}</span>
                    </Tooltip>
                  ) : ''}
                </TableCell>
              ))}
            </TableRow>
          ))}
            {/* Monthly Workload Summary Row */}
            <TableRow sx={{ 
              position: 'sticky',
              bottom: 0,
              bgcolor: 'background.paper',
              borderTop: '2px solid',
              borderColor: 'divider',
              '& td': {
                borderBottom: 'none'
              }
            }}>
              <TableCell sx={{ 
                position: 'sticky',
                left: 0,
                bgcolor: 'background.paper',
                zIndex: 2,
                borderRight: '1px solid rgba(224, 224, 224, 1)',
                fontWeight: 600,
                fontSize: '0.95rem',
                color: 'primary.main'
              }}>
                Monthly Workload
              </TableCell>
              {MONTHS.map((_, monthIdx) => (
                <TableCell
                  key={monthIdx}
                  align="center"
                  onClick={() => handleMonthlyWorkloadClick(monthIdx)}
                  sx={{
                    bgcolor: monthlyTotals.totalTasks[monthIdx] > 0
                      ? `rgba(46, 125, 50, ${0.1 + 0.7 * (monthlyTotals.totalTasks[monthIdx] / monthlyTotals.maxTasks)})`
                      : 'background.paper',
                    color: monthlyTotals.totalTasks[monthIdx] > 0 ? '#1b5e20' : 'text.secondary',
                    fontWeight: 600,
                    position: 'relative',
                    cursor: monthlyTotals.totalTasks[monthIdx] > 0 ? 'pointer' : 'default',
                    borderRadius: 1,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    height: 40,
                    fontSize: '0.95rem',
                    '&:hover': monthlyTotals.totalTasks[monthIdx] > 0 ? {
                      transform: 'scale(1.1)',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                      zIndex: 1,
                      bgcolor: `rgba(46, 125, 50, ${0.2 + 0.7 * (monthlyTotals.totalTasks[monthIdx] / monthlyTotals.maxTasks)})`
                    } : {}
                  }}
                >
                  <Tooltip
                    title={
                      <Box sx={{ p: 1.5 }}>
                        <Typography variant="subtitle2" sx={{ 
                          mb: 1,
                          fontWeight: 600,
                          color: '#1b5e20'
                        }}>
                          {`${monthlyTotals.totalTasks[monthIdx]} total pruning tasks`}
                        </Typography>
                        <Typography variant="caption" display="block" sx={{ mb: 0.5 }}>
                          {`Most common type: ${getMostCommonType(Object.values(matrix).map(monthArr => monthArr[monthIdx]).flat().filter(Boolean))}`}
                        </Typography>
                        <Typography variant="caption" display="block" sx={{ color: 'text.secondary' }}>
                          {`Estimated time: ${estimatePruningTime(Object.values(matrix).map(monthArr => monthArr[monthIdx]).flat().filter(Boolean))}`}
                        </Typography>
                      </Box>
                    }
                    arrow
                    placement="top"
                    componentsProps={{
                      tooltip: {
                        sx: {
                          bgcolor: 'white',
                          color: 'text.primary',
                          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                          '& .MuiTooltip-arrow': {
                            color: 'white'
                          }
                        }
                      }
                    }}
                  >
                    <span>{monthlyTotals.totalTasks[monthIdx]}</span>
                  </Tooltip>
                </TableCell>
              ))}
            </TableRow>
          </TableBody>
        </Table>
      </Box>

      {/* Plant List Dialog */}
      <Dialog 
        open={!!selectedCell} 
        onClose={() => setSelectedCell(null)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
          }
        }}
      >
        <DialogTitle
          sx={{
            borderBottom: '1px solid',
            borderColor: 'divider',
            pb: 1.5,
            background: 'linear-gradient(45deg, #2e7d32 30%, #43a047 90%)',
            color: 'white',
            minHeight: 0
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 500,
                fontSize: '1.1rem',
                letterSpacing: 0.2,
                color: 'white',
                mb: 0
              }}
            >
              {selectedCell && `${MONTHS[selectedCell.monthIdx]} Pruning`}
            </Typography>
            {selectedCell?.type && (
              <Box
                component="span"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.18)',
                  color: 'white',
                  fontWeight: 400,
                  fontSize: '0.8rem',
                  borderRadius: 1,
                  px: 1,
                  py: 0.25,
                  ml: 0.5,
                  letterSpacing: 0.5,
                  boxShadow: 'none'
                }}
              >
                {selectedCell.type}
              </Box>
            )}
            <Box sx={{ flex: 1 }} />
            <IconButton
              onClick={() => setSelectedCell(null)}
              size="small"
              sx={{
                color: 'white',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' }
              }}
            >
              <CloseIcon />
            </IconButton>
          </Box>
          <Typography
            variant="body2"
            sx={{
              opacity: 0.85,
              fontWeight: 400,
              fontSize: '0.95rem',
              mt: 0.5
            }}
          >
            {selectedCell && `${selectedCell.plants.length} plants need pruning`}
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ p: 3 }}>
          <Typography
            variant="body2"
            color="text.secondary"
            gutterBottom
            sx={{ mb: 2 }}
          >
            {selectedCell && `Estimated total time: ${estimatePruningTime(selectedCell.plants)}`}
          </Typography>
          <Box sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 3,
            bgcolor: 'background.paper',
            borderRadius: 1,
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
            p: 2
          }}>
            {selectedCell?.plants.map(plant => (
              <Box
                key={plant.id}
                sx={{
                  position: 'relative',
                  borderRadius: 3,
                  overflow: 'hidden',
                  boxShadow: '0 2px 12px rgba(46,125,50,0.10)',
                  bgcolor: 'background.default',
                  height: 180,
                  display: 'flex',
                  alignItems: 'flex-end',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    boxShadow: '0 8px 24px rgba(46,125,50,0.18)',
                    transform: 'translateY(-2px) scale(1.03)'
                  }
                }}
                onClick={e => {
                  // Only open details if not clicking the checkmark
                  if ((e.target as HTMLElement).closest('.prune-checkmark-btn')) return;
                  handlePlantClick(plant);
                }}
              >
                {/* Plant image as background */}
                {plant.image_url ? (
                  <Box
                    component="img"
                    src={plant.image_url}
                    alt={plant.common_name}
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      zIndex: 1
                    }}
                  />
                ) : (
                  <Avatar
                    variant="rounded"
                    sx={{
                      width: '100%',
                      height: '100%',
                      fontSize: 56,
                      bgcolor: 'primary.light',
                      color: 'primary.contrastText',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      zIndex: 1
                    }}
                  >
                    🌿
                  </Avatar>
                )}
                {/* Overlay with title and chips */}
                <Box
                  sx={{
                    position: 'absolute',
                    left: 0,
                    right: 0,
                    bottom: 0,
                    zIndex: 2,
                    p: 1,
                    background: 'linear-gradient(0deg, rgba(0,0,0,0.55) 80%, rgba(0,0,0,0.08) 100%)',
                    color: 'white',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 0.5
                  }}
                >
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.95rem', mb: 0.25, textShadow: '0 2px 8px rgba(0,0,0,0.18)' }}>
                    {plant.common_name}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    <Box
                      component="span"
                      sx={{
                        bgcolor: 'rgba(255,255,255,0.8)',
                        color: 'primary.main',
                        fontWeight: 600,
                        fontSize: '0.75rem',
                        borderRadius: 1,
                        px: 0.75,
                        py: 0.15,
                        mr: 0.5
                      }}
                    >
                      {plant.type}
                    </Box>
                    <Box
                      component="span"
                      sx={{
                        bgcolor: 'rgba(255,255,255,0.8)',
                        color: 'success.dark',
                        fontWeight: 600,
                        fontSize: '0.75rem',
                        borderRadius: 1,
                        px: 0.75,
                        py: 0.15
                      }}
                    >
                      {getSectionName(plant.section)}
                    </Box>
                  </Box>
                </Box>
                {/* Checkmark button */}
                <IconButton
                  className="prune-checkmark-btn"
                  size="small"
                  sx={{
                    position: 'absolute',
                    top: 10,
                    right: 10,
                    bgcolor: prunedMap[plant.id] ? 'success.main' : 'grey.200',
                    color: prunedMap[plant.id] ? 'success.contrastText' : 'grey.600',
                    boxShadow: prunedMap[plant.id] ? '0 2px 8px rgba(46,125,50,0.15)' : 'none',
                    transition: 'all 0.2s',
                    zIndex: 3,
                    '&:hover': {
                      bgcolor: prunedMap[plant.id] ? 'success.dark' : 'grey.300',
                      color: prunedMap[plant.id] ? 'success.contrastText' : 'grey.800',
                    }
                  }}
                  onClick={e => {
                    e.stopPropagation();
                    setPrunedMap(prev => ({
                      ...prev,
                      [plant.id]: !prev[plant.id]
                    }));
                  }}
                >
                  {prunedMap[plant.id] ? <CheckCircleIcon /> : <RadioButtonUncheckedIcon />}
                </IconButton>
              </Box>
            ))}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Plant Details Dialog */}
      {selectedPlant && (
        <PlantDetails
          plant={selectedPlant}
          open={!!selectedPlant}
          onClose={handleCloseDetails}
          sections={sections}
        />
      )}
    </Paper>
  );
}; 
