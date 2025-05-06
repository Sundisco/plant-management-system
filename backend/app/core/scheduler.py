from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services import weather_service
from app.core.config import settings
import asyncio
from datetime import datetime, timedelta

async def update_weather_periodic(background_tasks: BackgroundTasks):
    """Periodic task to update weather data"""
    db = SessionLocal()
    try:
        await weather_service.update_weather_forecasts(db, settings.WEATHER_LOCATION)
    finally:
        db.close()
    
    # Schedule the next update
    next_update = datetime.now() + timedelta(hours=settings.WEATHER_UPDATE_INTERVAL)
    background_tasks.add_task(
        asyncio.sleep,
        settings.WEATHER_UPDATE_INTERVAL * 3600,  # Convert hours to seconds
        update_weather_periodic,
        background_tasks
    ) 