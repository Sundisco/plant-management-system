import React from 'react';
import { Box, List, ListItem, ListItemText, ListItemAvatar, Avatar, IconButton, Typography, Chip, Collapse, IconButton as MuiIconButton, Paper } from '@mui/material';
import { Droppable, Draggable, DraggableProvided, DraggableStateSnapshot, DroppableProvided, DroppableStateSnapshot } from '@hello-pangea/dnd';
import DeleteIcon from '@mui/icons-material/Delete';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
import { Plant } from '../../types/Plant';
import { Section } from '../../types/Section';
import { PlantGrid } from './PlantGrid';

interface PlantListProps {
  plants: Plant[];
  plantsByType: { [key: string]: Plant[] };
  plantIndexMap: Map<number, number>;
  expandedTypes: { [key: string]: boolean };
  onToggleType: (type: string) => void;
  onPlantClick: (plant: Plant) => void;
  onRemovePlant: (plantId: number) => void;
  droppableId: string;
  sections?: Section[];
}

export const PlantList: React.FC<PlantListProps> = ({
  plants,
  plantsByType,
  plantIndexMap,
  expandedTypes,
  onToggleType,
  onPlantClick,
  onRemovePlant,
  droppableId,
  sections
}) => {
  const sectionList = sections ?? [];
  const [viewMode, setViewMode] = React.useState<'list' | 'grid'>('list');
  const getSectionName = (sectionId: string | null | undefined) => {
    if (!sectionId || !Array.isArray(sectionList)) return 'Unassigned';
    const section = sectionList.find(s => s.section_id === sectionId);
    if (!section) return 'Unassigned';
    return `${section.glyph || '🌱'} ${section.name}`;
  };

  // For Current Garden, show grouped by type, each type as its own Droppable
  if (droppableId === 'unassigned')
    return (
      <Box>
        {Object.entries(plantsByType).map(([type, typePlants]) => (
          <Box key={type} sx={{ mb: 2 }}>
            <Paper
              elevation={0}
              sx={{ 
                position: 'sticky',
                top: 0,
                zIndex: 2,
                bgcolor: 'background.paper',
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                p: 1.5,
                borderRadius: 2,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                border: '1px solid',
                borderColor: 'divider',
                '&:hover': {
                  bgcolor: 'background.paper',
                  borderColor: 'primary.light',
                },
              }}
              onClick={() => onToggleType(type)}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <Typography variant="subtitle1" sx={{ 
                  fontWeight: 600,
                  color: 'text.primary'
                }}>
                  {type}
                </Typography>
                <Chip 
                  label={typePlants.length} 
                  size="small" 
                  color="primary" 
                  variant="outlined"
                  sx={{ 
                    fontWeight: 500,
                    height: '24px'
                  }}
                />
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <IconButton
                  size="small"
                  onClick={e => { e.stopPropagation(); setViewMode(viewMode === 'list' ? 'grid' : 'list'); }}
                  sx={{ ml: 1 }}
                >
                  {viewMode === 'list' ? <ViewModuleIcon /> : <ViewListIcon />}
                </IconButton>
                <MuiIconButton 
                  size="small"
                  sx={{
                    color: 'primary.main',
                    transition: 'transform 0.2s ease',
                    transform: expandedTypes[type] ? 'rotate(180deg)' : 'none'
                  }}
                >
                  <ExpandMoreIcon />
                </MuiIconButton>
              </Box>
            </Paper>
            <Collapse in={expandedTypes[type]}>
              <Droppable droppableId={`type-${type}`}>
                {(provided: DroppableProvided, snapshot: DroppableStateSnapshot) => {
                  if (viewMode === 'grid') {
                    return (
                      <PlantGrid
                        plants={typePlants}
                        onPlantClick={onPlantClick}
                        droppableProvided={provided}
                        droppableSnapshot={snapshot}
                        sections={sections}
                        chipMode="section"
                        columns={2}
                        showOnlySectionChip={true}
                      />
                    );
                  } else {
                    return (
                      <List
                        ref={provided.innerRef}
                        {...provided.droppableProps}
                        sx={{ 
                          width: '100%', 
                          bgcolor: 'transparent',
                          mt: 1,
                          minHeight: '50px',
                          '& > .MuiListItem-root': {
                            mb: 1,
                            '&:last-child': {
                              mb: 0
                            }
                          }
                        }}
                      >
                        {typePlants.map((plant, index) => (
                          <Draggable
                            key={`plant-${plant.id}`}
                            draggableId={`plant-${plant.id}`}
                            index={index}
                          >
                            {(provided: DraggableProvided, snapshot: DraggableStateSnapshot) => {
                              const listItemProps = {
                                ref: provided.innerRef,
                                ...provided.draggableProps,
                                ...provided.dragHandleProps,
                                sx: {
                                  cursor: 'grab',
                                  bgcolor: 'background.paper',
                                  position: 'relative',
                                  transition: 'all 0.2s ease',
                                  borderRadius: 2,
                                  border: '1px solid',
                                  borderColor: snapshot.isDragging ? 'primary.main' : 'divider',
                                  boxShadow: snapshot.isDragging ? '0 4px 12px rgba(0,0,0,0.1)' : 'none',
                                  transform: snapshot.isDragging ? 'scale(1.02)' : 'none',
                                  display: 'flex',
                                  alignItems: 'center',
                                  minHeight: 80,
                                  py: 1,
                                  px: 1.5,
                                  mb: 1,
                                  '&:hover': {
                                    bgcolor: 'action.hover',
                                    borderColor: 'primary.light',
                                    '& .delete-button': {
                                      opacity: 1,
                                    },
                                  },
                                },
                                onClick: () => onPlantClick(plant)
                              };

                              return (
                                <ListItem {...listItemProps}>
                                  {/* Rectangular image thumbnail */}
                                  {plant.image_url ? (
                                    <Box sx={{
                                      width: 96,
                                      height: 72,
                                      borderRadius: 2,
                                      overflow: 'hidden',
                                      boxShadow: 1,
                                      mr: 2,
                                      flexShrink: 0,
                                      background: '#f5f5f5',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                    }}>
                                      <img
                                        src={plant.image_url}
                                        alt={plant.common_name}
                                        style={{
                                          width: '100%',
                                          height: '100%',
                                          objectFit: 'cover',
                                          display: 'block',
                                        }}
                                      />
                                    </Box>
                                  ) : (
                                    <Avatar 
                                      sx={{ 
                                        width: 96, 
                                        height: 72,
                                        borderRadius: 2,
                                        mr: 2,
                                        bgcolor: 'primary.light',
                                        color: 'primary.contrastText',
                                        fontSize: 32,
                                        flexShrink: 0,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                      }}
                                    >
                                      🌿
                                    </Avatar>
                                  )}
                                  {/* Plant info */}
                                  <Box sx={{ flex: 1, minWidth: 0 }}>
                                    <Typography
                                      variant="body1"
                                      sx={{ fontWeight: 600, color: 'text.primary', mb: 0.5, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
                                    >
                                      {plant.common_name}
                                    </Typography>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                      <Chip
                                        label={getSectionName(plant.section)}
                                        size="small"
                                        sx={{
                                          bgcolor: 'background.paper',
                                          color: 'primary.main',
                                          border: '1px solid',
                                          borderColor: 'primary.light',
                                          fontWeight: 500,
                                          fontSize: '0.75rem',
                                          height: '22px',
                                          px: 1,
                                        }}
                                      />
                                    </Box>
                                  </Box>
                                  <IconButton
                                    size="small"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      onRemovePlant(plant.id);
                                    }}
                                    className="delete-button"
                                    sx={{
                                      opacity: 0,
                                      transition: 'all 0.2s ease',
                                      bgcolor: 'error.light',
                                      color: 'error.contrastText',
                                      '&:hover': {
                                        bgcolor: 'error.main',
                                        transform: 'scale(1.1)',
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
                        {provided.placeholder}
                      </List>
                    );
                  }
                }}
              </Droppable>
            </Collapse>
          </Box>
        ))}
      </Box>
    );

  // For Sections, show flat list
  return (
    <Droppable droppableId={droppableId}>
      {(provided: DroppableProvided, snapshot: DroppableStateSnapshot): JSX.Element => (
        <Box
          ref={provided.innerRef}
          {...provided.droppableProps}
          sx={{ 
            minHeight: '100px',
            p: 1,
            borderRadius: 2,
            border: snapshot.isDraggingOver ? '2px dashed' : 'none',
            borderColor: 'primary.main',
            bgcolor: snapshot.isDraggingOver ? 'action.hover' : 'transparent',
            transition: 'all 0.2s ease'
          }}
        >
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
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: snapshot.isDragging ? 'primary.main' : 'divider',
                    boxShadow: snapshot.isDragging ? '0 4px 12px rgba(0,0,0,0.1)' : 'none',
                    transform: snapshot.isDragging ? 'scale(1.02)' : 'none',
                    mb: 1,
                    '&:hover': {
                      bgcolor: 'action.hover',
                      borderColor: 'primary.light',
                    },
                  },
                  onClick: () => onPlantClick(plant)
                };

                return (
                  <ListItem {...listItemProps}>
                    <ListItemAvatar>
                      <Avatar 
                        src={plant.image_url}
                        alt={plant.common_name}
                        sx={{ 
                          width: 48, 
                          height: 48,
                          bgcolor: 'primary.light',
                          color: 'primary.contrastText',
                          border: '2px solid',
                          borderColor: 'background.paper',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                        }}
                      >
                        🌿
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={plant.common_name}
                      secondary={plant.type}
                      primaryTypographyProps={{
                        variant: 'body1',
                        sx: { 
                          fontWeight: 600,
                          color: 'text.primary',
                          mb: 0.5
                        }
                      }}
                      secondaryTypographyProps={{
                        variant: 'caption',
                        sx: {
                          color: 'text.secondary',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5
                        }
                      }}
                    />
                    <IconButton 
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRemovePlant(plant.id);
                      }}
                      sx={{
                        bgcolor: 'error.light',
                        color: 'error.contrastText',
                        '&:hover': {
                          bgcolor: 'error.main',
                          transform: 'scale(1.1)',
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
          {provided.placeholder}
        </Box>
      )}
    </Droppable>
  );
}; 