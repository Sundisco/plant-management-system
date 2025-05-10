import asyncio
import logging
from app.core.config import settings
from app.services.weather_service import update_weather_forecasts
from app.database import SessionLocal

logger = logging.getLogger(__name__)

async def update_weather_periodic():
    """Periodically update weather forecasts"""
    while True:
        try:
            logger.info("Starting weather update")
            db = SessionLocal()
            try:
                await update_weather_forecasts(db, settings.WEATHER_LOCATION)
                logger.info("Weather update completed successfully")
            except Exception as e:
                logger.error(f"Error updating weather forecasts: {str(e)}")
            finally:
                db.close()
            
            # Sleep with cancellation handling
            try:
                await asyncio.sleep(settings.WEATHER_UPDATE_INTERVAL * 3600)  # Convert hours to seconds
            except asyncio.CancelledError:
                logger.info("Weather update task was cancelled")
                raise
        except asyncio.CancelledError:
            logger.info("Weather update task was cancelled")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in weather update task: {str(e)}")
            # Sleep for a shorter time on error
            try:
                await asyncio.sleep(300)  # 5 minutes
            except asyncio.CancelledError:
                logger.info("Weather update task was cancelled")
                raise

def start_scheduler():
    """Start the background tasks"""
    try:
        loop = asyncio.get_event_loop()
        weather_task = loop.create_task(update_weather_periodic())
        
        # Add task to the loop
        loop.create_task(weather_task)
        
        logger.info("Scheduler started successfully")
        return weather_task
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise 