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
    return user_service.get_user_plants(db, user_id) 