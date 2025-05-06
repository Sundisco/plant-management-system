export interface Plant {
  id: number;
  common_name: string;
  scientific_name: string[];
  other_names: string[];
  type: string;
  image_url: string;
  section: string | null;
  in_user_garden: boolean;
  description?: string;
  growth_rate?: string;
  maintenance?: string;
  hardiness_zone?: string;
  cycle?: string;
  watering?: string;
  is_evergreen?: boolean;
  edible_fruit?: boolean;
  attracts?: string[];
  sunlight?: string[];
} 