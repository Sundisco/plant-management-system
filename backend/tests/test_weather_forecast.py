import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from httpx import AsyncClient
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services import weather_service
from app.models.weather_forecast import WeatherForecast
from app.schemas.weather_forecast import WeatherForecastCreate
from app.main import app
from unittest.mock import patch, AsyncMock

# Sample weather data for mocking API responses
MOCK_WEATHER_RESPONSE = {
    "hourly": {
        "time": [
            "2024-03-20T00:00",
            "2024-03-20T01:00",
            "2024-03-20T02:00"
        ],
        "temperature_2m": [10.5, 11.0, 10.8],
        "precipitation": [0.0, 0.2, 0.0],
        "wind_speed_10m": [5.2, 5.5, 5.1]
    }
}

@pytest.fixture
async def mock_weather_api():
    """Mock the external weather API calls"""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_WEATHER_RESPONSE
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch('httpx.AsyncClient') as mock:
        mock.return_value = mock_client
        mock.return_value.__aenter__ = mock_client.__aenter__
        yield mock

@pytest.fixture
def sample_weather_forecast(db: Session):
    """Create a sample weather forecast in the database"""
    forecast = WeatherForecast(
        timestamp=datetime.now(),
        location="Denmark",
        temperature=20.5,
        precipitation=0.0,
        wind_speed=5.2
    )
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    return forecast

@pytest.mark.asyncio
async def test_fetch_weather_data(mock_weather_api):
    """Test fetching weather data from API"""
    forecasts = await weather_service.fetch_weather_data()
    
    assert isinstance(forecasts, list)
    assert len(forecasts) == 3
    assert forecasts[0]["location"] == "Denmark"
    assert isinstance(forecasts[0]["temperature"], float)
    assert forecasts[0]["temperature"] == 10.5  # Check actual value from mock

def test_create_weather_forecast(db: Session):
    """Test creating a new weather forecast"""
    forecast_data = {
        "timestamp": datetime.now(),
        "location": "Denmark",
        "temperature": 20.5,
        "precipitation": 0.0,
        "wind_speed": 5.2
    }
    
    forecast = WeatherForecastCreate(**forecast_data)
    db_forecast = weather_service.create_weather_forecast(db, forecast)
    
    assert db_forecast.location == "Denmark"
    assert db_forecast.temperature == 20.5

def test_create_duplicate_forecast(db: Session, sample_weather_forecast):
    """Test handling of duplicate weather forecasts"""
    forecast_data = {
        "timestamp": sample_weather_forecast.timestamp,
        "location": sample_weather_forecast.location,
        "temperature": 21.0,
        "precipitation": 0.0,
        "wind_speed": 5.2
    }
    
    forecast = WeatherForecastCreate(**forecast_data)
    
    with pytest.raises(Exception):
        weather_service.create_weather_forecast(db, forecast)

def test_get_weather_forecast(db: Session, sample_weather_forecast):
    """Test retrieving weather forecasts"""
    forecasts = weather_service.get_weather_forecast(
        db,
        location="Denmark",
        start_date=datetime.now() - timedelta(days=1),
        end_date=datetime.now() + timedelta(days=1)
    )
    
    assert len(forecasts) > 0
    assert forecasts[0].location == "Denmark"

def test_should_update_forecast(db: Session, sample_weather_forecast):
    """Test the update check logic"""
    # Recent forecast
    assert not weather_service.should_update_forecast(db, "Denmark")
    
    # Old forecast
    sample_weather_forecast.timestamp = datetime.now() - timedelta(hours=7)
    db.commit()
    assert weather_service.should_update_forecast(db, "Denmark")

@pytest.mark.asyncio
async def test_weather_endpoint(async_client, mock_weather_api, db: Session):
    """Test the weather API endpoint"""
    # Create a sample forecast first
    forecast = WeatherForecast(
        timestamp=datetime.now(),
        location="Denmark",
        temperature=20.5,
        precipitation=0.0,
        wind_speed=5.2
    )
    db.add(forecast)
    db.commit()

    response = await async_client.get("/api/weather/Denmark")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_historical_weather_endpoint(
    async_client,
    sample_weather_forecast,
    db: Session
):
    """Test the historical weather endpoint"""
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() + timedelta(days=1)
    
    response = await async_client.get(
        "/api/weather/Denmark/historical",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_scheduler_update(mock_weather_api, db: Session):
    """Test the scheduled weather update"""
    from app.core.scheduler import update_weather_periodic
    
    # Create initial data to ensure there's something to return
    forecast = WeatherForecast(
        timestamp=datetime.now(),
        location="Denmark",
        temperature=20.5,
        precipitation=0.0,
        wind_speed=5.2
    )
    db.add(forecast)
    db.commit()
    
    await update_weather_periodic()
    
    forecasts = weather_service.get_weather_forecast(
        db,
        "Denmark",
        datetime.now() - timedelta(hours=1),
        datetime.now() + timedelta(days=1)
    )
    
    assert len(forecasts) > 0 

@router.get("/weather/summary")
def get_weather_summary(db: Session = Depends(get_db)):
    """Get weather summary for charts/graphs"""
    return {
        "daily_temperatures": ...,
        "precipitation_forecast": ...,
        "wind_conditions": ...
    } 