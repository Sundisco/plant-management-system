from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta, datetime
from app.services import watering_schedule as schedule_service
from app.schemas.watering_schedule import (
    WateringSchedule as WateringScheduleSchema,
    WateringScheduleCreate,
    WateringScheduleUpdate,
    WateringScheduleResponse,
    WateringScheduleOverview
)
from app.database import get_db
import logging
from app.models.watering_schedule import WateringSchedule

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=WateringScheduleSchema)
def create_schedule(schedule: WateringScheduleCreate, db: Session = Depends(get_db)):
    """Create a new watering schedule"""
    try:
        return schedule_service.create_watering_schedule(
            db=db,
            user_id=schedule.user_id,
            plant_id=schedule.plant_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating watering schedule: {str(e)}"
        )

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

@router.get("/watering-schedule/user/{user_id}", response_model=WateringScheduleOverview)
def get_watering_schedule_overview(user_id: int, db: Session = Depends(get_db)):
    """Get watering schedule overview with weather adjustments"""
    try:
        logger.info(f"Getting watering schedule for user {user_id}")
        schedule = schedule_service.get_watering_schedule(db, user_id)
        if not schedule:
            return {
                "schedule": [],
                "last_updated": datetime.utcnow().isoformat()
            }
        return schedule
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting watering schedule: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e)}
        )

@router.post("/watering/schedule/{user_id}/plant/{plant_id}", response_model=WateringScheduleResponse)
def create_plant_schedule(user_id: int, plant_id: int, db: Session = Depends(get_db)):
    """Create a new watering schedule for a plant"""
    try:
        schedule = schedule_service.create_watering_schedule(db, user_id, plant_id)
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/test", response_model=WateringScheduleOverview)
def get_watering_schedule_test(user_id: int, db: Session = Depends(get_db)):
    """Get watering schedule with mock weather data for testing weather adjustments"""
    try:
        logger.info(f"Getting test watering schedule for user {user_id}")
        schedule = schedule_service.get_watering_schedule(db, user_id)
        if not schedule:
            return {
                "schedule": [],
                "last_updated": datetime.utcnow().isoformat()
            }

        # Add mock weather data for the next day (high temperature)
        tomorrow = (datetime.utcnow() + timedelta(days=1)).date().isoformat()
        
        # First, add weather data to all days
        for day in schedule["schedule"]:
            if day["date"] == tomorrow:
                # Add hot weather data for tomorrow
                day["weather"] = {
                    "temperature": 35.0,  # High temperature
                    "precipitation": 0.0,
                    "wind_speed": 5.0,
                    "weather_icons": ["hot"]  # Include weather icons in the weather object
                }
            else:
                # Add normal weather data for other days
                day["weather"] = {
                    "temperature": 20.0,
                    "precipitation": 0.0,
                    "wind_speed": 5.0,
                    "weather_icons": ["sunny"]  # Include weather icons in the weather object
                }
            # Remove the separate weather_icons field
            if "weather_icons" in day:
                del day["weather_icons"]

        # Then, adjust all future schedules
        adjusted_plants = []  # Keep track of adjusted plants
        for day in schedule["schedule"]:
            current_date = datetime.fromisoformat(day["date"]).date()
            if current_date >= datetime.fromisoformat(tomorrow).date():
                for section in day["sections"]:
                    for group in section["groups"]:
                        for plant in group["plants"]:
                            # Get the actual schedule from the database
                            db_schedule = db.query(WateringSchedule).filter(
                                WateringSchedule.user_id == user_id,
                                WateringSchedule.plant_id == plant["plant_id"],
                                WateringSchedule.scheduled_date == current_date
                            ).first()
                            
                            if db_schedule and not db_schedule.weather_adjusted:  # Only adjust if not already adjusted
                                # Calculate adjusted date (one day earlier)
                                original_date = db_schedule.scheduled_date
                                adjusted_date = db_schedule.scheduled_date - timedelta(days=1)
                                
                                # Check if a schedule already exists for the adjusted date
                                existing_schedule = db.query(WateringSchedule).filter(
                                    WateringSchedule.user_id == user_id,
                                    WateringSchedule.plant_id == plant["plant_id"],
                                    WateringSchedule.scheduled_date == adjusted_date
                                ).first()
                                
                                if not existing_schedule:
                                    # Create a new schedule for the adjusted date
                                    new_schedule = WateringSchedule(
                                        user_id=user_id,
                                        plant_id=plant["plant_id"],
                                        scheduled_date=adjusted_date,
                                        water_needed=True,
                                        volume_needed=db_schedule.volume_needed,
                                        weather_dependent=True,
                                        completed=False,
                                        weather_adjusted=True,
                                        frequency_days=db_schedule.frequency_days,
                                        depth_mm=db_schedule.depth_mm,
                                        volume_feet=db_schedule.volume_feet
                                    )
                                    
                                    # Delete the original schedule
                                    db.delete(db_schedule)
                                    db.add(new_schedule)
                                    db.commit()
                                    
                                    # Update the plant data to reflect the adjustment
                                    plant["weather_adjusted"] = True
                                    plant["weather_info"] = {
                                        "is_adjusted": True,
                                        "original_date": original_date.isoformat()
                                    }
                                    plant["next_watering"] = adjusted_date.isoformat()

        # Override any weather data from the database with our mock data
        for day in schedule["schedule"]:
            if day["date"] == tomorrow:
                day["weather"] = {
                    "temperature": 35.0,
                    "precipitation": 0.0,
                    "wind_speed": 5.0,
                    "weather_icons": ["hot"]
                }
            else:
                day["weather"] = {
                    "temperature": 20.0,
                    "precipitation": 0.0,
                    "wind_speed": 5.0,
                    "weather_icons": ["sunny"]
                }

        return schedule
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting test watering schedule: {str(e)}"
        )

