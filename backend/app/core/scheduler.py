from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services import weather_service
from app.core.config import settings
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def update_weather_periodic(background_tasks: BackgroundTasks):
    """Periodic task to update weather data"""
    try:
        # Use a timeout for the database session
        async with asyncio.timeout(30):  # 30 second timeout
            db = SessionLocal()
            try:
                await weather_service.update_weather_forecasts(db, settings.WEATHER_LOCATION)
            finally:
                db.close()
    except asyncio.TimeoutError:
        logger.error("Weather update timed out")
    except Exception as e:
        logger.error(f"Error updating weather: {str(e)}")
    
    # Schedule the next update
    try:
        next_update = datetime.now() + timedelta(hours=settings.WEATHER_UPDATE_INTERVAL)
        await asyncio.sleep(settings.WEATHER_UPDATE_INTERVAL * 3600)  # Convert hours to seconds
        asyncio.create_task(update_weather_periodic(background_tasks))
    except Exception as e:
        logger.error(f"Error scheduling next weather update: {str(e)}") 