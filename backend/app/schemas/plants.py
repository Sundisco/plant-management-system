# /backend/app/schemas/plants.py
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.base import BaseSchema

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
    family: Optional[str]
    type: Optional[str]
    cycle: Optional[str]
    watering: Optional[str]
    image_url: Optional[str]
    description: Optional[str]
    is_evergreen: Optional[bool]
    growth_rate: Optional[str]
    maintenance: Optional[str]
    hardiness_zone: Optional[str]
    edible_fruit: Optional[bool]
    section: Optional[str]
    attracts: Optional[List[str]] = []
    sunlight: Optional[List[str]] = []

    class Config:
        orm_mode = True

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
