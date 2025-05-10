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
    while True:  # Keep running until cancelled
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
        except asyncio.CancelledError:
            logger.info("Weather update task was cancelled")
            raise  # Re-raise to properly handle cancellation
        except Exception as e:
            logger.error(f"Error updating weather: {str(e)}")
        
        try:
            # Wait for the next update interval
            await asyncio.sleep(settings.WEATHER_UPDATE_INTERVAL * 3600)  # Convert hours to seconds
        except asyncio.CancelledError:
            logger.info("Weather update sleep was cancelled")
            raise  # Re-raise to properly handle cancellation
        except Exception as e:
            logger.error(f"Error in weather update sleep: {str(e)}")
            # If there's an error, wait a bit before retrying
            await asyncio.sleep(60)  # Wait 1 minute before retrying 