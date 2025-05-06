from pydantic import BaseModel, ConfigDict, constr
from typing import Optional, List
from app.schemas.plants import Plant

class AttractsBase(BaseModel):
    plant_id: int
    species: constr(min_length=1)  # Ensures non-empty string

class AttractsCreate(AttractsBase):
    pass

class Attracts(AttractsBase):
    id: int
    plant: Optional[Plant] = None
    
    model_config = ConfigDict(from_attributes=True)

# Additional schema for returning multiple species for a plant
class PlantAttracts(BaseModel):
    plant_id: int
    species_list: List[str]
