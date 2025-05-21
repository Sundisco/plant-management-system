import React from 'react';
import { Box, Typography, IconButton, TextField, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import { DragDropContext, Droppable, DropResult } from '@hello-pangea/dnd';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { Plant } from '../../types/Plant';
import { Section } from '../../types/Section';
import { PlantList } from './PlantList';
import { fetchSections, createSection, renameSection, deleteSection } from '../../utils/sectionsApi';

interface SectionViewProps {
  sections: Section[];
  plants: Plant[];
  plantsByType: { [key: string]: Plant[] };
  plantIndexMap: Map<number, number>;
  expandedTypes: { [key: string]: boolean };
  onToggleType: (type: string) => void;
  onPlantClick: (plant: Plant) => void;
  onRemovePlant: (plantId: number) => void;
  onSectionUpdate: (updatedSections: Section[]) => void;
}

export const SectionView: React.FC<SectionViewProps> = ({
  sections,
  plants,
  plantsByType,
  plantIndexMap,
  expandedTypes,
  onToggleType,
  onPlantClick,
  onRemovePlant,
  onSectionUpdate,
}) => {
  const [editingSection, setEditingSection] = React.useState<Section | null>(null);
  const [newName, setNewName] = React.useState('');

  const handleDragEnd = async (result: DropResult) => {
    const { source, destination } = result;

    if (!destination) return;

    const sourceId = source.droppableId;
    const destId = destination.droppableId;

    // Don't allow dropping into type sections
    if (destId.startsWith('type-')) return;

    // Find the plant being moved
    const plantId = parseInt(result.draggableId.replace('plant-', ''));
    const plant = plants.find(p => p.id === plantId);
    if (!plant) return;

    // Update the plant's section
    const updatedPlant = { ...plant, section: destId };
    
    try {
      // Update the plant in the backend
      const response = await fetch(`/api/plants/user/${plant.user_id}/plants/${plantId}/section`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ section: destId }),
      });

      if (!response.ok) {
        throw new Error('Failed to update plant section');
      }

      // Update the plant in the local state
      const updatedPlants = plants.map(p => 
        p.id === plantId ? updatedPlant : p
      );

      // Force a re-render of the droppable areas
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
      }, 0);
    } catch (error) {
      console.error('Error updating plant section:', error);
    }
  };

  const handleEditClick = (section: Section) => {
    setEditingSection(section);
    setNewName(section.name);
  };

  const handleDeleteClick = async (sectionId: number) => {
    try {
      await deleteSection(sectionId);
      const updatedSections = sections.filter(s => s.id !== sectionId);
      onSectionUpdate(updatedSections);
    } catch (error) {
      console.error('Error deleting section:', error);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingSection) return;

    try {
      const response = await renameSection(editingSection.id, newName, editingSection.glyph);
      if (response.data) {
        const updatedSections = sections.map(s => 
          s.id === editingSection.id ? response.data as Section : s
        );
        onSectionUpdate(updatedSections);
        setEditingSection(null);
      }
    } catch (error) {
      console.error('Error updating section:', error);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        p: 2,
        borderBottom: '1px solid',
        borderColor: 'divider'
      }}>
        <Typography variant="h6">Current Garden</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {sections.map(section => (
            <Box key={section.id} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="subtitle1">{section.name}</Typography>
              <IconButton size="small" onClick={() => handleEditClick(section)}>
                <EditIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={() => handleDeleteClick(section.id)}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Box>
          ))}
        </Box>
      </Box>

      <DragDropContext onDragEnd={handleDragEnd}>
        <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          {/* Left column - Unassigned plants grouped by type */}
          <Box sx={{ 
            width: '33%', 
            p: 2, 
            borderRight: '1px solid',
            borderColor: 'divider',
            overflowY: 'auto'
          }}>
            <Typography variant="h6" sx={{ mb: 2 }}>Unassigned Plants</Typography>
            <PlantList
              plants={plants}
              plantsByType={plantsByType}
              plantIndexMap={plantIndexMap}
              expandedTypes={expandedTypes}
              onToggleType={onToggleType}
              onPlantClick={onPlantClick}
              onRemovePlant={onRemovePlant}
              droppableId="unassigned"
              sections={sections}
            />
          </Box>

          {/* Middle column - Section plants */}
          <Box sx={{ 
            width: '33%', 
            p: 2, 
            borderRight: '1px solid',
            borderColor: 'divider',
            overflowY: 'auto'
          }}>
            {sections.map(section => (
              <Box key={section.id} sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>{section.name}</Typography>
                <PlantList
                  plants={plants.filter(p => p.section === section.section_id)}
                  plantsByType={plantsByType}
                  plantIndexMap={plantIndexMap}
                  expandedTypes={expandedTypes}
                  onToggleType={onToggleType}
                  onPlantClick={onPlantClick}
                  onRemovePlant={onRemovePlant}
                  droppableId={section.section_id}
                  sections={sections}
                />
              </Box>
            ))}
          </Box>

          {/* Right column - Plant details */}
          <Box sx={{ 
            width: '33%', 
            p: 2,
            overflowY: 'auto'
          }}>
            <Typography variant="h6" sx={{ mb: 2 }}>Plant Details</Typography>
            {/* Plant details content will go here */}
          </Box>
        </Box>
      </DragDropContext>

      {/* Edit Section Dialog */}
      <Dialog open={!!editingSection} onClose={() => setEditingSection(null)}>
        <DialogTitle>Edit Section</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Section Name"
            fullWidth
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingSection(null)}>Cancel</Button>
          <Button onClick={handleSaveEdit} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}; 