from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services import watering as watering_service
from app.schemas.watering import Watering, WateringCreate
from app.database import get_db
from app.models.watering_schedule import WateringSchedule
import requests

router = APIRouter()

@router.post("/", response_model=Watering)
def create_watering(watering: WateringCreate, db: Session = Depends(get_db)):
    return watering_service.create_watering(db, watering)

@router.get("/{watering_id}", response_model=Watering)
def read_watering(watering_id: int, db: Session = Depends(get_db)):
    db_watering = watering_service.get_watering(db, watering_id)
    if db_watering is None:
        raise HTTPException(status_code=404, detail="Watering not found")
    return db_watering

@router.get("/plant/{plant_id}", response_model=Watering)
def read_plant_watering(plant_id: int, db: Session = Depends(get_db)):
    db_watering = watering_service.get_plant_watering(db, plant_id)
    if db_watering is None:
        raise HTTPException(status_code=404, detail="Watering not found for this plant")
    return db_watering

@router.put("/{watering_id}", response_model=Watering)
def update_watering(watering_id: int, watering: WateringCreate, db: Session = Depends(get_db)):
    db_watering = watering_service.update_watering(db, watering_id, watering)
    if db_watering is None:
        raise HTTPException(status_code=404, detail="Watering not found")
    return db_watering

@router.delete("/{watering_id}")
def delete_watering(watering_id: int, db: Session = Depends(get_db)):
    if not watering_service.delete_watering(db, watering_id):
        raise HTTPException(status_code=404, detail="Watering not found")
    return {"message": "Watering deleted successfully"}

@router.get("/watering/schedule/{user_id}")
async def get_watering_schedule(user_id: int, db: Session = Depends(get_db)):
    schedules = db.query(WateringSchedule).filter(
        WateringSchedule.user_id == user_id
    ).all()
    
    # Get weather data from a weather API
    # You'll need to sign up for a weather API service
    weather_data = get_weather_data()  # Implement this function
    
    return {
        "schedule": [
            {
                "day": schedule.day,
                "amount": schedule.amount,
                "weather_dependent": schedule.weather_dependent
            }
            for schedule in schedules
        ],
        "weather": weather_data
    }
