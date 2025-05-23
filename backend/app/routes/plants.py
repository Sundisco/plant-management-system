# /backend/app/routes/plants.py
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.models.plants import Plant as DBPlant
from app.models.attracts import Attracts
from app.models.sunlight import Sunlight
from sqlalchemy import or_, func, Index, text
from app.services import plant_service
from app.schemas.plants import (
    Plant, 
    PlantCreate, 
    PlantSearch, 
    SearchResponse, 
    Plant as PlantResponse  # Use Plant as PlantResponse
)
from app.schemas.plant_guides import PlantGuide
from app.services import plant_guides as guide_service
from app.models.user_plants import UserPlant
from sqlalchemy import Text
import threading
from app.scripts.initialize_watering_schedules import sync_watering_schedules
from functools import lru_cache
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

# Cache for user plants (5 minutes TTL)
user_plants_cache = {}
CACHE_TTL = 300  # 5 minutes in seconds

def get_cached_user_plants(user_id: int) -> set:
    """Get user plants from cache or database"""
    cache_key = f"user_plants_{user_id}"
    cache_data = user_plants_cache.get(cache_key)
    
    if cache_data and (datetime.now() - cache_data['timestamp']).seconds < CACHE_TTL:
        return cache_data['data']
    
    return None

def set_cached_user_plants(user_id: int, plants: set):
    """Set user plants in cache"""
    cache_key = f"user_plants_{user_id}"
    user_plants_cache[cache_key] = {
        'data': plants,
        'timestamp': datetime.now()
    }

