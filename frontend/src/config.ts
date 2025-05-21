// API Configuration
const isDevelopment = import.meta.env.DEV;
const baseUrl = 'https://7983-89-150-165-205.ngrok-free.app';  // Using ngrok URL for both development and production

// API Endpoints
export const API_ENDPOINTS = {
  BASE_URL: baseUrl, // Use the same baseUrl as defined above
  PLANTS: '/api/plants',
  PLANTS_SEARCH: '/api/plants/search',
  USER_PLANTS: (userId: number) => `/api/plants/user/${userId}/plants`,
  ADD_PLANT: (userId: number) => `/api/plants/user/${userId}/plants`,
  PLANT_SECTION: (userId: number, plantId: number) => `/api/plants/user/${userId}/plants/${plantId}/section`,
  WATERING_SCHEDULE: (userId: number) => `/api/watering-schedule/watering-schedule/user/${userId}`,
  PRUNING: (userId: number) => `/api/pruning/schedule/${userId}`,
  PLANT_SUGGESTIONS: (sectionId: string) => `/suggestions/${sectionId}`,
  WEATHER: `${baseUrl}/api/weather`,
  SECTIONS: (userId: number) => `/api/sections/${userId}`,
  CREATE_SECTION: (userId: number) => `/api/sections/${userId}`,
  UPDATE_SECTION: (userId: number, sectionId: number) => `/api/sections/${userId}/${sectionId}`,
  DELETE_SECTION: (userId: number, sectionId: number) => `/api/sections/${userId}/${sectionId}`,
};

// API Error Messages
export const API_ERRORS = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  NOT_FOUND: 'Resource not found.',
  UNAUTHORIZED: 'Please log in to continue.',
  FORBIDDEN: 'You do not have permission to perform this action.',
};

// API Timeouts
export const API_TIMEOUTS = {
  DEFAULT: 10000,  // 10 seconds
  SEARCH: 5000,    // 5 seconds
  UPLOAD: 30000,   // 30 seconds
}; 