import React, { useState } from 'react';
import { Box, Paper, Typography, List, ListItem, ListItemText, ListItemAvatar, Avatar, IconButton, TextField, Dialog, DialogTitle, DialogContent, DialogActions, Button, Grid, Select, MenuItem, Badge } from '@mui/material';
import { DragDropContext, Droppable, Draggable, DroppableProvided, DraggableProvided, DroppableStateSnapshot, DraggableStateSnapshot } from '@hello-pangea/dnd';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import FilterListIcon from '@mui/icons-material/FilterList';
import { PlantSearch } from '../PlantSearch';
import { PlantList } from './PlantList';
import WateringSchedule from '../WateringSchedule';
import { PruningSchedule } from '../PruningSchedule';
import { PlantSuggestions } from '../PlantSuggestions';
import { Plant } from '../../types/Plant';
import { PlantGrid } from './PlantGrid';

interface Section {
  id: number;
  section_id: string;
  name: string;
  glyph: string;
  user_id: number;
  created_at?: string;
  updated_at?: string;
}

interface GardenLayoutProps {
  plants: Plant[];
  plantsByType: { [key: string]: Plant[] };
  plantIndexMap: Map<number, number>;
  expandedTypes: { [key: string]: boolean };
  selectedSection: string | null;
  onToggleType: (type: string) => void;
  onPlantClick: (plant: Plant) => void;
  onRemovePlant: (plantId: number) => void;
  onDragEnd: (result: any) => void;
  onPlantAdded: (plant: Plant) => void;
  onSectionSelect: (sectionId: string) => void;
  sections: Section[];
  onAddSection: (name: string, glyph: string) => void;
  onRenameSection: (id: number, name: string, glyph: string) => void;
  onDeleteSection: (id: number) => void;
}

const UNASSIGNED_DROPPABLE_ID = 'unassigned';

// Add a list of garden-related emojis
const GARDEN_EMOJIS = [
  '🌱', '🌿', '🌳', '🌲', '🌴', '🌵', '🌸', '🌺', '🌻', '🌼',
  '🌷', '🌹', '🍀', '☘️', '🌾', '🌽', '🥕', '🥬', '🥦', '🍅',
  '🍆', '🥒', '🥑', '🥝', '🍎', '🍐', '🍊', '🍋', '🍌', '🍇',
  '🍓', '🫐', '🍈', '🍉', '🍑', '🍒', '🍍', '🥭', '🥥', '🌰'
];