@router.get("/search")
async def search_plants(
    query: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Search endpoint that checks common_name, scientific_name, other_names, and type"""
    try:
        # Start with a base query that includes only necessary columns
        search_query = db.query(
            DBPlant.id,
            DBPlant.common_name,
            DBPlant.scientific_name,
            DBPlant.other_names,
            DBPlant.type,
            DBPlant.image_url
        )
        
        if query:
            search_term = f"%{query}%"
            # Use ILIKE for string fields and proper ANY syntax for array fields
            search_query = search_query.filter(
                or_(
                    DBPlant.common_name.ilike(search_term),
                    DBPlant.type.ilike(search_term),
                    text("EXISTS (SELECT 1 FROM unnest(plants.scientific_name) AS sci_name WHERE sci_name ILIKE :search_term)").bindparams(search_term=search_term),
                    text("EXISTS (SELECT 1 FROM unnest(plants.other_names) AS other_name WHERE other_name ILIKE :search_term)").bindparams(search_term=search_term)
                )
            )
        
        # Get user plants from cache or database
        user_plants = None
        if user_id:
            user_plants = get_cached_user_plants(user_id)
            if user_plants is None:
                user_plants = {
                    plant_id[0] for plant_id in 
                    db.query(UserPlant.plant_id)
                    .filter(UserPlant.user_id == user_id)
                    .all()
                }
                set_cached_user_plants(user_id, user_plants)
        
        # Execute the query with a limit
        plants = search_query.limit(20).all()
        
        print(f"Query: {query}")
        print(f"Number of plants found: {len(plants)}")
        if plants:
            print(f"Sample results: {[(p.common_name, p.scientific_name) for p in plants[:3]]}")
        
        return {
            "items": [
                {
                    "id": plant.id,
                    "common_name": plant.common_name,
                    "scientific_name": plant.scientific_name if plant.scientific_name else [],
                    "other_names": plant.other_names if plant.other_names else [],
                    "type": plant.type or "",
                    "image_url": plant.image_url,
                    "in_user_garden": plant.id in user_plants if user_plants else False
                }
                for plant in plants
            ]
        }

    except Exception as e:
        print("Search error:", str(e))
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}

@router.get("/types")
def get_plant_types(db: Session = Depends(get_db)):
    """Get all available plant types"""
    types = db.query(DBPlant.type).distinct().all()
    return [t[0] for t in types if t[0]]

@router.get("/{plant_id}", response_model=Plant)
def read_plant(plant_id: int, db: Session = Depends(get_db)):
    plant = plant_service.get_plant_by_id(db, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    # Serialize attracts and sunlight as lists of strings
    attracts = [a.species for a in plant.attracts] if plant.attracts else []
    sunlight = [s.condition for s in plant.sunlight_info] if plant.sunlight_info else []
    return {
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
        "section": getattr(plant, "section", None),
        "created_at": getattr(plant, "created_at", None),
        "updated_at": getattr(plant, "updated_at", None),
        "attracts": attracts,
        "sunlight": sunlight
    }

@router.get("/", response_model=list[Plant])
def read_plants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return plant_service.get_plants(db, skip=skip, limit=limit)

@router.post("/", response_model=Plant)
def create_plant_view(plant: PlantCreate, db: Session = Depends(get_db)):
    return plant_service.create_plant(db, plant)

@router.put("/{plant_id}", response_model=Plant)
def update_plant_view(plant_id: int, plant: PlantCreate, db: Session = Depends(get_db)):
    updated_plant = plant_service.update_plant(db, plant_id, plant)
    if updated_plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return updated_plant

@router.delete("/{plant_id}")
def delete_plant_view(plant_id: int, db: Session = Depends(get_db)):
    if not plant_service.delete_plant(db, plant_id):
        raise HTTPException(status_code=404, detail="Plant not found")
    return {"message": "Plant deleted successfully"}

@router.get("/{plant_id}/guides", response_model=List[PlantGuide])
def read_plant_guides(plant_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    guides = guide_service.get_guides_for_plant(db, plant_id, skip=skip, limit=limit)
    return guides

@router.post("/user/{user_id}/plants/{plant_id}")
def add_plant_to_garden(
    user_id: int,
    plant_id: int,
    db: Session = Depends(get_db)
):
    """
    Add a plant to user's garden and return full plant info
    """
    try:
        # Check if plant exists
        plant = db.query(DBPlant).filter(DBPlant.id == plant_id).first()
        if not plant:
            raise HTTPException(
                status_code=404,
                detail="Plant not found"
            )

        # Check if plant already in user's garden
        existing = db.query(UserPlant).filter(
            UserPlant.user_id == user_id,
            UserPlant.plant_id == plant_id
        ).first()
        
        if existing:
            # Return the plant info even if it's already in the garden
            return {
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
                "section": existing.section
            }
        
        # Create new user_plant entry
        user_plant = UserPlant(user_id=user_id, plant_id=plant_id)
        db.add(user_plant)
        db.commit()
        db.refresh(user_plant)
    
        # Trigger watering schedule sync in background
        threading.Thread(target=sync_watering_schedules).start()

        return {
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
            "section": None  # New plants start with no section
        }
    except Exception as e:
        db.rollback()
        print(f"Error adding plant to garden: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to add plant to garden"
        )

@router.get("/user/{user_id}/plants", response_model=List[PlantResponse])
def get_user_plants(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get all plants in user's garden with their sections
    """
    try:
        # Query user_plants first to get sections and timestamps
        user_plants_dict = {
            up.plant_id: {
                'section': up.section,
                'created_at': up.created_at,
                'updated_at': up.updated_at
            }
            for up in db.query(UserPlant)
            .filter(UserPlant.user_id == user_id)
            .all()
        }
        
        if not user_plants_dict:
            return []
        
        # Get the full plant information for these plants with their relationships
        plants = (
            db.query(DBPlant)
            .filter(DBPlant.id.in_(user_plants_dict.keys()))
            .options(
                joinedload(DBPlant.attracts),
                joinedload(DBPlant.sunlight_info)
            )
            .limit(limit)
            .all()
        )
        
        # Combine plant info with sections and timestamps
        result = []
        for plant in plants:
            try:
                plant_info = user_plants_dict.get(plant.id, {})
                attracts = [a.species for a in plant.attracts] if plant.attracts else []
                sunlight = [s.condition for s in plant.sunlight_info] if plant.sunlight_info else []
                plant_data = {
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
                    "section": plant_info.get('section'),
                    "created_at": plant_info.get('created_at'),
                    "updated_at": plant_info.get('updated_at'),
                    "attracts": attracts,
                    "sunlight": sunlight
                }
                result.append(plant_data)
            except Exception as e:
                continue
        return result
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user/{user_id}/plants/{plant_id}")
def remove_plant_from_garden(
    user_id: int,
    plant_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove a plant from user's garden
    """
    user_plant = db.query(UserPlant).filter(
        UserPlant.user_id == user_id,
        UserPlant.plant_id == plant_id
    ).first()
    
    if not user_plant:
        raise HTTPException(
            status_code=404,
            detail="Plant not found in garden"
        )
    
    db.delete(user_plant)
    db.commit()

    # Trigger watering schedule sync in background
    threading.Thread(target=sync_watering_schedules).start()

    return {"status": "success"}

@router.get("/basic-search")  # New URL path
async def basic_search(
    query: str = Query(...),  # Make query required
    db: Session = Depends(get_db)
):
    try:
        search_query = db.query(DBPlant)
        search_query = search_query.filter(DBPlant.common_name.ilike(f"%{query}%"))
        plants = search_query.all()
        
        return {
            "items": [
                {
                    "id": plant.id,
                    "common_name": plant.common_name,
                    "scientific_name": plant.scientific_name,
                    "other_names": plant.other_names,
                    "type": plant.type
                }
                for plant in plants
            ]
        }
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/user/{user_id}/plants/{plant_id}/section")
async def update_plant_section(
    user_id: int,
    plant_id: int,
    section: dict,
    db: Session = Depends(get_db)
):
    """Update the section of a plant in user's garden"""
    print(f"Updating section for plant {plant_id} to {section}")  # Debug log
    
    user_plant = db.query(UserPlant).filter(
        UserPlant.user_id == user_id,
        UserPlant.plant_id == plant_id
    ).first()
    
    if not user_plant:
        raise HTTPException(status_code=404, detail="Plant not found in garden")
    
    # Store just the section value, not the whole dictionary
    section_value = section.get('section')
    print(f"Current section in DB: {user_plant.section}")  # Debug log
    print(f"Setting section to: {section_value}")  # Debug log
    
    user_plant.section = section_value
    
    try:
        db.commit()
        db.refresh(user_plant)
        print(f"Updated section in DB: {user_plant.section}")  # Debug log
        return {"status": "success", "section": user_plant.section}
    except Exception as e:
        db.rollback()
        print(f"Error updating section: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

class PlantFilter(BaseModel):
    attracts: Optional[List[str]] = None
    type: Optional[str] = None
    growth_rate: Optional[str] = None
    maintenance: Optional[str] = None
    cycle: Optional[str] = None
    watering: Optional[str] = None
    sunlight: Optional[List[str]] = None
    is_evergreen: Optional[bool] = None
    edible_fruit: Optional[bool] = None

@router.post("/filtered")
async def get_filtered_plants(
    filter: PlantFilter,
    db: Session = Depends(get_db)
):
    """Get plants filtered by various criteria"""
    try:
        print(f"Received filter parameters: {filter.dict()}")
        
        query = db.query(DBPlant).options(
            joinedload(DBPlant.attracts),
            joinedload(DBPlant.sunlight_info)
        )

        # Apply filters
        if filter.attracts:
            print(f"Filtering by attracts: {filter.attracts}")
            query = query.filter(DBPlant.attracts.any(Attracts.species.in_(filter.attracts)))
        if filter.type:
            print(f"Filtering by type: {filter.type}")
            query = query.filter(DBPlant.type == filter.type)
        if filter.growth_rate:
            print(f"Filtering by growth_rate: {filter.growth_rate}")
            query = query.filter(DBPlant.growth_rate == filter.growth_rate)
        if filter.maintenance:
            print(f"Filtering by maintenance: {filter.maintenance}")
            query = query.filter(DBPlant.maintenance == filter.maintenance)
        if filter.cycle:
            print(f"Filtering by cycle: {filter.cycle}")
            query = query.filter(DBPlant.cycle == filter.cycle)
        if filter.watering:
            print(f"Filtering by watering: {filter.watering}")
            query = query.filter(DBPlant.watering == filter.watering)
        if filter.sunlight:
            print(f"Filtering by sunlight: {filter.sunlight}")
            query = query.filter(DBPlant.sunlight_info.any(Sunlight.condition.in_(filter.sunlight)))
        if filter.is_evergreen is not None:
            print(f"Filtering by is_evergreen: {filter.is_evergreen}")
            query = query.filter(DBPlant.is_evergreen == filter.is_evergreen)
        if filter.edible_fruit is not None:
            print(f"Filtering by edible_fruit: {filter.edible_fruit}")
            query = query.filter(DBPlant.edible_fruit == filter.edible_fruit)

        plants = query.all()
        print(f"Found {len(plants)} plants matching the criteria")
        
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

    except Exception as e:
        print(f"Error in filtered plants search: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
