export interface Plant {
  id: number;
  common_name: string;
  scientific_name: string[];
  other_names: string[];
  family?: string;
  type: string;
  description?: string;
  growth_rate?: string;
  maintenance?: string;
  hardiness_zone?: string;
  image_url: string;
  cycle?: string;
  watering?: string;
  is_evergreen: boolean;
  edible_fruit: boolean;
  section: string | null;
  in_user_garden: boolean;
  attracts?: string[];
  sunlight?: string[];
} 