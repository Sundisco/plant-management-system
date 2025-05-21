from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.services import users as user_service
from app.schemas.users import User, UserCreate, UserWithPlants, UserPlantAdd
from app.schemas.plants import Plant
from app.database import get_db
from fastapi.exceptions import ResponseValidationError

router = APIRouter()

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db, user)

@router.get("/{user_id}", response_model=UserWithPlants)
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = user_service.get_user(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except ResponseValidationError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/plants")
def add_plant_to_user(user_id: int, plant: UserPlantAdd, db: Session = Depends(get_db)):
    return user_service.add_plant_to_user(db, user_id, plant.plant_id)

@router.delete("/{user_id}/plants/{plant_id}")
def remove_plant_from_user(user_id: int, plant_id: int, db: Session = Depends(get_db)):
    if not user_service.remove_plant_from_user(db, user_id, plant_id):
        raise HTTPException(status_code=404, detail="Plant not found in user's garden")
    return {"message": "Plant removed from user's garden"}

@router.get("/{user_id}/plants", response_model=List[Plant])
def read_user_plants(user_id: int, db: Session = Depends(get_db)):
    plants = user_service.get_user_plants(db, user_id)
    result = []
    for plant in plants:
        attracts = [a.species for a in plant.attracts] if hasattr(plant, 'attracts') and plant.attracts else []
        sunlight = [s.condition for s in getattr(plant, 'sunlight_info', [])] if hasattr(plant, 'sunlight_info') else []
        result.append({
            "id": plant.id,
            "common_name": plant.common_name,
            "scientific_name": plant.scientific_name or [],
            "other_names": plant.other_names or [],
            "family": plant.family,
            "type": plant.type,
            "cycle": plant.cycle,
            "watering": plant.watering,
            "image_url": plant.image_url,
            "description": plant.description,
            "is_evergreen": plant.is_evergreen,
            "growth_rate": plant.growth_rate,
            "maintenance": plant.maintenance,
            "hardiness_zone": plant.hardiness_zone,
            "edible_fruit": plant.edible_fruit,
            "section": getattr(plant, "section", None),
            "created_at": getattr(plant, "created_at", None),
            "updated_at": getattr(plant, "updated_at", None),
            "attracts": attracts,
            "sunlight": sunlight
        })
    return result 