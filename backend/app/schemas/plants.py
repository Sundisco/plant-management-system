# /backend/app/schemas/plants.py
from pydantic import BaseModel, field_validator
from typing import List, Optional
from app.schemas.base import BaseSchema
from datetime import datetime
from pydantic import field_serializer

class PlantBase(BaseSchema):
    common_name: str
    scientific_name: List[str]
    other_names: Optional[List[str]] = None
    family: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    growth_rate: Optional[str] = None
    maintenance: Optional[str] = None
    hardiness_zone: Optional[str] = None
    image_url: Optional[str] = None
    cycle: Optional[str] = None
    watering: Optional[str] = None
    is_evergreen: bool = False
    edible_fruit: bool = False

    class Config:
        from_attributes = True

class PlantCreate(PlantBase):
    pass

class Plant(BaseModel):
    id: int
    common_name: str
    scientific_name: List[str]
    other_names: List[str]
    family: Optional[str] = None
    type: Optional[str] = None
    cycle: Optional[str] = None
    watering: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    is_evergreen: Optional[bool] = None
    growth_rate: Optional[str] = None
    maintenance: Optional[str] = None
    hardiness_zone: Optional[str] = None
    edible_fruit: Optional[bool] = None
    section: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    attracts: Optional[List[str]] = None
    sunlight: Optional[List[str]] = None

    @property
    def attracts(self):
        # Use attracts_names if available
        if hasattr(self, 'attracts_names'):
            return list(self.attracts_names)
        return []

    class Config:
        from_attributes = True

# Use Plant as PlantResponse since they're the same
PlantResponse = Plant

# Add these new classes for search functionality
class PlantSearch(BaseModel):
    query: Optional[str] = None
    plant_type: Optional[str] = None

class SearchResponse(BaseModel):
    items: List[Plant]
    total: int
    offset: int = 0
    limit: int = 10
