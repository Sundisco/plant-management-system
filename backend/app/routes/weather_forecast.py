from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.services import weather_service
from app.schemas.weather_forecast import WeatherForecast
from app.database import get_db

router = APIRouter()

@router.get("/{location}", response_model=List[WeatherForecast])
async def get_weather_forecast(
    location: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Check if we need to update the forecast
    if weather_service.should_update_forecast(db, location):
        # Update forecasts in the background
        background_tasks.add_task(weather_service.update_weather_forecasts, db, location)
    
    # Return current forecasts from database
    forecasts = weather_service.get_weather_forecast(
        db,
        location,
        datetime.now(),
        datetime.now() + timedelta(days=7)
    )
    
    if not forecasts:
        # If no forecasts available, fetch them immediately
        forecasts = await weather_service.update_weather_forecasts(db, location)
    
    return forecasts

@router.get("/{location}/historical", response_model=List[WeatherForecast])
def get_historical_weather(
    location: str,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    return weather_service.get_weather_forecast(db, location, start_date, end_date) 