# /backend/app/services/plant_guides.py
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
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
    guides = db.query(PlantGuide)\
        .options(joinedload(PlantGuide.plant))\
        .filter(PlantGuide.plant_id == plant_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    if not guides:
        return []
    
    # Create a serialized version of the guides
    serialized_guides = []
    for guide in guides:
        guide_dict = {
            "id": guide.id,
            "plant_id": guide.plant_id,
            "type": guide.type,
            "description": guide.description,
            "plant": None
        }
        
        if guide.plant:
            plant_dict = {
                "id": guide.plant.id,
                "common_name": guide.plant.common_name,
                "scientific_name": guide.plant.scientific_name or [],
                "other_names": guide.plant.other_names or [],
                "family": guide.plant.family,
                "type": guide.plant.type,
                "description": guide.plant.description,
                "growth_rate": guide.plant.growth_rate,
                "maintenance": guide.plant.maintenance,
                "hardiness_zone": guide.plant.hardiness_zone,
                "image_url": guide.plant.image_url,
                "cycle": guide.plant.cycle,
                "watering": guide.plant.watering,
                "is_evergreen": guide.plant.is_evergreen,
                "edible_fruit": guide.plant.edible_fruit,
                "attracts": [a.species for a in guide.plant.attracts] if guide.plant.attracts else [],
                "sunlight": [s.condition for s in guide.plant.sunlight_info] if guide.plant.sunlight_info else []
            }
            guide_dict["plant"] = plant_dict
        
        serialized_guides.append(guide_dict)
    
    return serialized_guides

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
