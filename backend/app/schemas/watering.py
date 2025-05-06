from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from enum import Enum
from app.schemas.plants import Plant

class WateringPeriod(str, Enum):
    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"
    ANYTIME = "anytime"

class WateringBase(BaseModel):
    plant_id: int
    frequency_days: int = Field(gt=0)
    depth_mm: int = Field(gt=0)
    volume_feet: float = Field(gt=0)
    period: WateringPeriod
    drought_tolerant: bool = False
    soil: List[str]

class WateringCreate(WateringBase):
    pass

class Watering(WateringBase):
    id: int
    plant: Optional[Plant] = None
    
    model_config = ConfigDict(from_attributes=True)