@router.get("/user/{user_id}/test-weather", response_model=WateringScheduleOverview)
def get_watering_schedule_test_weather(user_id: int, db: Session = Depends(get_db)):
    """Test endpoint specifically for testing weather display with mock data"""
    try:
        logger.info(f"Getting test weather schedule for user {user_id}")
        schedule = schedule_service.get_watering_schedule(db, user_id)
        if not schedule:
            return {
                "schedule": [],
                "last_updated": datetime.utcnow().isoformat()
            }

        # Add mock weather data for the next day (high temperature)
        tomorrow = (datetime.utcnow() + timedelta(days=1)).date().isoformat()
        next_week = (datetime.utcnow() + timedelta(days=7)).date().isoformat()
        
        # Override weather data for all days and set weather adjustment flags
        for day in schedule["schedule"]:
            current_date = datetime.fromisoformat(day["date"]).date()
            
            # Set weather data based on the day
            if day["date"] == tomorrow:
                # Hot weather for tomorrow (35°C)
                day["weather"] = {
                    "temperature": 35.0,
                    "precipitation": 0.0,
                    "wind_speed": 5.0,
                    "weather_icons": ["hot"]
                }
            elif day["date"] == next_week:
                # Rainy weather for next week (15mm)
                day["weather"] = {
                    "temperature": 18.0,
                    "precipitation": 15.0,
                    "wind_speed": 8.0,
                    "weather_icons": ["rainy"]
                }
            else:
                # Normal weather for other days
                day["weather"] = {
                    "temperature": 20.0,
                    "precipitation": 0.0,
                    "wind_speed": 5.0,
                    "weather_icons": ["sunny"]
                }
            
            # Mark plants as weather adjusted based on conditions
            for section in day["sections"]:
                for group in section["groups"]:
                    for plant in group["plants"]:
                        # Reset weather adjustment flags
                        plant["weather_adjusted"] = False
                        plant["weather_info"] = {
                            "is_adjusted": False,
                            "original_date": None
                        }
                        
                        # Calculate weather impact
                        if day["date"] == tomorrow:
                            # Hot weather (35°C) - this takes precedence for all future schedules
                            temp_impact = (35 - 25) / 5  # = 2.0
                            rain_impact = 0
                            total_impact = temp_impact - rain_impact  # = 2.0
                            days_to_adjust = 3  # Since 2.0 > 1.2
                            
                            original_date = current_date
                            adjusted_date = original_date - timedelta(days=days_to_adjust)
                            plant["weather_adjusted"] = True
                            plant["weather_info"] = {
                                "is_adjusted": True,
                                "original_date": original_date.isoformat()
                            }
                            plant["next_watering"] = adjusted_date.isoformat()
                        elif day["date"] == next_week:
                            # Only apply rain adjustment if the plant is scheduled for after next week
                            # AND if it hasn't already been adjusted by hot weather
                            scheduled_date = datetime.fromisoformat(plant["next_watering"]).date()
                            if scheduled_date > current_date and not plant["weather_adjusted"]:
                                # Rainy weather (15mm)
                                temp_impact = 0
                                rain_impact = (15 - 10) / 5  # = 1.0
                                total_impact = temp_impact - rain_impact  # = -1.0
                                days_to_adjust = -2  # Since -1.0 < -0.8
                                
                                original_date = current_date
                                adjusted_date = original_date + timedelta(days=abs(days_to_adjust))
                                plant["weather_adjusted"] = True
                                plant["weather_info"] = {
                                    "is_adjusted": True,
                                    "original_date": original_date.isoformat()
                                }
                                plant["next_watering"] = adjusted_date.isoformat()

        return schedule
    except Exception as e:
        logger.error(f"Error in test weather endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting test weather schedule: {str(e)}"
        )
