from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services import sunlight as sunlight_service
from app.schemas.sunlight import Sunlight, SunlightCreate
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=Sunlight)
def create_sunlight(sunlight: SunlightCreate, db: Session = Depends(get_db)):
    return sunlight_service.create_sunlight(db, sunlight)

@router.get("/{sunlight_id}", response_model=Sunlight)
def read_sunlight(sunlight_id: int, db: Session = Depends(get_db)):
    db_sunlight = sunlight_service.get_sunlight(db, sunlight_id)
    if db_sunlight is None:
        raise HTTPException(status_code=404, detail="Sunlight not found")
    return db_sunlight

@router.get("/plant/{plant_id}", response_model=Sunlight)
def read_plant_sunlight(plant_id: int, db: Session = Depends(get_db)):
    db_sunlight = sunlight_service.get_plant_sunlight(db, plant_id)
    if db_sunlight is None:
        raise HTTPException(status_code=404, detail="Sunlight not found for this plant")
    return db_sunlight

@router.put("/{sunlight_id}", response_model=Sunlight)
def update_sunlight(sunlight_id: int, sunlight: SunlightCreate, db: Session = Depends(get_db)):
    db_sunlight = sunlight_service.update_sunlight(db, sunlight_id, sunlight)
    if db_sunlight is None:
        raise HTTPException(status_code=404, detail="Sunlight not found")
    return db_sunlight

@router.delete("/{sunlight_id}")
def delete_sunlight(sunlight_id: int, db: Session = Depends(get_db)):
    if not sunlight_service.delete_sunlight(db, sunlight_id):
        raise HTTPException(status_code=404, detail="Sunlight not found")
    return {"message": "Sunlight deleted successfully"}
