from sqlalchemy.orm import Session
from app.models.plants import Plant
from app.schemas.plants import PlantCreate

def create_plant(db: Session, plant: PlantCreate):
    db_plant = Plant(**plant.model_dump())
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant

def get_plants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Plant).offset(skip).limit(limit).all()

def get_plant_by_id(db: Session, plant_id: int):
    return db.query(Plant).filter(Plant.id == plant_id).first()

def update_plant(db: Session, plant_id: int, plant_data: PlantCreate):
    db_plant = get_plant_by_id(db, plant_id)
    if db_plant:
        for key, value in plant_data.model_dump().items():
            setattr(db_plant, key, value)
        db.commit()
        db.refresh(db_plant)
    return db_plant

def delete_plant(db: Session, plant_id: int):
    plant = get_plant_by_id(db, plant_id)
    if plant:
        db.delete(plant)
        db.commit()
        return True
    return False 