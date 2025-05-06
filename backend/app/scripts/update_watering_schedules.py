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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_watering_schedules():
    """Update watering schedules based on weather forecasts"""
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

        # Get all active schedules
        active_schedules = db.query(WateringSchedule).filter(
            WateringSchedule.completed == False,
            WateringSchedule.scheduled_date >= datetime.now().date()
        ).all()

        logger.info(f"Found {len(active_schedules)} active schedules")

        for schedule in active_schedules:
            plant = db.query(Plant).filter(Plant.id == schedule.plant_id).first()
            if not plant:
                logger.warning(f"Plant {schedule.plant_id} not found")
                continue

            watering_info = db.query(Watering).filter(Watering.plant_id == plant.id).first()
            if not watering_info:
                logger.warning(f"No watering info found for plant {plant.id}")
                continue

            # Calculate base frequency (adjusted for drought tolerance)
            base_frequency = watering_info.frequency_days
            if watering_info.drought_tolerant:
                base_frequency = int(base_frequency * 1.5)

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

            # Get forecast for scheduled date
            day_forecasts = [f for f in weather_forecasts if f.timestamp.date() == schedule.scheduled_date]
            if day_forecasts:
                forecast = min(day_forecasts, key=lambda x: abs(x.timestamp.hour - 12))
                adjustment = WateringAdjustment.calculate_adjustment(base_watering, forecast)
                
                # Update schedule based on weather
                if adjustment["skip_watering"]:
                    # Postpone watering due to heavy rain
                    new_scheduled_date = schedule.scheduled_date + timedelta(days=1)
                    schedule.scheduled_date = new_scheduled_date
                    schedule.next_scheduled_date = new_scheduled_date + timedelta(days=base_frequency)
                    schedule.water_needed = False
                    logger.info(f"Postponed watering for plant {plant.id} due to heavy rain")
                else:
                    # Adjust volume based on weather
                    schedule.volume_needed = watering_info.volume_feet * adjustment["volume_adjustment"]
                    schedule.water_needed = True
                    logger.info(f"Adjusted volume for plant {plant.id} based on weather")

        # Commit all changes
        db.commit()
        logger.info("Successfully updated watering schedules")

    except Exception as e:
        logger.error(f"Error updating watering schedules: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_watering_schedules() 