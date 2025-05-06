from sqlalchemy.orm import Session
from app.models.attracts import Attracts
from app.models.plants import Plant
from app.schemas.attracts import AttractsCreate
from fastapi import HTTPException
from typing import List

def create_attracts(db: Session, attracts: AttractsCreate):
    # First check if the plant exists
    plant = db.query(Plant).filter(Plant.id == attracts.plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    # Then create the attracts entry
    db_attracts = Attracts(**attracts.model_dump())
    db.add(db_attracts)
    try:
        db.commit()
        db.refresh(db_attracts)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create attracts entry")
    return db_attracts

def get_attracts(db: Session, attracts_id: int):
    return db.query(Attracts).filter(Attracts.id == attracts_id).first()

def get_plant_attracts(db: Session, plant_id: int) -> List[Attracts]:
    return db.query(Attracts).filter(Attracts.plant_id == plant_id).all()

def delete_attracts(db: Session, attracts_id: int):
    db_attracts = get_attracts(db, attracts_id)
    if db_attracts is None:
        return False
    
    db.delete(db_attracts)
    db.commit()
    return True

def delete_plant_attracts(db: Session, plant_id: int):
    db_attracts = get_plant_attracts(db, plant_id)
    if not db_attracts:
        return False
    
    for attract in db_attracts:
        db.delete(attract)
    db.commit()
    return True
