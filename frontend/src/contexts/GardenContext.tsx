import React, { createContext, useContext, useState, useCallback } from 'react';
import { Plant } from '../types/Plant';
import { API_ENDPOINTS } from '../config';

interface GardenContextType {
  plants: Plant[];
  setPlants: (plants: Plant[]) => void;
  refreshPlants: () => Promise<void>;
  lastUpdated: Date | null;
  searchResults: Plant[];
  setSearchResults: (plants: Plant[]) => void;
  clearSearch: () => void;
}

const GardenContext = createContext<GardenContextType | undefined>(undefined);

export const GardenProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [searchResults, setSearchResults] = useState<Plant[]>([]);

  const refreshPlants = useCallback(async () => {
    try {
      const response = await fetch(`${API_ENDPOINTS.USER_PLANTS(1)}?limit=50`);
      if (!response.ok) {
        throw new Error('Failed to fetch plants');
      }
      const data = await response.json();
      setPlants(data);
      setLastUpdated(new Date());
      
      // Clear search results when garden is refreshed
      setSearchResults([]);
    } catch (error) {
      console.error('Error refreshing plants:', error);
    }
  }, []);

  // Add a function to update plants and lastUpdated
  const updatePlants = useCallback((newPlants: Plant[]) => {
    setPlants(newPlants);
    setLastUpdated(new Date());
  }, []);

  const clearSearch = useCallback(() => {
    setSearchResults([]);
  }, []);

  return (
    <GardenContext.Provider value={{ 
      plants, 
      setPlants: updatePlants, // Use the new updatePlants function instead of setPlants
      refreshPlants, 
      lastUpdated,
      searchResults,
      setSearchResults,
      clearSearch
    }}>
      {children}
    </GardenContext.Provider>
  );
};

export const useGarden = () => {
  const context = useContext(GardenContext);
  if (context === undefined) {
    throw new Error('useGarden must be used within a GardenProvider');
  }
  return context;
}; 