export const GardenLayout: React.FC<GardenLayoutProps> = ({
  plants,
  plantsByType,
  plantIndexMap,
  expandedTypes,
  selectedSection,
  onToggleType,
  onPlantClick,
  onRemovePlant,
  onDragEnd,
  onPlantAdded,
  onSectionSelect,
  sections,
  onAddSection,
  onRenameSection,
  onDeleteSection,
}) => {
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [newSectionName, setNewSectionName] = useState('');
  const [renameSectionId, setRenameSectionId] = useState<number | null>(null);
  const [renameSectionName, setRenameSectionName] = useState('');
  const [deleteSectionId, setDeleteSectionId] = useState<number | null>(null);
  const [selectedGlyph, setSelectedGlyph] = useState<string>('');
  const [isNextWeek, setIsNextWeek] = useState(false);
  const [sectionFilter, setSectionFilter] = useState('');
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [activeFilterCount, setActiveFilterCount] = useState(0);

  const plantsInSection = plants.filter(plant => plant.section === selectedSection);

  const handleAddSectionClick = () => {
    setNewSectionName('');
    setSelectedGlyph(GARDEN_EMOJIS[Math.floor(Math.random() * GARDEN_EMOJIS.length)]); // Random default
    setAddDialogOpen(true);
  };
  const handleAddSectionConfirm = () => {
    if (newSectionName.trim()) {
      onAddSection(newSectionName.trim(), selectedGlyph);
      setAddDialogOpen(false);
    }
  };

  const handleRenameClick = (id: number, name: string, glyph: string) => {
    setRenameSectionId(id);
    setRenameSectionName(name);
    setSelectedGlyph(glyph);
    setRenameDialogOpen(true);
  };
  const handleRenameConfirm = () => {
    if (renameSectionId !== null && renameSectionName.trim()) {
      onRenameSection(renameSectionId, renameSectionName.trim(), selectedGlyph);
      setRenameDialogOpen(false);
    }
  };

  const handleDeleteClick = (id: number) => {
    setDeleteSectionId(id);
    setDeleteDialogOpen(true);
  };
  const handleDeleteConfirm = () => {
    if (deleteSectionId !== null) {
      onDeleteSection(deleteSectionId);
      setDeleteDialogOpen(false);
    }
  };

  return (
    <Box sx={{ 
      height: 'calc(100vh - 120px)',
      display: 'grid', 
      gridTemplateColumns: 'minmax(300px, 1fr) minmax(400px, 2fr) minmax(400px, 2fr)', 
      gap: 2, 
      p: 0,
      overflow: 'hidden',
      position: 'relative',
      width: '100%',
    }}>
      <DragDropContext onDragEnd={onDragEnd}>
        {/* Left Column */}
        <Paper elevation={2} sx={{ bgcolor: 'background.paper', borderRadius: 3, boxShadow: 2, p: 0, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0, overflow: 'hidden' }}>
          {/* Current Garden Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', bgcolor: '#f5f5f5', borderBottom: '1px solid #e0e0e0', p: 1, minHeight: 38, gap: 1.5 }}>
            <Typography component="span" sx={{ fontSize: 28, mr: 1 }}>🌳</Typography>
            <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>Current Garden</Typography>
          </Box>
          {/* Search bar */}
          <Box sx={{ p: 2, pt: 0 }}>
            <PlantSearch onPlantAdded={onPlantAdded} />
          </Box>
          {/* Aggregated plant type list (with counts and grid/list toggle) */}
          <Box sx={{ p: 2, pt: 0, flexGrow: 1, minHeight: 0, maxHeight: 'calc(100vh - 350px)', overflowY: 'auto' }}>
            <PlantList
              plants={plants}
              plantsByType={plantsByType}
              plantIndexMap={plantIndexMap}
              expandedTypes={expandedTypes}
              onToggleType={onToggleType}
              onPlantClick={onPlantClick}
              onRemovePlant={onRemovePlant}
              droppableId={UNASSIGNED_DROPPABLE_ID}
              sections={sections}
            />
          </Box>
          {/* Spacer before Sections */}
          <Box sx={{ height: 12 }} />
          {/* Sections Header + Add Button */}
          <Box sx={{ display: 'flex', alignItems: 'center', bgcolor: '#f5f5f5', borderBottom: '1px solid #e0e0e0', p: 1, minHeight: 38, gap: 1.5, justifyContent: 'space-between', flexShrink: 0 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Typography component="span" sx={{ fontSize: 24, mr: 1 }}>🗂️</Typography>
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>Sections</Typography>
            </Box>
            <IconButton size="small" color="primary" onClick={handleAddSectionClick}>
              <AddIcon />
            </IconButton>
          </Box>
          {/* Sections List */}
          <Box sx={{ minHeight: 168, maxHeight: 200, overflowY: 'auto', p: 2, pt: 0, flexShrink: 0 }}>
            <List>
              {sections.map((section) => (
                <ListItem 
                  key={section.section_id}
                  button
                  selected={selectedSection === section.section_id}
                  onClick={() => onSectionSelect(section.section_id)}
                  secondaryAction={
                    <Box>
                      <IconButton size="small" onClick={e => { e.stopPropagation(); handleRenameClick(section.id, section.name, section.glyph); }}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={e => { e.stopPropagation(); handleDeleteClick(section.id); }}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  }
                >
                  <ListItemText 
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="h6" component="span">{section.glyph || '🌱'}</Typography>
                        <Typography>{section.name}</Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>

          {/* Add Section Dialog */}
          <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)}>
            <DialogTitle>Add Section</DialogTitle>
            <DialogContent>
              <TextField
                autoFocus
                margin="dense"
                label="Section Name"
                fullWidth
                value={newSectionName}
                onChange={e => setNewSectionName(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') handleAddSectionConfirm(); }}
              />
              <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>Choose a symbol for this section:</Typography>
              <Grid container spacing={1} sx={{ maxHeight: '200px', overflowY: 'auto' }}>
                {GARDEN_EMOJIS.map((emoji) => (
                  <Grid item key={emoji}>
                    <IconButton
                      onClick={() => setSelectedGlyph(emoji)}
                      sx={{
                        bgcolor: selectedGlyph === emoji ? 'primary.main' : 'transparent',
                        color: selectedGlyph === emoji ? 'white' : 'inherit',
                        '&:hover': {
                          bgcolor: selectedGlyph === emoji ? 'primary.dark' : 'action.hover',
                        },
                      }}
                    >
                      {emoji}
                    </IconButton>
                  </Grid>
                ))}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleAddSectionConfirm} variant="contained">Add</Button>
            </DialogActions>
          </Dialog>

          {/* Rename Section Dialog */}
          <Dialog open={renameDialogOpen} onClose={() => setRenameDialogOpen(false)}>
            <DialogTitle>Edit Section</DialogTitle>
            <DialogContent>
              <TextField
                autoFocus
                margin="dense"
                label="Section Name"
                fullWidth
                value={renameSectionName}
                onChange={e => setRenameSectionName(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') handleRenameConfirm(); }}
              />
              <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>Choose a symbol for this section:</Typography>
              <Grid container spacing={1} sx={{ maxHeight: '200px', overflowY: 'auto' }}>
                {GARDEN_EMOJIS.map((emoji) => (
                  <Grid item key={emoji}>
                    <IconButton
                      onClick={() => setSelectedGlyph(emoji)}
                      sx={{
                        bgcolor: selectedGlyph === emoji ? 'primary.main' : 'transparent',
                        color: selectedGlyph === emoji ? 'white' : 'inherit',
                        '&:hover': {
                          bgcolor: selectedGlyph === emoji ? 'primary.dark' : 'action.hover',
                        },
                      }}
                    >
                      {emoji}
                    </IconButton>
                  </Grid>
                ))}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setRenameDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleRenameConfirm} variant="contained">Save</Button>
            </DialogActions>
          </Dialog>

          {/* Delete Section Dialog */}
          <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
            <DialogTitle>Delete Section</DialogTitle>
            <DialogContent>
              <Typography>Are you sure you want to delete this section? All plants in this section will be unassigned.</Typography>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleDeleteConfirm} color="error" variant="contained">Delete</Button>
            </DialogActions>
          </Dialog>
        </Paper>

        {/* Middle Column */}
        <Paper elevation={2} sx={{ bgcolor: 'background.paper', borderRadius: 3, boxShadow: 2, p: 0, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', bgcolor: '#f5f5f5', borderBottom: '1px solid #e0e0e0', p: 1, minHeight: 38, gap: 1.5, justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Typography component="span" sx={{ fontSize: 28, mr: 1 }}>💧</Typography>
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>Watering Schedule</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Button
                variant={!isNextWeek ? "contained" : "text"}
                size="small"
                onClick={() => setIsNextWeek(false)}
                sx={{
                  borderRadius: 1.5,
                  textTransform: 'none',
                  minWidth: 100,
                  transition: 'all 0.2s ease',
                  ...(!isNextWeek && {
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                    boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #1976D2 30%, #1CB5E0 90%)',
                    }
                  })
                }}
              >
                This Week
              </Button>
              <Button
                variant={isNextWeek ? "contained" : "text"}
                size="small"
                onClick={() => setIsNextWeek(true)}
                sx={{
                  borderRadius: 1.5,
                  textTransform: 'none',
                  minWidth: 100,
                  transition: 'all 0.2s ease',
                  ...(isNextWeek && {
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                    boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #1976D2 30%, #1CB5E0 90%)',
                    }
                  })
                }}
              >
                Next Week
              </Button>
            </Box>
          </Box>
          {/* Watering Schedule - Fixed height */}
          <Box sx={{ height: '400px' }}>
            <WateringSchedule 
              sectionId={selectedSection ? parseInt(selectedSection) : undefined} 
              sections={sections} 
              isNextWeek={isNextWeek}
              setIsNextWeek={setIsNextWeek}
            />
          </Box>
          
          {/* Selected Section Plants - Scrollable area with unified header, moved up */}
          <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', mt: -4.5 }}>
            {/* Unified Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', bgcolor: '#f5f5f5', borderBottom: '1px solid #e0e0e0', p: 1, minHeight: 38, gap: 1.5 }}>
              {selectedSection ? (
                <>
                  <Typography component="span" sx={{ fontSize: 28, mr: 1 }}>
                    {sections.find(s => s.section_id === selectedSection)?.glyph || '🪴'}
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                    {sections.find(s => s.section_id === selectedSection)?.name || selectedSection} Plants
                  </Typography>
                </>
              ) : (
                <>
                  <Typography component="span" sx={{ fontSize: 28, mr: 1 }}>🪴</Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                    Select a Section
                  </Typography>
                </>
              )}
            </Box>
            {/* Scrollable Content */}
            <Box sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
              {selectedSection ? (
                <Droppable droppableId={selectedSection?.toString() || ''}>
                  {(provided: DroppableProvided, snapshot: DroppableStateSnapshot): JSX.Element => (
                    <Box
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      sx={{
                        flex: 1,
                        minHeight: '200px',
                        bgcolor: snapshot.isDraggingOver ? 'action.hover' : 'background.default',
                        border: '2px dashed',
                        borderColor: snapshot.isDraggingOver ? 'primary.main' : 'grey.300',
                        borderRadius: 1,
                        m: 2,
                        p: 0
                      }}
                    >
                      {plantsInSection.length > 0 ? (
                        <PlantGrid
                          plants={plantsInSection}
                          onPlantClick={onPlantClick}
                        />
                      ) : (
                        <Box
                          sx={{
                            flex: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'text.secondary',
                            fontSize: '0.875rem',
                            minHeight: 180
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
          </Box>
        </Paper>

        {/* Right Column */}
        <Paper elevation={2} sx={{ bgcolor: 'background.paper', borderRadius: 3, boxShadow: 2, p: 0, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
          {/* Pruning Schedule Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', bgcolor: '#f5f5f5', borderBottom: '1px solid #e0e0e0', p: 2, minHeight: 56, gap: 1.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Typography component="span" sx={{ fontSize: 28, mr: 1 }}>✂️</Typography>
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>Pruning Schedule</Typography>
            </Box>
            <Select
              value={sectionFilter}
              onChange={e => setSectionFilter(e.target.value)}
              displayEmpty
              size="small"
              sx={{ 
                minWidth: 160,
                bgcolor: 'rgba(255,255,255,0.9)',
                borderRadius: 1,
                '& .MuiSelect-select': {
                  py: 1
                },
                '&:hover': {
                  bgcolor: 'white'
                }
              }}
            >
              <MenuItem value="">All Plants</MenuItem>
              {sections.map(section => (
                <MenuItem key={section.section_id} value={section.section_id}>{section.name}</MenuItem>
              ))}
            </Select>
          </Box>
          <PruningSchedule 
            selectedSection={selectedSection} 
            userPlants={plants} 
            sections={sections}
            onPlantClick={onPlantClick}
            sectionFilter={sectionFilter}
            setSectionFilter={setSectionFilter}
          />
          {/* Plant Inspiration Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', bgcolor: '#f5f5f5', borderBottom: '1px solid #e0e0e0', p: 2, minHeight: 56, gap: 1.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Typography component="span" sx={{ fontSize: 24, mr: 1 }}>🌱</Typography>
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>Plant Inspiration</Typography>
            </Box>
            <Badge badgeContent={activeFilterCount} color="primary">
              <Button
                variant="outlined"
                onClick={() => setIsFilterOpen(true)}
                startIcon={<FilterListIcon />}
                size="small"
              >
                Filters
              </Button>
            </Badge>
          </Box>
          <PlantSuggestions 
            selectedSection={selectedSection}
            isFilterOpen={isFilterOpen}
            setIsFilterOpen={setIsFilterOpen}
            activeFilterCount={activeFilterCount}
          />
        </Paper>
      </DragDropContext>
    </Box>
  );
}; 