import React from 'react';
import { Box, Card, CardContent, Typography, Chip, Avatar } from '@mui/material';
import { Plant } from '../../types/Plant';
import { Draggable } from '@hello-pangea/dnd';
import { Section } from '../../types/Section';
import LocationOnIcon from '@mui/icons-material/LocationOn';

interface PlantGridProps {
  plants: Plant[];
  onPlantClick: (plant: Plant) => void;
  droppableProvided?: any;
  droppableSnapshot?: any;
  sections?: Section[];
  chipMode?: 'section' | 'type';
  columns?: number;
  showOnlySectionChip?: boolean;
}

export const PlantGrid: React.FC<PlantGridProps> = ({ plants, onPlantClick, droppableProvided, droppableSnapshot, sections = [], chipMode = 'type', columns = 3, showOnlySectionChip = false }) => {
  const getSectionName = (sectionId: string | null | undefined) => {
    if (!sectionId || !Array.isArray(sections)) return 'Unassigned';
    const section = sections.find(s => s.section_id === sectionId);
    if (!section) return 'Unassigned';
    return `${section.glyph || '🌱'} ${section.name}`;
  };

  return (
    <Box
      sx={{ 
        display: 'grid', 
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: 2,
        p: 2
      }}
      ref={droppableProvided ? droppableProvided.innerRef : undefined}
      {...(droppableProvided ? droppableProvided.droppableProps : {})}
    >
      {plants.map((plant, index) => (
        <Draggable key={plant.id} draggableId={`plant-${plant.id}`} index={index}>
          {(provided) => (
            <Card
              ref={provided.innerRef}
              {...provided.draggableProps}
              {...provided.dragHandleProps}
              onClick={() => onPlantClick(plant)}
              sx={{
                position: 'relative',
                height: '240px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 12px 24px rgba(0,0,0,0.15)',
                  '& .MuiCardMedia-root': {
                    transform: 'scale(1.05)'
                  }
                },
                borderRadius: '16px',
                overflow: 'hidden',
                bgcolor: 'background.paper',
                border: '1px solid',
                borderColor: 'divider'
              }}
            >
              {plant.image_url && (
                <Box sx={{ 
                  position: 'relative',
                  height: '100%',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.5))',
                    zIndex: 1
                  }
                }}>
                  <img
                    src={plant.image_url}
                    alt={plant.common_name}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      transition: 'transform 0.5s ease'
                    }}
                  />
                  <Box sx={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    zIndex: 2,
                    p: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 1
                  }}>
                    <Typography variant="h6" sx={{ 
                      color: 'white',
                      fontWeight: 600,
                      fontSize: '1.1rem',
                      lineHeight: 1.2,
                      textShadow: '0 1px 2px rgba(0,0,0,0.2)'
                    }}>
                      {plant.common_name}
                    </Typography>
                    <Box sx={{ 
                      display: 'flex', 
                      flexWrap: 'wrap', 
                      gap: 0.75
                    }}>
                      {chipMode === 'section' && (
                        <Chip 
                          icon={<LocationOnIcon sx={{ color: 'white' }} />} 
                          label={getSectionName(plant.section)}
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
                      {!showOnlySectionChip && (
                        <>
                          {chipMode !== 'section' && (
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
                          )}
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
                        </>
                      )}
                    </Box>
                  </Box>
                </Box>
              )}
            </Card>
          )}
        </Draggable>
      ))}
      {droppableProvided && droppableProvided.placeholder}
    </Box>
  );
}; 