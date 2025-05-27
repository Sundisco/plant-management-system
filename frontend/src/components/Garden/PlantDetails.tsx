import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, IconButton, Grid, Box, Typography, Chip, Avatar, Button, DialogActions } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { Plant } from '../../types/Plant';
import { Section } from '../../types/Section';
import PlantGuidesTabs from '../PlantGuidesTabs/PlantGuidesTabs';
import { useTheme } from '@mui/material/styles';
import LocationOnIcon from '@mui/icons-material/LocationOn';

interface PlantDetailsProps {
  plant: Plant | null;
  open: boolean;
  onClose: () => void;
  sections?: Section[];
}

export const PlantDetails: React.FC<PlantDetailsProps> = ({ plant, open, onClose, sections = [] }) => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [plantData, setPlantData] = useState<Plant | null>(null);

  useEffect(() => {
    if (plant) {
      setPlantData(plant);
    }
  }, [plant]);

  const getSectionName = (sectionId: string | undefined | null) => {
    if (!sectionId) return 'Unassigned';
    const section = sections.find(s => s.section_id === sectionId);
    return section ? section.name : 'Unassigned';
  };

  if (!plantData) {
    return null;
  }

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '16px',
          overflow: 'hidden'
        }
      }}
    >
      <DialogTitle sx={{ 
        p: 3,
        background: 'linear-gradient(to right, rgba(255,255,255,0.95), rgba(255,255,255,1))',
        borderBottom: '1px solid',
        borderColor: 'divider'
      }}>
        <div className="flex justify-between items-center">
          <Box>
            <Typography variant="h5" sx={{ 
              fontWeight: 600,
              mb: 0.5,
              color: 'text.primary'
            }}>
              {plantData.common_name}
            </Typography>
            <Typography variant="subtitle1" sx={{ 
              color: 'text.secondary',
              fontStyle: 'italic'
            }}>
              {plantData.scientific_name?.[0]}
            </Typography>
            {plantData.other_names && plantData.other_names.length > 0 && (
              <Typography variant="body2" sx={{ 
                color: 'text.secondary',
                mt: 0.5
              }}>
                Also known as: {plantData.other_names.join(', ')}
              </Typography>
            )}
          </Box>
          <IconButton 
            onClick={onClose} 
            size="small"
            sx={{
              bgcolor: 'action.hover',
              '&:hover': {
                bgcolor: 'action.selected'
              }
            }}
          >
            <CloseIcon />
          </IconButton>
        </div>
      </DialogTitle>
      <DialogContent sx={{ p: 2 }}>
        <Grid container spacing={2}>
          {/* Left Column - Image and Basic Info */}
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ 
                position: 'relative',
                borderRadius: '12px',
                overflow: 'hidden',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}>
                <img 
                  src={plantData.image_url} 
                  alt={plantData.common_name}
                  style={{ 
                    width: '100%', 
                    height: '300px', 
                    objectFit: 'cover'
                  }}
                />
                <Box 
                  className="overlay"
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%)',
                    opacity: 0,
                    transition: 'opacity 0.3s ease',
                    display: 'flex',
                    alignItems: 'flex-end',
                    p: 2
                  }}
                >
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    <Chip 
                      label={plantData.type} 
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
                    {plantData.edible_fruit && (
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
                    {plantData.cycle === 'perennial' && (
                      <Chip 
                        label="Perennial" 
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
                  </Box>
                </Box>
              </Box>
              
              {/* Description */}
              {plantData.description && (
                <Box sx={{ 
                  p: 2,
                  borderRadius: '12px',
                  bgcolor: 'background.paper',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                }}>
                  <Typography variant="h6" sx={{ 
                    color: 'text.primary', 
                    mb: 1.5,
                    fontWeight: 600,
                    borderBottom: '2px solid',
                    borderColor: 'primary.main',
                    pb: 0.5
                  }}>
                    Description
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    color: 'text.secondary',
                    lineHeight: 1.6,
                    fontSize: '0.9rem'
                  }}>
                    {plantData.description}
                  </Typography>
                </Box>
              )}

              {/* Growing Conditions */}
              <Box sx={{ 
                p: 2,
                borderRadius: '12px',
                bgcolor: 'background.paper',
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
              }}>
                <Typography variant="h6" sx={{ 
                  color: 'text.primary', 
                  mb: 1.5,
                  fontWeight: 600,
                  borderBottom: '2px solid',
                  borderColor: 'primary.main',
                  pb: 0.5
                }}>
                  Growing Conditions
                </Typography>
                
                {/* Sunlight Requirements */}
                {plantData.sunlight && plantData.sunlight.length > 0 && (
                  <Box sx={{ mb: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle2" sx={{ 
                        color: 'text.secondary', 
                        fontWeight: 600,
                        minWidth: '100px'
                      }}>
                        Sunlight:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {plantData.sunlight.map((condition, index) => (
                          <Chip
                            key={index}
                            label={condition}
                            size="small"
                            sx={{ 
                              bgcolor: 'rgba(255, 193, 7, 0.85)',
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
                        ))}
                      </Box>
                    </Box>
                  </Box>
                )}

                {/* Watering */}
                {plantData.watering && (
                  <Box sx={{ mb: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                      <Typography variant="subtitle2" sx={{ 
                        color: 'text.secondary', 
                        fontWeight: 600,
                        minWidth: '100px'
                      }}>
                        Watering:
                      </Typography>
                      <Typography variant="body2" sx={{ 
                        color: 'text.secondary',
                        lineHeight: 1.6,
                        fontSize: '0.9rem'
                      }}>
                        {plantData.watering}
                      </Typography>
                    </Box>
                  </Box>
                )}

                {/* Hardiness Zone */}
                {plantData.hardiness_zone && (
                  <Box sx={{ mb: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle2" sx={{ 
                        color: 'text.secondary', 
                        fontWeight: 600,
                        minWidth: '100px'
                      }}>
                        Hardiness:
                      </Typography>
                      <Chip
                        label={`Zone ${plantData.hardiness_zone}`}
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
                    </Box>
                  </Box>
                )}
              </Box>
            </Box>
          </Grid>

          {/* Right Column - Details and Guides */}
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {/* Plant Details */}
              <Box sx={{ 
                p: 2,
                borderRadius: '12px',
                bgcolor: 'background.paper',
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
              }}>
                <Typography variant="h6" sx={{ 
                  color: 'text.primary', 
                  mb: 1.5,
                  fontWeight: 600,
                  borderBottom: '2px solid',
                  borderColor: 'primary.main',
                  pb: 0.5
                }}>
                  Plant Details
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {/* Type */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2" sx={{ 
                      color: 'text.secondary', 
                      fontWeight: 600,
                      minWidth: '100px'
                    }}>
                      Type:
                    </Typography>
                    <Chip
                      label={plantData.type}
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
                  </Box>

                  {/* Section */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2" sx={{ 
                      color: 'text.secondary', 
                      fontWeight: 600,
                      minWidth: '100px'
                    }}>
                      Section:
                    </Typography>
                    <Chip
                      icon={<LocationOnIcon sx={{ color: 'white' }} />}
                      label={getSectionName(plantData.section)}
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
                  </Box>
                </Box>
              </Box>

              {/* Wildlife Attractions */}
              {plantData.attracts && plantData.attracts.length > 0 && (
                <Box sx={{ 
                  p: 2,
                  borderRadius: '12px',
                  bgcolor: 'background.paper',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                }}>
                  <Typography variant="h6" sx={{ 
                    color: 'text.primary', 
                    mb: 1.5,
                    fontWeight: 600,
                    borderBottom: '2px solid',
                    borderColor: 'primary.main',
                    pb: 0.5
                  }}>
                    Wildlife Attractions
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {plantData.attracts.map((species, index) => (
                      <Chip
                        key={index}
                        label={species}
                        size="small"
                        sx={{ 
                          bgcolor: 'rgba(255, 152, 0, 0.85)',
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
                    ))}
                  </Box>
                </Box>
              )}

              {/* Plant Guides Tabs */}
              <Box sx={{ 
                p: 2,
                borderRadius: '12px',
                bgcolor: 'background.paper',
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
              }}>
                <Typography variant="h6" sx={{ 
                  color: 'text.primary', 
                  mb: 1.5,
                  fontWeight: 600,
                  borderBottom: '2px solid',
                  borderColor: 'primary.main',
                  pb: 0.5
                }}>
                  Care Guides
                </Typography>
                <PlantGuidesTabs plantId={plantData.id} />
              </Box>
            </Box>
          </Grid>
        </Grid>
      </DialogContent>
    </Dialog>
  );
}; 