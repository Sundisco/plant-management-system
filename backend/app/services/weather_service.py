from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.weather_forecast import WeatherForecast
from app.schemas.weather_forecast import WeatherForecastCreate
from fastapi import HTTPException
from datetime import datetime, timedelta
import httpx
from typing import List
import logging
import traceback
import asyncio
from app.core.config import settings

# Constants
LAT = 56  # Denmark latitude
LON = 10  # Denmark longitude
WEATHER_API_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m,precipitation,wind_speed_10m&timezone=Europe%2FLondon"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def fetch_weather_data() -> List[dict]:
    """Fetch weather forecast from Open-Meteo API"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={settings.WEATHER_LAT}&longitude={settings.WEATHER_LON}&hourly=temperature_2m,precipitation,wind_speed_10m&timezone=Europe%2FLondon"
    
    try:
        logger.info("Fetching weather data from Open-Meteo API")
        async with httpx.AsyncClient(timeout=10.0) as client:  # 10 second timeout
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                forecasts = []
                times = data['hourly']['time']
                temps = data['hourly']['temperature_2m']
                precips = data['hourly']['precipitation']
                winds = data['hourly']['wind_speed_10m']
                
                for i in range(len(times)):
                    forecasts.append({
                        "timestamp": datetime.fromisoformat(times[i]),
                        "location": settings.WEATHER_LOCATION,
                        "temperature": temps[i],
                        "precipitation": precips[i],
                        "wind_speed": winds[i]
                    })
                logger.info(f"Successfully fetched {len(forecasts)} weather forecasts")
                return forecasts
            except asyncio.CancelledError:
                logger.info("Weather data fetch was cancelled")
                raise
            except httpx.TimeoutException:
                logger.error("Weather data fetch timed out")
                raise HTTPException(status_code=504, detail="Weather data fetch timed out")
            except httpx.HTTPError as e:
                logger.error(f"HTTP error fetching weather data: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")
    except asyncio.CancelledError:
        logger.info("Weather data fetch was cancelled")
        raise
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

def create_weather_forecast(db: Session, forecast: WeatherForecastCreate):
    try:
        logger.debug(f"Creating weather forecast for {forecast.timestamp}")
        db_forecast = WeatherForecast(**forecast.model_dump())
        db.add(db_forecast)
        db.commit()
        db.refresh(db_forecast)
        return db_forecast
    except IntegrityError:
        logger.debug(f"Weather forecast already exists for {forecast.timestamp}")
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Weather forecast already exists for this timestamp and location"
        )
    except Exception as e:
        logger.error(f"Error creating weather forecast: {str(e)}")
        db.rollback()
        raise

def get_weather_forecast(
    db: Session,
    location: str,
    start_date: datetime = None,
    end_date: datetime = None
):
    try:
        logger.debug(f"Getting weather forecast for {location}")
        query = db.query(WeatherForecast).filter(WeatherForecast.location == location)
        
        if start_date:
            query = query.filter(WeatherForecast.timestamp >= start_date)
        if end_date:
            query = query.filter(WeatherForecast.timestamp <= end_date)
        
        forecasts = query.order_by(WeatherForecast.timestamp).all()
        logger.debug(f"Found {len(forecasts)} weather forecasts")
        return forecasts
    except Exception as e:
        logger.error(f"Error getting weather forecast: {str(e)}")
        raise

async def update_weather_forecasts(db: Session, location: str):
    """Fetch new weather data and update database"""
    try:
        logger.info(f"Updating weather forecasts for {location}")
        try:
            forecasts = await fetch_weather_data()
        except asyncio.CancelledError:
            logger.info("Weather update was cancelled")
            raise
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return []  # Return empty list instead of raising
        
        updated_count = 0
        
        for forecast_data in forecasts:
            try:
                forecast = WeatherForecastCreate(**forecast_data)
                try:
                    create_weather_forecast(db, forecast)
                    updated_count += 1
                except HTTPException as e:
                    if e.status_code == 400:  # Already exists
                        continue
                    logger.error(f"Error creating forecast: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error creating forecast: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing forecast data: {str(e)}")
                continue
            
        logger.info(f"Successfully updated {updated_count} weather forecasts")
        return get_weather_forecast(
            db,
            location,
            datetime.now(),
            datetime.now() + timedelta(days=7)
        )
    except asyncio.CancelledError:
        logger.info("Weather update was cancelled")
        raise
    except Exception as e:
        logger.error(f"Error updating weather forecasts: {str(e)}")
        return []  # Return empty list instead of raising

def should_update_forecast(db: Session, location: str) -> bool:
    """Check if we need to update the forecast"""
    try:
        latest = db.query(WeatherForecast)\
            .filter(WeatherForecast.location == location)\
            .order_by(WeatherForecast.timestamp.desc())\
            .first()
        
        if not latest:
            logger.info("No weather forecasts found, update needed")
            return True
        
        # Update if latest forecast is more than 6 hours old
        needs_update = datetime.now(latest.timestamp.tzinfo) - latest.timestamp > timedelta(hours=6)
        logger.debug(f"Latest forecast is from {latest.timestamp}, update needed: {needs_update}")
        return needs_update
    except Exception as e:
        logger.error(f"Error checking if forecast needs update: {str(e)}")
        return True  # If there's an error, assume we need to update 