from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.models.watering_schedule import WateringSchedule
from app.schemas.watering_schedule import WateringScheduleCreate, WateringScheduleUpdate
from fastapi import HTTPException
from datetime import date, datetime, timedelta
from app.models.user_plants import UserPlant
from app.models.plants import Plant
from app.models.watering import Watering
from app.models.users import User
from app.schemas.watering import WateringBase
from app.services.weather_service import get_weather_forecast, update_weather_forecasts, should_update_forecast
from app.services.watering_adjustment import WateringAdjustment
from app.core.config import settings
import logging
import asyncio
import traceback
from typing import List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_watering_schedule(db: Session, user_id: int, plant_id: int):
    """Create a new watering schedule for a plant"""
    try:
        logger.info(f"Creating watering schedule for user {user_id}, plant {plant_id}")
        
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            raise ValueError("User not found")
        
        # Get plant and its watering requirements
        plant = db.query(Plant).filter(Plant.id == plant_id).first()
        if not plant:
            logger.error(f"Plant {plant_id} not found")
            raise ValueError("Plant not found")
        
        watering_info = db.query(Watering).filter(Watering.plant_id == plant_id).first()
        if not watering_info:
            logger.error(f"No watering information found for plant {plant_id}")
            raise ValueError("Plant watering information not found")

        # Update weather forecasts if needed
        if should_update_forecast(db, settings.WEATHER_LOCATION):
            logger.info("Updating weather forecasts")
            asyncio.run(update_weather_forecasts(db, settings.WEATHER_LOCATION))

        # Get weather forecast for the next week
        weather_forecasts = get_weather_forecast(
            db,
            settings.WEATHER_LOCATION,
            datetime.now(),
            datetime.now() + timedelta(days=7)
        )
        logger.debug(f"Got {len(weather_forecasts)} weather forecasts")

        # Create base watering requirements
        base_watering = WateringBase(
            plant_id=plant_id,
            frequency_days=watering_info.frequency_days,
            depth_mm=watering_info.depth_mm,
            volume_feet=watering_info.volume_feet,
            period=watering_info.period,
            drought_tolerant=watering_info.drought_tolerant,
            soil=watering_info.soil
        )

        # Get adjusted schedule
        adjusted_schedule = WateringAdjustment.get_adjusted_schedule(
            base_watering,
            weather_forecasts
        )
        logger.info(f"Generated adjusted schedule with {len(adjusted_schedule)} entries")

        # Create watering schedule entries
        for day_schedule in adjusted_schedule:
            if not day_schedule["skip_watering"]:
                schedule = WateringSchedule(
                    user_id=user_id,
                    plant_id=plant_id,
                    scheduled_date=day_schedule["date"],
                    water_needed=True,
                    volume_needed=day_schedule["adjusted_volume"],
                    weather_dependent=True,
                    next_scheduled_date=day_schedule["date"] + timedelta(days=watering_info.frequency_days)
                )
                db.add(schedule)

        db.commit()
        logger.info("Successfully created watering schedule")
        return adjusted_schedule
    except Exception as e:
        logger.error(f"Error creating watering schedule: {str(e)}")
        raise

