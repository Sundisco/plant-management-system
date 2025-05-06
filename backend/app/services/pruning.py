from sqlalchemy.orm import Session
from app.models.pruning import Pruning
from app.schemas.pruning import PruningCreate
from fastapi import HTTPException

def create_pruning(db: Session, pruning: PruningCreate):
    # Check if pruning already exists for this plant
    existing = db.query(Pruning).filter(Pruning.plant_id == pruning.plant_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Pruning information already exists for this plant")
    
    db_pruning = Pruning(**pruning.model_dump())
    db.add(db_pruning)
    db.commit()
    db.refresh(db_pruning)
    return db_pruning

def get_pruning(db: Session, pruning_id: int):
    return db.query(Pruning).filter(Pruning.id == pruning_id).first()

def get_plant_pruning(db: Session, plant_id: int):
    return db.query(Pruning).filter(Pruning.plant_id == plant_id).first()

def update_pruning(db: Session, pruning_id: int, pruning: PruningCreate):
    db_pruning = get_pruning(db, pruning_id)
    if db_pruning is None:
        return None
    
    for key, value in pruning.model_dump().items():
        setattr(db_pruning, key, value)
    
    db.commit()
    db.refresh(db_pruning)
    return db_pruning

def delete_pruning(db: Session, pruning_id: int):
    db_pruning = get_pruning(db, pruning_id)
    if db_pruning is None:
        return False
    
    db.delete(db_pruning)
    db.commit()
    return True
