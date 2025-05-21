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
    """Sync watering schedules for all user plants"""
    try:
        db = SessionLocal()
        today = datetime.now().date()

        # Get all current user plants
        user_plants = db.query(UserPlant).all()
        logger.info(f"Found {len(user_plants)} current user plants")

        # Get all current schedules
        current_schedules = db.query(WateringSchedule).all()
        current_plant_ids = {schedule.plant_id for schedule in current_schedules}
        
        # Find plants that need schedules
        plants_needing_schedules = [
            up for up in user_plants 
            if up.plant_id not in current_plant_ids
        ]
        
        # Remove schedules for deleted plants
        deleted_plant_ids = current_plant_ids - {up.plant_id for up in user_plants}
        if deleted_plant_ids:
            logger.info(f"Removing {len(deleted_plant_ids)} schedules for deleted plants")
            db.query(WateringSchedule).filter(
                WateringSchedule.plant_id.in_(deleted_plant_ids)
            ).delete()

        # Add schedules for new plants
        if plants_needing_schedules:
            logger.info(f"Adding schedules for {len(plants_needing_schedules)} new plants")
            for user_plant in plants_needing_schedules:
                if not user_plant.plant or not user_plant.plant.watering_info:
                    continue

                watering_info = user_plant.plant.watering_info
                base_frequency = watering_info.frequency_days

                # Create base watering requirements
                base_watering = WateringBase(
                    plant_id=user_plant.plant_id,
                    frequency_days=base_frequency,
                    depth_mm=watering_info.depth_mm,
                    volume_feet=watering_info.volume_feet,
                    period=watering_info.period,
                    drought_tolerant=watering_info.drought_tolerant,
                    soil=watering_info.soil if watering_info.soil else []
                )
                
                # Check if a schedule already exists for this plant
                existing_schedule = db.query(WateringSchedule).filter(
                    WateringSchedule.user_id == user_plant.user_id,
                    WateringSchedule.plant_id == user_plant.plant_id,
                    WateringSchedule.scheduled_date == today
                ).first()
                
                if existing_schedule:
                    logger.info(f"Schedule already exists for plant {user_plant.plant_id} on {today}")
                    continue
                
                # Create initial schedule for today
                schedule = WateringSchedule(
                    user_id=user_plant.user_id,
                    plant_id=user_plant.plant_id,
                    scheduled_date=today,
                    completed=False,
                    completion_timestamp=None,
                    water_needed=True,
                    volume_needed=watering_info.volume_feet,
                    next_scheduled_date=None
                )

                db.add(schedule)
                logger.info(f"Created new schedule for plant {user_plant.plant_id} (user {user_plant.user_id})")

        # Ensure no schedules are marked as completed without a completion timestamp
        db.query(WateringSchedule).filter(
            WateringSchedule.completed == True,
            WateringSchedule.completion_timestamp == None
        ).update({
            "completed": False
        })
        
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