from sqlalchemy.orm import Session
from app.models.watering import Watering
from app.schemas.watering import WateringCreate
from fastapi import HTTPException

def create_watering(db: Session, watering: WateringCreate):
    # Check if watering already exists for this plant
    existing = db.query(Watering).filter(Watering.plant_id == watering.plant_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Watering information already exists for this plant")
    
    db_watering = Watering(**watering.model_dump(exclude={'plant'}))
    db.add(db_watering)
    db.commit()
    db.refresh(db_watering)
    return db_watering

def get_watering(db: Session, watering_id: int):
    return db.query(Watering).filter(Watering.id == watering_id).first()

def get_plant_watering(db: Session, plant_id: int):
    return db.query(Watering).filter(Watering.plant_id == plant_id).first()

def update_watering(db: Session, watering_id: int, watering: WateringCreate):
    db_watering = get_watering(db, watering_id)
    if db_watering is None:
        return None
    
    update_data = watering.model_dump(exclude={'plant'})
    for key, value in update_data.items():
        setattr(db_watering, key, value)
    
    db.commit()
    db.refresh(db_watering)
    return db_watering

def delete_watering(db: Session, watering_id: int):
    db_watering = get_watering(db, watering_id)
    if db_watering is None:
        return False
    
    db.delete(db_watering)
    db.commit()
    return True
