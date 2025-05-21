import { api } from './api';
import { API_ENDPOINTS } from '../config';

export const fetchSections = async (userId: number) => {
  console.log('Fetching sections for user:', userId);
  console.log('Sections API URL:', `${API_ENDPOINTS.BASE_URL}/api/sections?user_id=${userId}`);
  const response = await api.get(`${API_ENDPOINTS.BASE_URL}/api/sections?user_id=${userId}`);
  console.log('Sections response:', response);
  return response;
};

export const createSection = async (userId: number, section_id: string, name: string, glyph: string) => {
  return api.post(`${API_ENDPOINTS.BASE_URL}/api/sections?user_id=${userId}`, { 
    section_id,
    name,
    glyph
  });
};

export const renameSection = async (sectionId: number, name: string, glyph: string) => {
  return api.put(`${API_ENDPOINTS.BASE_URL}/api/sections/${sectionId}`, { 
    name,
    glyph
  });
};

export const deleteSection = async (sectionId: number) => {
  return api.delete(`${API_ENDPOINTS.BASE_URL}/api/sections/${sectionId}`);
}; 