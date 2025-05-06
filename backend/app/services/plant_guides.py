# /backend/app/services/plant_guides.py
from sqlalchemy.orm import Session
from app.models.plant_guides import PlantGuide
from app.schemas.plant_guides import PlantGuideCreate
from fastapi import HTTPException

def get_plant_guides(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PlantGuide).offset(skip).limit(limit).all()

def create_plant_guide(db: Session, guide: PlantGuideCreate):
    db_guide = PlantGuide(**guide.model_dump())
    db.add(db_guide)
    db.commit()
    db.refresh(db_guide)
    return db_guide

def get_plant_guide(db: Session, guide_id: int):
    return db.query(PlantGuide).filter(PlantGuide.id == guide_id).first()

def get_guides_for_plant(db: Session, plant_id: int, skip: int = 0, limit: int = 100):
    return db.query(PlantGuide)\
        .filter(PlantGuide.plant_id == plant_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_all_guides(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PlantGuide).offset(skip).limit(limit).all()

def update_plant_guide(db: Session, guide_id: int, guide: PlantGuideCreate):
    db_guide = get_plant_guide(db, guide_id)
    if db_guide is None:
        return None
    
    for key, value in guide.model_dump().items():
        setattr(db_guide, key, value)
    
    db.commit()
    db.refresh(db_guide)
    return db_guide

def delete_plant_guide(db: Session, guide_id: int):
    db_guide = get_plant_guide(db, guide_id)
    if db_guide is None:
        return False
    
    db.delete(db_guide)
    db.commit()
    return True
