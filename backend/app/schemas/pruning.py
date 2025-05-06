from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from app.schemas.plants import Plant

class PruningBase(BaseModel):
    plant_id: int
    frequency: int = Field(gt=0)
    months: List[str]
    interval: str = "Unknown"

class PruningCreate(PruningBase):
    pass

class Pruning(PruningBase):
    id: int
    plant: Optional[Plant] = None
    
    model_config = ConfigDict(from_attributes=True)
