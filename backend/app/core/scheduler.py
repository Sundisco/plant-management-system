from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services import weather_service
from app.core.config import settings
import asyncio

@repeat_every(seconds=60 * 60 * settings.WEATHER_UPDATE_INTERVAL)  # Update every 6 hours
async def update_weather_periodic():
    """Periodic task to update weather data"""
    db = SessionLocal()
    try:
        await weather_service.update_weather_forecasts(db, settings.WEATHER_LOCATION)
    finally:
        db.close() 