def get_user_watering_schedule(db: Session, user_id: int) -> List[dict]:
    """Get watering schedule for all plants of a user"""
    try:
        logger.info(f"Getting watering schedule for user {user_id}")
        
        # Get all user plants with their last watering date - optimized query
        user_plants = (
            db.query(UserPlant)
            .filter(UserPlant.user_id == user_id)
            .options(
                joinedload(UserPlant.plant).joinedload(Plant.watering_info)  # Use watering_info instead of watering
            )
            .all()
        )
        
        if not user_plants:
            logger.info(f"No plants found for user {user_id}")
            return []
        
        # Get weather forecast for next 7 days
        try:
            weather_forecast = get_weather_forecast(
                db,
                "Denmark",  # Use the configured location
                datetime.now(),
                datetime.now() + timedelta(days=7)
            )
        except Exception as e:
            logger.error(f"Error getting weather forecast: {str(e)}")
            weather_forecast = []  # Continue without weather data
        
        # Process each plant
        schedule = []
        for user_plant in user_plants:
            try:
                if not user_plant.plant or not user_plant.plant.watering_info:
                    logger.warning(f"Missing plant or watering info for user_plant {user_plant.id}")
                    continue
                
                # Get watering info
                watering_info = user_plant.plant.watering_info
                
                # Calculate next watering date
                next_watering = calculate_next_watering(
                    watering_info,
                    weather_forecast
                )
                
                if next_watering:
                    schedule.append({
                        "plant_id": user_plant.plant_id,
                        "plant_name": user_plant.plant.common_name,
                        "next_watering": next_watering,
                        "section": user_plant.section
                    })
            except Exception as e:
                logger.error(f"Error processing plant {user_plant.plant_id}: {str(e)}")
                continue
        
        logger.info(f"Generated watering schedule with {len(schedule)} entries")
        return schedule
    except Exception as e:
        logger.error(f"Error in get_user_watering_schedule: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating watering schedule: {str(e)}"
        )

def calculate_next_watering(watering_info: Watering, weather_forecast: List[dict]) -> Optional[datetime]:
    """Calculate next watering date based on watering info and weather forecast"""
    try:
        if not watering_info:
            return None
            
        # Get base watering frequency in days
        frequency = watering_info.frequency_days
        
        # Adjust for weather conditions
        if weather_forecast:
            # Check next 3 days of forecast
            for i in range(min(3, len(weather_forecast))):
                forecast = weather_forecast[i]
                if forecast['precipitation'] > 5:  # If significant rain
                    frequency += 1  # Delay watering by one day
                if forecast['temperature'] > 25:  # If hot
                    frequency -= 0.5  # Water more frequently
        
        # Calculate next watering date
        next_watering = datetime.now() + timedelta(days=max(1, frequency))
        return next_watering
    except Exception as e:
        logger.error(f"Error calculating next watering: {str(e)}")
        return None

def get_schedule(db: Session, schedule_id: int):
    return db.query(WateringSchedule).filter(WateringSchedule.id == schedule_id).first()

def get_user_schedules(db: Session, user_id: int, date_from: date = None, date_to: date = None):
    query = db.query(WateringSchedule).filter(WateringSchedule.user_id == user_id)
    
    if date_from:
        query = query.filter(WateringSchedule.scheduled_date >= date_from)
    if date_to:
        query = query.filter(WateringSchedule.scheduled_date <= date_to)
        
    return query.order_by(WateringSchedule.scheduled_date).all()

def get_user_plant_schedules(
    db: Session, user_id: int, plant_id: int, 
    date_from: date = None, date_to: date = None
):
    query = db.query(WateringSchedule).filter(
        WateringSchedule.user_id == user_id,
        WateringSchedule.plant_id == plant_id
    )
    
    if date_from:
        query = query.filter(WateringSchedule.scheduled_date >= date_from)
    if date_to:
        query = query.filter(WateringSchedule.scheduled_date <= date_to)
        
    return query.order_by(WateringSchedule.scheduled_date).all()

def update_schedule(db: Session, schedule_id: int, schedule_update: WateringScheduleUpdate):
    db_schedule = get_schedule(db, schedule_id)
    if not db_schedule:
        return None
    
    update_data = schedule_update.model_dump(exclude_unset=True)
    
    if schedule_update.completed:
        update_data["completion_timestamp"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_schedule(db: Session, schedule_id: int):
    db_schedule = get_schedule(db, schedule_id)
    if not db_schedule:
        return False
    
    db.delete(db_schedule)
    db.commit()
    return True

def get_upcoming_schedules(db: Session, user_id: int, days: int = 7):
    today = date.today()
    end_date = today + timedelta(days=days)
    return db.query(WateringSchedule).filter(
        WateringSchedule.user_id == user_id,
        WateringSchedule.scheduled_date >= today,
        WateringSchedule.scheduled_date <= end_date,
        WateringSchedule.completed == False
    ).order_by(WateringSchedule.scheduled_date).all()
