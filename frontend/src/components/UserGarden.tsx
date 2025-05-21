import React, { useState, useEffect } from 'react';
import { Card, Grid, Button, Typography, Box } from '@mui/material';
import { Plant } from '../types/Plant';
import { API_ENDPOINTS } from '../config';

interface UserGardenProps {
  userId: number;
}

export const UserGarden: React.FC<UserGardenProps> = ({ userId }) => {
  const [userPlants, setUserPlants] = useState<Plant[]>([]);

  useEffect(() => {
    fetchUserPlants();
  }, [userId]);

  const fetchUserPlants = async () => {
    try {
      const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.USER_PLANTS(userId)}`);
      const data = await response.json();
      setUserPlants(data);
    } catch (error) {
      console.error('Error fetching user plants:', error);
    }
  };

  const removePlant = async (plantId: number) => {
    try {
      await fetch(API_ENDPOINTS.ADD_PLANT(userId), {
        method: 'DELETE',
      });
      fetchUserPlants(); // Refresh the list
    } catch (error) {
      console.error('Error removing plant:', error);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" sx={{ mb: 2 }}>Your Garden</Typography>
      <Grid container spacing={2}>
        {userPlants.map((plant) => (
          <Grid item xs={12} sm={6} md={4} key={plant.id}>
            <Card sx={{ p: 2 }}>
              <img 
                src={plant.image_url} 
                alt={plant.common_name} 
                style={{ width: '100%', height: '200px', objectFit: 'cover' }}
              />
              <Typography variant="h6" sx={{ mt: 1 }}>{plant.common_name}</Typography>
              <Button 
                variant="contained" 
                color="error" 
                onClick={() => removePlant(plant.id)}
                sx={{ mt: 1 }}
              >
                Remove
              </Button>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}; 