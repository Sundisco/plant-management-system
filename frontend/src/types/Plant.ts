export interface Plant {
  id: number;
  common_name: string;
  scientific_name?: string[];
  other_names?: string[];
  description?: string;
  type: string;
  is_evergreen?: boolean;
  edible_fruit?: boolean;
  image_url?: string;
  sunlight?: string[];
  watering?: string;
  hardiness_zone?: string;
  growth_rate?: string;
  maintenance?: string;
  cycle?: string;
  attracts?: string[];
  section?: string;
  last_watered?: string;
  next_watering?: string;
  in_user_garden: boolean;
  user_id: number;
}

export interface WateringSchedule {
  [date: string]: number;
} 