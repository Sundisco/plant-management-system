import pytest
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from app.models.watering_schedule import WateringSchedule
from app.models.weather_forecast import WeatherForecast
from app.models.user_plants import UserPlant
from app.models.plants import Plant
from app.models.watering import Watering
from app.services.watering_schedule import get_watering_schedule
from starlette.testclient import TestClient
from app.main import app
from app.database import SessionLocal
import json

@pytest.fixture
def db():
    """Create a fresh database session for each test"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """Create a test client"""
    with TestClient(app) as test_client:
        yield test_client

def test_weather_adjustment_flow(client: TestClient, db: Session):
    """Test the complete flow of weather-based schedule adjustments"""
    # Create test data
    today = date.today()
    user_id = 1
    plant_id = 1
    
    # Create a plant with watering info
    plant = Plant(
        id=plant_id,
        common_name="Test Plant",
        scientific_name=["Test Scientific"]
    )
    db.add(plant)
    
    watering_info = Watering(
        plant_id=plant_id,
        frequency_days=7,
        depth_mm=10,
        volume_feet=1.0
    )
    db.add(watering_info)
    
    # Create user plant
    user_plant = UserPlant(
        user_id=user_id,
        plant_id=plant_id,
        section="A"
    )
    db.add(user_plant)
    
    # Create a schedule for tomorrow
    schedule = WateringSchedule(
        user_id=user_id,
        plant_id=plant_id,
        scheduled_date=today + timedelta(days=1),
        water_needed=True,
        completed=False
    )
    db.add(schedule)
    
    # Create weather forecast with high temperature
    forecast = WeatherForecast(
        timestamp=datetime.now(),
        temperature=30.0,  # High temperature
        precipitation=0.0,
        wind_speed=5.0
    )
    db.add(forecast)
    db.commit()
    
    # Test API endpoint
    response = client.get(f"/api/watering-schedule/watering-schedule/user/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "schedule" in data
    assert len(data["schedule"]) > 0
    
    # Find the adjusted schedule
    found_adjusted = False
    for day in data["schedule"]:
        if day["date"] == (today + timedelta(days=1)).isoformat():
            for section in day["sections"]:
                if section["name"] == "A":
                    for plant in section["plants"]:
                        if plant["plant_id"] == plant_id:
                            assert plant["weather_adjusted"] == True
                            found_adjusted = True
                            break
    
    assert found_adjusted, "Could not find weather-adjusted schedule"

def test_multiple_weather_conditions(client: TestClient, db: Session):
    """Test different weather conditions and their impact on schedules"""
    today = date.today()
    user_id = 1
    plant_id = 1
    
    # Create test data
    plant = Plant(
        id=plant_id,
        common_name="Test Plant",
        scientific_name=["Test Scientific"]
    )
    db.add(plant)
    
    watering_info = Watering(
        plant_id=plant_id,
        frequency_days=7,
        depth_mm=10,
        volume_feet=1.0
    )
    db.add(watering_info)
    
    user_plant = UserPlant(
        user_id=user_id,
        plant_id=plant_id,
        section="A"
    )
    db.add(user_plant)
    
    # Create schedules for different days
    schedules = []
    for i in range(1, 4):
        schedule = WateringSchedule(
            user_id=user_id,
            plant_id=plant_id,
            scheduled_date=today + timedelta(days=i),
            water_needed=True,
            completed=False
        )
        schedules.append(schedule)
        db.add(schedule)
    
    # Create different weather conditions
    weather_conditions = [
        (30.0, 0.0, 5.0),   # Hot and dry
        (20.0, 15.0, 5.0),  # Rainy
        (22.0, 2.0, 5.0),   # Normal
    ]
    
    for i, (temp, precip, wind) in enumerate(weather_conditions):
        forecast = WeatherForecast(
            timestamp=datetime.now() + timedelta(days=i),
            temperature=temp,
            precipitation=precip,
            wind_speed=wind
        )
        db.add(forecast)
    
    db.commit()
    
    # Test API endpoint
    response = client.get(f"/api/watering-schedule/watering-schedule/user/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "schedule" in data
    
    # Verify adjustments for each condition
    for i, (temp, precip, wind) in enumerate(weather_conditions):
        day = today + timedelta(days=i+1)
        day_str = day.isoformat()
        
        # Find the schedule for this day
        for schedule_day in data["schedule"]:
            if schedule_day["date"] == day_str:
                for section in schedule_day["sections"]:
                    if section["name"] == "A":
                        for plant in section["plants"]:
                            if plant["plant_id"] == plant_id:
                                # Hot and dry should be adjusted forward
                                if temp > 25 and precip < 5:
                                    assert plant["weather_adjusted"] == True
                                # Rainy should be adjusted backward
                                elif precip > 10:
                                    assert plant["weather_adjusted"] == True
                                # Normal conditions might not need adjustment
                                else:
                                    assert plant["weather_adjusted"] == False 