import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, List, ListItem, ListItemText, ListItemAvatar, Avatar, IconButton, ListItemSecondaryAction, Chip, Collapse, IconButton as MuiIconButton, Dialog, DialogContent, DialogTitle, Grid } from '@mui/material';
import { DragDropContext, Droppable, Draggable, DropResult, DraggableProvided, DraggableStateSnapshot, DroppableProvided, DroppableStateSnapshot } from '@hello-pangea/dnd';
import DeleteIcon from '@mui/icons-material/Delete';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import CloseIcon from '@mui/icons-material/Close';
import { PlantSearch } from './PlantSearch';
import { Plant } from '../types/Plant';
import WateringSchedule from './WateringSchedule';
import { PruningSchedule } from './PruningSchedule';
import { PlantSuggestions } from './PlantSuggestions';
import { API_ENDPOINTS } from '../config';

interface Section {
  id: string;
  name: string;
}

interface GardenProps {
  userId: number;
}

export function Garden({ userId }: GardenProps) {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [expandedTypes, setExpandedTypes] = useState<{ [key: string]: boolean }>({});
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  const sections: Section[] = [
    { id: 'A', name: 'Section A' },
    { id: 'B', name: 'Section B' },
    { id: 'C', name: 'Section C' },
  ];

  const GARDEN_DROPPABLE_ID = 'garden';
  const UNASSIGNED_DROPPABLE_ID = 'unassigned';

  const plantsInSection = plants.filter(plant => plant.section === selectedSection);

  useEffect(() => {
    // Fetch plants for the default user
    fetch(API_ENDPOINTS.USER_PLANTS(userId))
      .then(res => res.json())
      .then(data => setPlants(data))
      .catch(err => console.error('Error fetching plants:', err));
  }, [userId]);

  const handleRemovePlant = async (plantId: number) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.USER_PLANTS(userId)}/${plantId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Remove plant from local state
        setPlants(plants => plants.filter(p => p.id !== plantId));
      } else {
        console.error('Failed to remove plant');
      }
    } catch (error) {
      console.error('Error removing plant:', error);
    }
  };

  const handlePlantAdded = (newPlant: Plant) => {
    setPlants(prevPlants => {
      // Check if plant already exists
      const existingPlant = prevPlants.find(p => p.id === newPlant.id);
      if (existingPlant) {
        // Update existing plant while preserving its section
        return prevPlants.map(p => 
          p.id === newPlant.id 
            ? { ...newPlant, section: existingPlant.section }
            : p
        );
      }
      // Add new plant with all fields
      return [...prevPlants, {
        ...newPlant,
        section: null,
        image_url: newPlant.image_url || '',
        scientific_name: newPlant.scientific_name || [],
        other_names: newPlant.other_names || [],
        type: newPlant.type || ''
      }];
    });
  };

  const unassignedPlants = plants.filter(plant => plant.section === null);

  const handleDragEnd = async (result: DropResult) => {
    document.body.style.overflow = 'auto';

    const { source, destination, draggableId } = result;
    
    if (!destination) return;

    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    ) return;

    const plantId = parseInt(draggableId.split('-')[1]);
    const newSection = destination.droppableId === UNASSIGNED_DROPPABLE_ID ? null : destination.droppableId;

    try {
      const response = await fetch(API_ENDPOINTS.PLANT_SECTION(userId, plantId), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ section: newSection }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update section: ${response.statusText}`);
      }

      // Update local state immediately
      setPlants(prevPlants => 
        prevPlants.map(p => 
          p.id === plantId 
            ? { ...p, section: newSection }
            : p
        )
      );

    } catch (error) {
      console.error('Error updating plant section:', error);
      // On error, refresh the entire garden data
      await fetch(API_ENDPOINTS.USER_PLANTS(userId));
    }
  };

  // Group plants by type
  const plantsByType = plants.reduce((acc, plant) => {
    const type = plant.type || 'Other';
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(plant);
    return acc;
  }, {} as { [key: string]: Plant[] });

  const toggleTypeExpansion = (type: string) => {
    setExpandedTypes(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  const handlePlantClick = (plant: Plant) => {
    // Create a new object with all the plant data to ensure we have the latest state
    const plantData = {
      ...plant,
      attracts: plant.attracts || [],
      sunlight: plant.sunlight || []
    };
    setSelectedPlant(plantData);
    setDetailsOpen(true);
  };

  const handleClosePlantDetails = () => {
    setSelectedPlant(null);
  };

  const renderCurrentGarden = (): JSX.Element => (
    <Paper sx={{ 
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      position: 'relative'
    }}>
      <Typography variant="h6" sx={{ p: 2, pb: 1 }}>Current Garden</Typography>
      <Box sx={{ 
        flex: 1,
        overflowY: 'auto',
        position: 'relative'
      }}>
        <Droppable droppableId={UNASSIGNED_DROPPABLE_ID}>
          {(provided: DroppableProvided, snapshot: DroppableStateSnapshot): JSX.Element => (
            <Box
              ref={provided.innerRef}
              {...provided.droppableProps}
              sx={{ 
                maxHeight: '600px', 
                overflowY: 'auto',
                '&::-webkit-scrollbar': {
                  width: '8px',
                },
                '&::-webkit-scrollbar-track': {
                  background: '#f1f1f1',
                },
                '&::-webkit-scrollbar-thumb': {
                  background: '#888',
                  borderRadius: '4px',
                },
                border: snapshot.isDraggingOver ? '2px dashed' : 'none',
                borderColor: 'primary.main',
                borderRadius: 1,
                p: 1,
              }}
            >
              {Object.entries(plantsByType).map(([type, plants]) => (
                <Box key={type} sx={{ mb: 2 }}>
                  <Box 
                    sx={{ 
                      position: 'sticky',
                      top: 0,
                      zIndex: 1,
                      bgcolor: 'background.paper',
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between',
                      p: 1,
                      borderRadius: 1,
                      cursor: 'pointer',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                      '&:hover': {
                        bgcolor: 'action.hover',
                      },
                    }}
                    onClick={() => toggleTypeExpansion(type)}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        {type}
                      </Typography>
                      <Chip 
                        label={plants.length} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                      />
                    </Box>
                    <MuiIconButton size="small">
                      {expandedTypes[type] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </MuiIconButton>
                  </Box>
                  <Collapse in={expandedTypes[type]}>
                    <List sx={{ 
                      width: '100%', 
                      bgcolor: 'background.paper',
                      mt: 1, // Add some space between header and list
                      borderRadius: 1,
                      '& > .MuiListItem-root': {
                        mb: 1, // Add space between list items
                        '&:last-child': {
                          mb: 0
                        }
                      }
                    }}>
                      {plants.map((plant, index) => (
                        <Draggable
                          key={`plant-${plant.id}`}
                          draggableId={`plant-${plant.id}`}
                          index={index}
                        >
                          {(provided: DraggableProvided, snapshot: DraggableStateSnapshot): JSX.Element => {
                            const listItemProps = {
                              ref: provided.innerRef,
                              ...provided.draggableProps,
                              ...provided.dragHandleProps,
                              sx: {
                                cursor: 'grab',
                                bgcolor: 'background.paper',
                                position: 'relative',
                                transition: 'all 0.2s ease',
                                ...(plant.section && {
                                  '&::before': {
                                    content: '""',
                                    position: 'absolute',
                                    left: 0,
                                    top: 0,
                                    bottom: 0,
                                    width: '3px',
                                    bgcolor: 'primary.main',
                                    borderRadius: '3px 0 0 3px',
                                  },
                                }),
                                '&:hover': {
                                  bgcolor: 'action.hover',
                                  '& .delete-button': {
                                    opacity: 1,
                                  },
                                },
                                ...(snapshot.isDragging && {
                                  bgcolor: 'action.hover',
                                  boxShadow: 3,
                                }),
                              },
                              onClick: () => handlePlantClick(plant)
                            };

                            return (
                              <ListItem {...listItemProps}>
                                <ListItemAvatar>
                                  <Avatar 
                                    src={plant.image_url}
                                    alt={plant.common_name}
                                    sx={{ 
                                      width: 40, 
                                      height: 40,
                                      bgcolor: 'primary.light',
                                      color: 'primary.contrastText',
                                    }}
                                  >
                                    🌿
                                  </Avatar>
                                </ListItemAvatar>
                                <ListItemText
                                  primary={plant.common_name}
                                  secondary={plant.section ? `Section ${plant.section}` : 'Unassigned'}
                                  primaryTypographyProps={{
                                    variant: 'body2',
                                    sx: { fontWeight: 'medium' }
                                  }}
                                  secondaryTypographyProps={{
                                    variant: 'caption',
                                    color: 'text.secondary'
                                  }}
                                />
                                <IconButton 
                                  size="small"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleRemovePlant(plant.id);
                                  }}
                                  className="delete-button"
                                  sx={{
                                    opacity: 0,
                                    transition: 'opacity 0.2s ease',
                                    '&:hover': {
                                      bgcolor: 'error.light',
                                      color: 'error.contrastText',
                                    },
                                  }}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </ListItem>
                            );
                          }}
                        </Draggable>
                      ))}
                    </List>
                  </Collapse>
                </Box>
              ))}
              {provided.placeholder}
            </Box>
          )}
        </Droppable>
      </Box>
    </Paper>
  );

  return (
    <Box sx={{ 
      height: '100vh', 
      display: 'grid', 
      gridTemplateColumns: '250px 1fr 1fr', 
      gap: 2, 
      p: 2,
      overflow: 'hidden', // Prevent page scrolling
      position: 'fixed', // Fix the container to viewport
      top: 0,
      left: 0,
      right: 0,
      bottom: 0
    }}>
      <DragDropContext onDragEnd={handleDragEnd}>
        {/* Left Column */}
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          height: '100%',
          position: 'relative',
          overflow: 'hidden' // Contain scrolling
        }}>
          {/* Search Section - Fixed at top */}
          <Box sx={{ 
            position: 'sticky', 
            top: 0, 
            zIndex: 2, 
            bgcolor: 'background.default', 
            pb: 2 
          }}>
            <PlantSearch onPlantAdded={handlePlantAdded} />
          </Box>

          {/* Current Garden - Scrollable area */}
          <Box sx={{ 
            flex: 1,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            mb: 2
          }}>
            <Paper sx={{ 
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}>
              {/* Fixed Header */}
              <Box sx={{ 
                borderBottom: 1, 
                borderColor: 'divider',
                p: 2
              }}>
                <Typography variant="h6">Current Garden</Typography>
              </Box>

              {/* Scrollable Content */}
              <Box sx={{ 
                flex: 1,
                overflowY: 'auto'
              }}>
                <Droppable droppableId={UNASSIGNED_DROPPABLE_ID}>
                  {(provided: DroppableProvided, snapshot: DroppableStateSnapshot): JSX.Element => (
                    <Box
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      sx={{ p: 1 }}
                    >
                      {Object.entries(plantsByType).map(([type, plants]) => (
                        <Box key={type} sx={{ mb: 2 }}>
                          <Box 
                            sx={{ 
                              position: 'sticky',
                              top: 0,
                              zIndex: 1,
                              bgcolor: 'background.paper',
                              display: 'flex', 
                              alignItems: 'center', 
                              justifyContent: 'space-between',
                              p: 1,
                              borderRadius: 1,
                              cursor: 'pointer',
                              boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                              '&:hover': {
                                bgcolor: 'action.hover',
                              },
                            }}
                            onClick={() => toggleTypeExpansion(type)}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                                {type}
                              </Typography>
                              <Chip 
                                label={plants.length} 
                                size="small" 
                                color="primary" 
                                variant="outlined"
                              />
                            </Box>
                            <MuiIconButton size="small">
                              {expandedTypes[type] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                            </MuiIconButton>
                          </Box>
                          <Collapse in={expandedTypes[type]}>
                            <List sx={{ 
                              width: '100%', 
                              bgcolor: 'background.paper',
                              mt: 1, // Add some space between header and list
                              borderRadius: 1,
                              '& > .MuiListItem-root': {
                                mb: 1, // Add space between list items
                                '&:last-child': {
                                  mb: 0
                                }
                              }
                            }}>
                              {plants.map((plant, index) => (
                                <Draggable
                                  key={`plant-${plant.id}`}
                                  draggableId={`plant-${plant.id}`}
                                  index={index}
                                >
                                  {(provided: DraggableProvided, snapshot: DraggableStateSnapshot): JSX.Element => {
                                    const listItemProps = {
                                      ref: provided.innerRef,
                                      ...provided.draggableProps,
                                      ...provided.dragHandleProps,
                                      sx: {
                                        cursor: 'grab',
                                        bgcolor: 'background.paper',
                                        position: 'relative',
                                        transition: 'all 0.2s ease',
                                        ...(plant.section && {
                                          '&::before': {
                                            content: '""',
                                            position: 'absolute',
                                            left: 0,
                                            top: 0,
                                            bottom: 0,
                                            width: '3px',
                                            bgcolor: 'primary.main',
                                            borderRadius: '3px 0 0 3px',
                                          },
                                        }),
                                        '&:hover': {
                                          bgcolor: 'action.hover',
                                          '& .delete-button': {
                                            opacity: 1,
                                          },
                                        },
                                        ...(snapshot.isDragging && {
                                          bgcolor: 'action.hover',
                                          boxShadow: 3,
                                        }),
                                      },
                                      onClick: () => handlePlantClick(plant)
                                    };

                                    return (
                                      <ListItem {...listItemProps}>
                                        <ListItemAvatar>
                                          <Avatar 
                                            src={plant.image_url}
                                            alt={plant.common_name}
                                            sx={{ 
                                              width: 40, 
                                              height: 40,
                                              bgcolor: 'primary.light',
                                              color: 'primary.contrastText',
                                            }}
                                          >
                                            🌿
                                          </Avatar>
                                        </ListItemAvatar>
                                        <ListItemText
                                          primary={plant.common_name}
                                          secondary={plant.section ? `Section ${plant.section}` : 'Unassigned'}
                                          primaryTypographyProps={{
                                            variant: 'body2',
                                            sx: { fontWeight: 'medium' }
                                          }}
                                          secondaryTypographyProps={{
                                            variant: 'caption',
                                            color: 'text.secondary'
                                          }}
                                        />
                                        <IconButton 
                                          size="small"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            handleRemovePlant(plant.id);
                                          }}
                                          className="delete-button"
                                          sx={{
                                            opacity: 0,
                                            transition: 'opacity 0.2s ease',
                                            '&:hover': {
                                              bgcolor: 'error.light',
                                              color: 'error.contrastText',
                                            },
                                          }}
                                        >
                                          <DeleteIcon fontSize="small" />
                                        </IconButton>
                                      </ListItem>
                                    );
                                  }}
                                </Draggable>
                              ))}
                            </List>
                          </Collapse>
                        </Box>
                      ))}
                      {provided.placeholder}
                    </Box>
                  )}
                </Droppable>
              </Box>
            </Paper>
          </Box>
          
          {/* Sections Selection - Fixed at bottom */}
          <Paper sx={{ 
            bgcolor: 'background.paper'
          }}>
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="h6" gutterBottom>Sections</Typography>
            </Box>
            <List>
              {sections.map((section) => (
                <ListItem 
                  key={section.id}
                  button
                  selected={selectedSection === section.id}
                  onClick={() => setSelectedSection(section.id)}
                >
                  <ListItemText primary={section.name} />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Box>

        {/* Middle Column */}
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: 2,
          height: '100%',
          overflow: 'hidden' // Contain scrolling
        }}>
          {/* Watering Schedule - Fixed height */}
          <Box sx={{ height: '400px' }}>
            <WateringSchedule sectionId={selectedSection ? parseInt(selectedSection) : undefined} />
          </Box>
          
          {/* Selected Section Plants - Scrollable area */}
          <Box sx={{ 
            flex: 1,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <Paper sx={{ 
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}>
              {/* Fixed Header */}
              <Box sx={{ 
                borderBottom: 1, 
                borderColor: 'divider',
                p: 2
              }}>
                <Typography variant="h6">
                  {selectedSection ? `Section ${selectedSection} Plants` : 'Select a Section'}
                </Typography>
              </Box>
              
              {/* Scrollable Content */}
              <Box sx={{ 
                flex: 1,
                overflowY: 'auto'
              }}>
                {selectedSection ? (
                  <Droppable droppableId={selectedSection}>
                    {(provided: DroppableProvided, snapshot: DroppableStateSnapshot): JSX.Element => (
                      <Box
                        ref={provided.innerRef}
                        {...provided.droppableProps}
                        sx={{ 
                          flex: 1,
                          display: 'flex',
                          flexDirection: 'column',
                          p: 2,
                          border: '2px dashed',
                          borderColor: snapshot.isDraggingOver ? 'primary.main' : 'grey.300',
                          borderRadius: 1,
                          m: 2,
                          minHeight: '200px',
                          bgcolor: snapshot.isDraggingOver ? 'action.hover' : 'background.default'
                        }}
                      >
                        {plantsInSection.length > 0 ? (
                          <List sx={{ width: '100%' }}>
                            {plantsInSection.map((plant, index) => (
                              <Draggable 
                                key={`plant-${plant.id}`}
                                draggableId={`plant-${plant.id}`}
                                index={index}
                              >
                                {(provided: DraggableProvided, snapshot: DraggableStateSnapshot): JSX.Element => {
                                  const listItemProps = {
                                    ref: provided.innerRef,
                                    ...provided.draggableProps,
                                    ...provided.dragHandleProps,
                                    sx: {
                                      mb: 1,
                                      bgcolor: 'background.paper',
                                      borderRadius: 1,
                                      boxShadow: snapshot.isDragging ? 3 : 1,
                                      '&:hover': {
                                        bgcolor: 'action.hover',
                                      },
                                    },
                                    onClick: () => handlePlantClick(plant)
                                  };

                                  return (
                                    <ListItem {...listItemProps}>
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
                                        secondary={plant.type}
                                      />
                                      <IconButton 
                                        edge="end" 
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleRemovePlant(plant.id);
                                        }}
                                      >
                                        <DeleteIcon />
                                      </IconButton>
                                    </ListItem>
                                  );
                                }}
                              </Draggable>
                            ))}
                          </List>
                        ) : (
                          <Box 
                            sx={{ 
                              flex: 1,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: 'text.secondary',
                              fontSize: '0.875rem'
                            }}
                          >
                            Drag plants here to add them to Section {selectedSection}
                          </Box>
                        )}
                        {provided.placeholder}
                      </Box>
                    )}
                  </Droppable>
                ) : (
                  <Box 
                    sx={{ 
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'text.secondary',
                      p: 2
                    }}
                  >
                    Select a section from the left to view and organize plants
                  </Box>
                )}
              </Box>
            </Paper>
          </Box>
        </Box>

        {/* Right Column */}
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: 2,
          height: '100%',
          overflow: 'hidden' // Contain scrolling
        }}>
          <PruningSchedule selectedSection={selectedSection} userPlants={plants} />
          <PlantSuggestions selectedSection={selectedSection} />
        </Box>
      </DragDropContext>

      {/* Plant Details Dialog */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <div className="flex justify-between items-center">
            <span>{selectedPlant?.common_name}</span>
            <IconButton onClick={() => setDetailsOpen(false)} size="small">
              <CloseIcon />
            </IconButton>
          </div>
        </DialogTitle>
        <DialogContent>
          {selectedPlant && (
            <Grid container spacing={4}>
              {/* Left Column - Image and Basic Info */}
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <img 
                    src={selectedPlant.image_url} 
                    alt={selectedPlant.common_name}
                    style={{ width: '100%', height: '300px', objectFit: 'cover', borderRadius: '8px' }}
                  />
                  
                  <Box>
                    <Typography variant="h6" sx={{ color: 'text.primary', mb: 1 }}>
                      {selectedPlant.scientific_name?.[0]}
                    </Typography>
                    {selectedPlant.other_names && selectedPlant.other_names.length > 0 && (
                      <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
                        Also known as: {selectedPlant.other_names.join(', ')}
                      </Typography>
                    )}

                    {/* Plant Type and Characteristics */}
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      <Chip 
                        label={selectedPlant.type} 
                        sx={{ bgcolor: 'success.light', color: 'success.dark' }}
                      />
                      {selectedPlant.is_evergreen ? (
                        <Chip 
                          label="Evergreen" 
                          sx={{ bgcolor: 'info.light', color: 'info.dark' }}
                        />
                      ) : (
                        <Chip 
                          label="Deciduous" 
                          sx={{ bgcolor: 'warning.light', color: 'warning.dark' }}
                        />
                      )}
                      {selectedPlant.edible_fruit && (
                        <Chip 
                          label="Edible Fruit" 
                          sx={{ bgcolor: 'error.light', color: 'error.dark' }}
                        />
                      )}
                    </Box>

                    {/* Description */}
                    {selectedPlant.description && (
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: 'text.secondary', fontWeight: 'medium', mb: 1 }}>
                          Description
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {selectedPlant.description}
                        </Typography>
                      </Box>
                    )}
                  </Box>

                  {/* Growing Conditions */}
                  <Box>
                    <Typography variant="h6" sx={{ color: 'text.primary', borderBottom: 1, borderColor: 'divider', pb: 1, mb: 2 }}>
                      Growing Conditions
                    </Typography>
                    
                    {/* Sunlight Requirements */}
                    {selectedPlant.sunlight && selectedPlant.sunlight.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" sx={{ color: 'text.secondary', fontWeight: 'medium', mb: 1 }}>
                          Sunlight Requirements
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {selectedPlant.sunlight.map((condition, index) => (
                            <Chip
                              key={index}
                              label={condition}
                              size="small"
                              sx={{ bgcolor: 'warning.light', color: 'warning.dark' }}
                            />
                          ))}
                        </Box>
                      </Box>
                    )}

                    {/* Watering */}
                    {selectedPlant.watering && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" sx={{ color: 'text.secondary', fontWeight: 'medium', mb: 1 }}>
                          Watering
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {selectedPlant.watering}
                        </Typography>
                      </Box>
                    )}

                    {/* Hardiness Zone */}
                    {selectedPlant.hardiness_zone && (
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: 'text.secondary', fontWeight: 'medium', mb: 1 }}>
                          Hardiness Zone
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {selectedPlant.hardiness_zone}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </Box>
              </Grid>

              {/* Right Column - Additional Info */}
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  {/* Plant Characteristics */}
                  <Box>
                    <Typography variant="h6" sx={{ color: 'text.primary', borderBottom: 1, borderColor: 'divider', pb: 1, mb: 2 }}>
                      Plant Characteristics
                    </Typography>

                    {/* Growth Rate */}
                    {selectedPlant.growth_rate && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" sx={{ color: 'text.secondary', fontWeight: 'medium', mb: 1 }}>
                          Growth Rate
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {selectedPlant.growth_rate}
                        </Typography>
                      </Box>
                    )}

                    {/* Maintenance */}
                    {selectedPlant.maintenance && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" sx={{ color: 'text.secondary', fontWeight: 'medium', mb: 1 }}>
                          Maintenance
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {selectedPlant.maintenance}
                        </Typography>
                      </Box>
                    )}

                    {/* Life Cycle */}
                    {selectedPlant.cycle && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" sx={{ color: 'text.secondary', fontWeight: 'medium', mb: 1 }}>
                          Life Cycle
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {selectedPlant.cycle}
                        </Typography>
                      </Box>
                    )}
                  </Box>

                  {/* Wildlife Attractions */}
                  {selectedPlant.attracts && selectedPlant.attracts.length > 0 && (
                    <Box>
                      <Typography variant="h6" sx={{ color: 'text.primary', borderBottom: 1, borderColor: 'divider', pb: 1, mb: 2 }}>
                        Wildlife Attractions
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {selectedPlant.attracts.map((species, index) => (
                          <Chip
                            key={index}
                            label={species}
                            sx={{ bgcolor: 'info.light', color: 'info.dark' }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {/* Current Location */}
                  <Box sx={{ pt: 2, borderTop: 1, borderColor: 'divider' }}>
                    <Typography variant="subtitle2" sx={{ color: 'text.secondary', fontWeight: 'medium', mb: 1 }}>
                      Current Location
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      {selectedPlant.section ? `Section ${selectedPlant.section}` : 'Unassigned'}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
} 