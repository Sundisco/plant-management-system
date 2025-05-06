import React, { useState, useEffect } from 'react';
import { Card, Grid, Button } from '@your-ui-library';

export const UserGarden: React.FC = () => {
  const [userPlants, setUserPlants] = useState<Plant[]>([]);

  useEffect(() => {
    fetchUserPlants();
  }, []);

  const fetchUserPlants = async () => {
    try {
      const response = await fetch(`/api/plants/user/${userId}/plants`);
      const data = await response.json();
      setUserPlants(data);
    } catch (error) {
      console.error('Error fetching user plants:', error);
    }
  };

  const removePlant = async (plantId: number) => {
    try {
      await fetch(`/api/plants/user/${userId}/plants/${plantId}`, {
        method: 'DELETE',
      });
      fetchUserPlants(); // Refresh the list
    } catch (error) {
      console.error('Error removing plant:', error);
    }
  };

  return (
    <div className="user-garden">
      <h2>Your Garden</h2>
      <Grid>
        {userPlants.map((plant) => (
          <Card key={plant.id}>
            <img src={plant.image_url} alt={plant.common_name} />
            <h3>{plant.common_name}</h3>
            <Button onClick={() => removePlant(plant.id)}>
              Remove
            </Button>
          </Card>
        ))}
      </Grid>
    </div>
  );
}; 