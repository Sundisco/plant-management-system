const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  PLANTS: `${baseUrl}/api/plants`,
  PLANTS_SEARCH: `${baseUrl}/api/plants/search`,
  USER_PLANTS: (userId: number) => `${baseUrl}/api/plants/user/${userId}/plants`,
  ADD_PLANT: (userId: number, plantId: number) => `${baseUrl}/api/plants/user/${userId}/plants/${plantId}`,
  PLANT_SECTION: (userId: number, plantId: number) => `${baseUrl}/api/plants/user/${userId}/plants/${plantId}/section`,
  WATERING_SCHEDULE: (userId: number) => `${baseUrl}/api/${userId}`,
  PRUNING: (userId: number) => `${baseUrl}/api/pruning/schedule/${userId}`,
  WEATHER: `${baseUrl}/api/weather`,
}; 