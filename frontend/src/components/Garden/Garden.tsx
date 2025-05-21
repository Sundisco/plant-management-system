import React, { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { DragDropContext, DropResult } from '@hello-pangea/dnd';
import { PlantSearch } from '../PlantSearch';
import { PlantList } from './PlantList';
import { GardenLayout } from './GardenLayout';
import { PlantDetails } from './PlantDetails';
import { Plant } from '../../types/Plant';
import { API_ENDPOINTS } from '../../config';
import { useAuth } from '../../contexts/AuthContext';
import * as sectionsApi from '../../utils/sectionsApi';
import WateringSchedule from '../WateringSchedule';
import { useGarden } from '../../contexts/GardenContext';

interface Section {
  id: number;
  section_id: string;
  name: string;
  glyph: string;
  user_id: number;
  created_at?: string;
  updated_at?: string;
}

interface GardenProps {
  userId?: number;
}

export function Garden({ userId = 1 }: GardenProps) {
  const { user } = useAuth();
  const { plants, setPlants, refreshPlants } = useGarden();
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [expandedTypes, setExpandedTypes] = useState<{ [key: string]: boolean }>({});
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sections, setSections] = useState<Section[]>([]);
  const [loadingSections, setLoadingSections] = useState(true);

  const GARDEN_DROPPABLE_ID = 'garden';
  const UNASSIGNED_DROPPABLE_ID = 'unassigned';

  const plantsInSection = plants.filter(plant => plant.section === selectedSection);

  // Initial load of plants
  useEffect(() => {
    refreshPlants();
  }, [refreshPlants]);

  useEffect(() => {
    const loadSections = async () => {
      setLoadingSections(true);
      const res = await sectionsApi.fetchSections(userId);
      if (res.data && Array.isArray(res.data)) setSections(res.data as Section[]);
      setLoadingSections(false);
    };
    loadSections();
  }, [userId]);

  useEffect(() => {
    if (!loadingSections && !loading) {
      console.log('Sections:', sections.map(s => ({ id: s.id, section_id: s.section_id, name: s.name })));
      console.log('Plants:', plants.map(p => ({ id: p.id, section: p.section, name: p.common_name })));
    }
  }, [sections, plants, loadingSections, loading]);

  const handleRemovePlant = async (plantId: number) => {
    try {
      const actualUserId = userId || user?.id;
      if (!actualUserId) {
        setError('User not authenticated');
        return;
      }

      const response = await fetch(`${API_ENDPOINTS.USER_PLANTS(actualUserId)}/${plantId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        const updatedPlants = plants.filter(p => p.id !== plantId);
        setPlants(updatedPlants);
      } else {
        throw new Error('Failed to remove plant');
      }
    } catch (error) {
      console.error('Error removing plant:', error);
      setError(error instanceof Error ? error.message : 'Failed to remove plant');
    }
  };

  const handlePlantAdded = (newPlant: Plant) => {
    const existingPlant = plants.find(p => p.id === newPlant.id);
    if (existingPlant) {
      const updatedPlants = plants.map(p => 
        p.id === newPlant.id 
          ? { ...newPlant, section: existingPlant.section }
          : p
      ) as Plant[];
      setPlants(updatedPlants);
    } else {
      const updatedPlants = [...plants, {
        ...newPlant,
        section: null,
        image_url: newPlant.image_url || '',
        scientific_name: newPlant.scientific_name || [],
        other_names: newPlant.other_names || [],
        type: newPlant.type || ''
      }] as Plant[];
      setPlants(updatedPlants);
    }
  };

  const handleDragEnd = async (result: DropResult) => {
    document.body.style.overflow = 'auto';

    const { source, destination, draggableId } = result;
    
    if (!destination) return;

    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    ) return;

    const validSectionIds = sections.map(s => s.section_id);
    if (
      destination.droppableId !== UNASSIGNED_DROPPABLE_ID &&
      !validSectionIds.includes(destination.droppableId)
    ) {
      alert('You can only assign plants to sections.');
      return;
    }

    console.log('Drag event:', {
      sourceDroppableId: source.droppableId,
      destinationDroppableId: destination.droppableId,
      draggableId
    });

    const plantId = parseInt(draggableId.split('-')[1]);
    const newSection = destination.droppableId === UNASSIGNED_DROPPABLE_ID ? null : destination.droppableId;

    const draggedPlant = plants.find(p => p.id === plantId);
    if (draggedPlant) {
      // Section-based DnD logic here
    }

    console.log('Assigning plant', plantId, 'to section', newSection);

    const actualUserId = userId || user?.id;
    if (!actualUserId) {
      console.error('User not authenticated');
      return;
    }

    console.log('Updating plant section:', {
      url: `${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.PLANT_SECTION(actualUserId, plantId)}`,
      payload: { section: newSection }
    });

    try {
      const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.PLANT_SECTION(actualUserId, plantId)}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ section: newSection }),
      });

      if (!response.ok) {
        alert(`Failed to update section: ${response.statusText}`);
        throw new Error(`Failed to update section: ${response.statusText}`);
      }

      setTimeout(() => {
        const updatedPlants = plants.map((p: Plant) => 
          p.id === plantId ? { ...p, section: newSection } : p
        );
        setPlants(updatedPlants);
      }, 100);
    } catch (error) {
      console.error('Error updating section:', error);
      setError(error instanceof Error ? error.message : 'Failed to update section');
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
    setDetailsOpen(false);
  };

  // Section management handlers
  const handleAddSection = async (name: string, glyph: string) => {
    // Generate next section_id (e.g., "A", "B", ...)
    // Find the highest existing section_id and increment it
    const existingIds = sections.map(s => s.section_id.charCodeAt(0));
    const nextId = String.fromCharCode(Math.max(...existingIds, 64) + 1);
    
    const res = await sectionsApi.createSection(userId, nextId, name, glyph);
    if (res.data && typeof res.data === 'object' && 'id' in res.data) {
      setSections((prev: Section[]) => {
        const newSections = [...prev, res.data as Section];
        return newSections;
      });
    }
  };

  const handleRenameSection = async (id: number, name: string, glyph: string) => {
    const res = await sectionsApi.renameSection(id, name, glyph);
    if (res.data && typeof res.data === 'object' && 'id' in res.data) {
      setSections((prev: Section[]) => prev.map(s => s.id === (res.data as Section).id ? res.data as Section : s));
    }
  };

  const handleDeleteSection = async (id: number) => {
    const deletedSection = sections.find(s => s.id === id);
    if (!deletedSection) return;

    try {
      // First, unassign all plants from this section in the backend
      const plantsToUnassign = plants.filter(p => p.section === deletedSection.section_id);
      const actualUserId = userId || user?.id;
      if (!actualUserId) {
        setError('User not authenticated');
        return;
      }

      // Update each plant's section to null in the backend
      await Promise.all(plantsToUnassign.map(async (plant) => {
        const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.PLANT_SECTION(actualUserId, plant.id)}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ section: null }),
        });
        if (!response.ok) {
          throw new Error(`Failed to unassign plant ${plant.id}`);
        }
      }));

      // Then delete the section
      await sectionsApi.deleteSection(id);

      // Update local state
      setSections((prev: Section[]) => prev.filter(s => s.id !== id));
      const updatedPlants = plants.map((p: Plant) => p.section === deletedSection.section_id ? { ...p, section: null } : p);
      setPlants(updatedPlants);
      if (selectedSection === deletedSection.section_id) setSelectedSection(null);
    } catch (error) {
      console.error('Error deleting section:', error);
      setError(error instanceof Error ? error.message : 'Failed to delete section');
    }
  };

  if (loadingSections) {
    return <div>Loading sections...</div>;
  }

  return (
    <>
      <DragDropContext onDragEnd={handleDragEnd}>
        <GardenLayout
          plants={plants}
          plantsByType={plantsByType}
          plantIndexMap={new Map()}
          expandedTypes={expandedTypes}
          selectedSection={selectedSection}
          onToggleType={toggleTypeExpansion}
          onPlantClick={handlePlantClick}
          onRemovePlant={handleRemovePlant}
          onDragEnd={handleDragEnd}
          onPlantAdded={handlePlantAdded}
          onSectionSelect={setSelectedSection}
          sections={sections}
          onAddSection={handleAddSection}
          onRenameSection={handleRenameSection}
          onDeleteSection={(id) => handleDeleteSection(id)}
        />
      </DragDropContext>
      <PlantDetails
        plant={selectedPlant}
        open={detailsOpen}
        onClose={handleClosePlantDetails}
        sections={sections}
      />
    </>
  );
} 