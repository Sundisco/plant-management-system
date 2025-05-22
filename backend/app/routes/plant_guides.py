# /backend/app/routes/plant_guides.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.services import plant_guides as guide_service
from app.schemas.plant_guides import PlantGuide, PlantGuideCreate
from app.database import get_db
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/", response_model=PlantGuide)
def create_guide(guide: PlantGuideCreate, db: Session = Depends(get_db)):
    try:
        return guide_service.create_plant_guide(db, guide)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[PlantGuide])
def read_guides(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        guides = guide_service.get_all_guides(db, skip=skip, limit=limit)
        return guides
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{guide_id}", response_model=PlantGuide)
def read_guide(guide_id: int, db: Session = Depends(get_db)):
    try:
        db_guide = guide_service.get_plant_guide(db, guide_id)
        if db_guide is None:
            raise HTTPException(status_code=404, detail="Guide not found")
        return db_guide
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{guide_id}", response_model=PlantGuide)
def update_guide(guide_id: int, guide: PlantGuideCreate, db: Session = Depends(get_db)):
    try:
        db_guide = guide_service.update_plant_guide(db, guide_id, guide)
        if db_guide is None:
            raise HTTPException(status_code=404, detail="Guide not found")
        return db_guide
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{guide_id}")
def delete_guide(guide_id: int, db: Session = Depends(get_db)):
    try:
        if not guide_service.delete_plant_guide(db, guide_id):
            raise HTTPException(status_code=404, detail="Guide not found")
        return {"message": "Guide deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plant/{plant_id}", response_model=List[PlantGuide])
def get_guides_for_plant(plant_id: int, db: Session = Depends(get_db)):
    try:
        guides = guide_service.get_guides_for_plant(db, plant_id)
        return guides
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
