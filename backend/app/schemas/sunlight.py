from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum
from app.schemas.plants import Plant

class SunlightCondition(str, Enum):
    FULL_SUN = "full sun"
    PART_SHADE = "part shade"
    FILTERED_SHADE = "filtered shade"
    SHADE = "shade"
    UNKNOWN = "Unknown"

class SunlightBase(BaseModel):
    plant_id: int
    condition: SunlightCondition = SunlightCondition.UNKNOWN

class SunlightCreate(SunlightBase):
    pass

class Sunlight(SunlightBase):
    id: int
    plant: Optional[Plant] = None
    
    model_config = ConfigDict(from_attributes=True)
