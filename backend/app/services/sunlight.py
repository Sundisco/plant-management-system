from sqlalchemy.orm import Session
from app.models.sunlight import Sunlight
from app.schemas.sunlight import SunlightCreate
from fastapi import HTTPException

def create_sunlight(db: Session, sunlight: SunlightCreate):
    # Check if sunlight already exists for this plant
    existing = db.query(Sunlight).filter(Sunlight.plant_id == sunlight.plant_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Sunlight information already exists for this plant")
    
    db_sunlight = Sunlight(**sunlight.model_dump())
    db.add(db_sunlight)
    db.commit()
    db.refresh(db_sunlight)
    return db_sunlight

def get_sunlight(db: Session, sunlight_id: int):
    return db.query(Sunlight).filter(Sunlight.id == sunlight_id).first()

def get_plant_sunlight(db: Session, plant_id: int):
    return db.query(Sunlight).filter(Sunlight.plant_id == plant_id).first()

def update_sunlight(db: Session, sunlight_id: int, sunlight: SunlightCreate):
    db_sunlight = get_sunlight(db, sunlight_id)
    if db_sunlight is None:
        return None
    
    for key, value in sunlight.model_dump().items():
        setattr(db_sunlight, key, value)
    
    db.commit()
    db.refresh(db_sunlight)
    return db_sunlight

def delete_sunlight(db: Session, sunlight_id: int):
    db_sunlight = get_sunlight(db, sunlight_id)
    if db_sunlight is None:
        return False
    
    db.delete(db_sunlight)
    db.commit()
    return True
