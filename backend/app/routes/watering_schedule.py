from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta, datetime
from app.services import watering_schedule as schedule_service
from app.schemas.watering_schedule import WateringSchedule as WateringScheduleSchema, WateringScheduleCreate, WateringScheduleUpdate
from app.database import get_db
from app.models.watering_schedule import WateringSchedule
from app.models.user_plants import UserPlant
from app.models.plants import Plant
from app.services.weather import get_weather_for_week

router = APIRouter()

@router.post("/", response_model=WateringScheduleSchema)
def create_schedule(schedule: WateringScheduleCreate, db: Session = Depends(get_db)):
    return schedule_service.create_watering_schedule(db, schedule)

@router.get("/user/{user_id}", response_model=List[WateringScheduleSchema])
def read_user_schedules(
    user_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return schedule_service.get_user_schedules(db, user_id, date_from, date_to)

@router.get("/user/{user_id}/plant/{plant_id}", response_model=List[WateringScheduleSchema])
def read_user_plant_schedules(
    user_id: int,
    plant_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return schedule_service.get_user_plant_schedules(db, user_id, plant_id, date_from, date_to)

@router.get("/user/{user_id}/upcoming", response_model=List[WateringScheduleSchema])
def read_upcoming_schedules(
    user_id: int,
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    return schedule_service.get_upcoming_schedules(db, user_id, days)

@router.put("/{schedule_id}", response_model=WateringScheduleSchema)
def update_schedule(
    schedule_id: int,
    schedule_update: WateringScheduleUpdate,
    db: Session = Depends(get_db)
):
    db_schedule = schedule_service.update_schedule(db, schedule_id, schedule_update)
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    if not schedule_service.delete_schedule(db, schedule_id):
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule deleted successfully"}

@router.get("/{user_id}")
def get_watering_schedule_overview(user_id: int, db: Session = Depends(get_db)):
    """Get watering schedule overview with weather adjustments"""
    try:
        schedule = schedule_service.get_user_watering_schedule(db, user_id)
        return {
            "schedule": schedule,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting watering schedule: {str(e)}"
        )

@router.post("/watering/schedule/{user_id}/plant/{plant_id}")
def create_plant_schedule(user_id: int, plant_id: int, db: Session = Depends(get_db)):
    """Create a new watering schedule for a plant"""
    try:
        schedule = schedule_service.create_watering_schedule(db, user_id, plant_id)
        return {
            "schedule": schedule,
            "last_updated": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating watering schedule: {str(e)}"
        )
