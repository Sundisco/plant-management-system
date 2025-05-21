from sqlalchemy.orm import Session, joinedload
from app.models.plants import Plant
from app.schemas.plants import PlantCreate

def create_plant(db: Session, plant: PlantCreate):
    db_plant = Plant(**plant.model_dump())
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant

def get_plants(db: Session, skip: int = 0, limit: int = 100):
    plants = (
        db.query(Plant)
        .options(
            joinedload(Plant.attracts),
            joinedload(Plant.sunlight_info)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Serialize the plants with their relationships
    result = []
    for plant in plants:
        attracts = [a.species for a in plant.attracts] if plant.attracts else []
        sunlight = [s.condition for s in plant.sunlight_info] if plant.sunlight_info else []
        
        plant_dict = {
            "id": plant.id,
            "common_name": plant.common_name,
            "scientific_name": plant.scientific_name or [],
            "other_names": plant.other_names or [],
            "family": plant.family,
            "type": plant.type,
            "cycle": plant.cycle,
            "watering": plant.watering,
            "image_url": plant.image_url,
            "description": plant.description,
            "is_evergreen": plant.is_evergreen,
            "growth_rate": plant.growth_rate,
            "maintenance": plant.maintenance,
            "hardiness_zone": plant.hardiness_zone,
            "edible_fruit": plant.edible_fruit,
            "attracts": attracts,
            "sunlight": sunlight
        }
        result.append(plant_dict)
    
    return result

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