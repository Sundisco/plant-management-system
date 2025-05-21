import { api } from './api';
import { API_ENDPOINTS } from '../config';

export const fetchSections = async (userId: number) => {
  return api.get(`${API_ENDPOINTS.BASE_URL}/api/sections?user_id=${userId}`);
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