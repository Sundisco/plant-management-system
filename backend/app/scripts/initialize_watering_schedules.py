from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.watering_schedule import WateringSchedule
from app.models.user_plants import UserPlant
from app.models.plants import Plant
from app.models.watering import Watering
from app.services.weather_service import get_weather_forecast, update_weather_forecasts, should_update_forecast
from app.services.watering_adjustment import WateringAdjustment
from app.core.config import settings
import logging
from app.schemas.watering import WateringBase
from dotenv import load_dotenv
import os
import psycopg2

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

conn = psycopg2.connect(os.environ["DATABASE_URL"])

def sync_watering_schedules():
    """Sync watering schedules with current user plants, handling additions and removals"""
    db = SessionLocal()
    try:
        # Update weather forecasts
        if should_update_forecast(db, settings.WEATHER_LOCATION):
            logger.info("Updating weather forecasts")
            update_weather_forecasts(db, settings.WEATHER_LOCATION)

        # Get weather forecast for next 7 days
        weather_forecasts = get_weather_forecast(
            db,
            settings.WEATHER_LOCATION,
            datetime.now(),
            datetime.now() + timedelta(days=7)
        )

        # Get all current user plants
        current_user_plants = db.query(UserPlant).all()
        current_plant_ids = {(up.user_id, up.plant_id) for up in current_user_plants}
        logger.info(f"Found {len(current_user_plants)} current user plants")

        # Get all active schedules
        active_schedules = db.query(WateringSchedule).filter(
            WateringSchedule.completed == False,
            WateringSchedule.scheduled_date >= datetime.now().date()
        ).all()
        
        # Find schedules to remove (plants that no longer exist)
        existing_schedule_keys = {(s.user_id, s.plant_id) for s in active_schedules}
        schedules_to_remove = existing_schedule_keys - current_plant_ids
        
        if schedules_to_remove:
            logger.info(f"Removing {len(schedules_to_remove)} schedules for deleted plants")
            for user_id, plant_id in schedules_to_remove:
                db.query(WateringSchedule).filter(
                    WateringSchedule.user_id == user_id,
                    WateringSchedule.plant_id == plant_id,
                    WateringSchedule.completed == False
                ).delete()

        # Find plants that need new schedules
        plants_to_add = current_plant_ids - existing_schedule_keys
        logger.info(f"Adding schedules for {len(plants_to_add)} new plants")

        # Create new schedules for added plants
        for user_id, plant_id in plants_to_add:
            plant = db.query(Plant).filter(Plant.id == plant_id).first()
            if not plant:
                logger.warning(f"Plant {plant_id} not found")
                continue

            watering_info = db.query(Watering).filter(Watering.plant_id == plant.id).first()
            if not watering_info:
                logger.warning(f"No watering info found for plant {plant.id}")
                continue

            # Calculate base frequency (adjusted for drought tolerance)
            base_frequency = watering_info.frequency_days
            if watering_info.drought_tolerant:
                base_frequency = int(base_frequency * 1.5)  # Drought tolerant plants can wait 50% longer

            # Create base watering requirements
            base_watering = WateringBase(
                plant_id=plant.id,
                frequency_days=base_frequency,
                depth_mm=watering_info.depth_mm,
                volume_feet=watering_info.volume_feet,
                period=watering_info.period,
                drought_tolerant=watering_info.drought_tolerant,
                soil=watering_info.soil
            )

            # Get the first forecast
            if weather_forecasts:
                forecast = min(weather_forecasts, key=lambda x: abs(x.timestamp.hour - 12))
                adjustment = WateringAdjustment.calculate_adjustment(base_watering, forecast)
                
                # Adjust frequency based on weather
                adjusted_frequency = base_frequency + adjustment["frequency_adjustment"]
                adjusted_volume = watering_info.volume_feet * adjustment["volume_adjustment"]
            else:
                adjusted_frequency = base_frequency
                adjusted_volume = watering_info.volume_feet

            # Calculate scheduled dates
            scheduled_date = datetime.now().date() + timedelta(days=adjusted_frequency)
            next_scheduled_date = scheduled_date + timedelta(days=adjusted_frequency)

            # Create watering schedule
            schedule = WateringSchedule(
                user_id=user_id,
                plant_id=plant.id,
                scheduled_date=scheduled_date,
                water_needed=True,
                volume_needed=adjusted_volume,
                weather_dependent=True,
                next_scheduled_date=next_scheduled_date,
                completed=False
            )

            # Add to database
            db.add(schedule)
            logger.info(f"Created new schedule for plant {plant.id} (user {user_id})")

        # Commit all changes
        db.commit()
        logger.info("Successfully synced watering schedules")

    except Exception as e:
        logger.error(f"Error syncing watering schedules: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    sync_watering_schedules() 