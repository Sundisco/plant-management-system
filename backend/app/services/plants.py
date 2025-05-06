# /backend/app/services/plants.py
from sqlalchemy.orm import Session
from models.plants import Plant
from schemas.plants import PlantCreate

def get_plants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Plant).offset(skip).limit(limit).all()

def create_plant(db: Session, plant: PlantCreate):
    db_plant = Plant(**plant.dict())
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant

def get_plant_by_id(db: Session, plant_id: int):
    return db.query(Plant).filter(Plant.id == plant_id).first()

def update_plant(db: Session, plant_id: int, plant_data: PlantCreate):
    db_plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if db_plant:
        for key, value in plant_data.dict().items():
            setattr(db_plant, key, value)
        db.commit()
        db.refresh(db_plant)
        return db_plant
    return None
