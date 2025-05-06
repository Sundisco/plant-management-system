from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.services import attracts as attracts_service
from app.schemas.attracts import Attracts, AttractsCreate, PlantAttracts
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=Attracts)
def create_attracts(attracts: AttractsCreate, db: Session = Depends(get_db)):
    return attracts_service.create_attracts(db, attracts)

@router.get("/{attracts_id}", response_model=Attracts)
def read_attracts(attracts_id: int, db: Session = Depends(get_db)):
    db_attracts = attracts_service.get_attracts(db, attracts_id)
    if db_attracts is None:
        raise HTTPException(status_code=404, detail="Attracts entry not found")
    return db_attracts

@router.get("/plant/{plant_id}", response_model=List[Attracts])
def read_plant_attracts(plant_id: int, db: Session = Depends(get_db)):
    return attracts_service.get_plant_attracts(db, plant_id)

@router.get("/plant/{plant_id}/species", response_model=PlantAttracts)
def read_plant_attracts_species(plant_id: int, db: Session = Depends(get_db)):
    attracts_list = attracts_service.get_plant_attracts(db, plant_id)
    return PlantAttracts(
        plant_id=plant_id,
        species_list=[attract.species for attract in attracts_list]
    )

@router.delete("/{attracts_id}")
def delete_attracts(attracts_id: int, db: Session = Depends(get_db)):
    if not attracts_service.delete_attracts(db, attracts_id):
        raise HTTPException(status_code=404, detail="Attracts entry not found")
    return {"message": "Attracts entry deleted successfully"}

@router.delete("/plant/{plant_id}")
def delete_plant_attracts(plant_id: int, db: Session = Depends(get_db)):
    if not attracts_service.delete_plant_attracts(db, plant_id):
        raise HTTPException(status_code=404, detail="No attracts entries found for this plant")
    return {"message": "All attracts entries for plant deleted successfully"}
