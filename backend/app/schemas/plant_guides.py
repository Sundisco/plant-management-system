# /backend/app/schemas/plant_guides.py
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional
from app.schemas.plants import Plant  # Fix the import path

class GuideType(str, Enum):
    SUNLIGHT = "sunlight"
    WATERING = "watering"
    PRUNING = "pruning"
    OTHER = "Other"

class PlantGuideBase(BaseModel):
    plant_id: int
    type: GuideType
    description: str

class PlantGuideCreate(PlantGuideBase):
    pass

class PlantGuide(PlantGuideBase):
    id: int
    plant: Plant  # Include the plant details (nested schema)
    
    model_config = ConfigDict(from_attributes=True)
