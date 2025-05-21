import { Section } from './Section';

export interface WateringSchedule {
  [key: string]: {
    date: string;
    plants: {
      id: number;
      name: string;
      section: string | null;
    }[];
  };
}

export interface WateringScheduleProps {
  sectionId?: number;
  sections: Section[];
  isNextWeek: boolean;
  setIsNextWeek: (value: boolean) => void;
}

export interface WateringEvent {
  id: number;
  plant_id: number;
  date: string;
  completed: boolean;
  notes?: string;
} 