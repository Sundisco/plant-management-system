import pytest
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from app.models.watering_schedule import WateringSchedule
from app.models.weather_forecast import WeatherForecast
from app.models.user_plants import UserPlant
from app.models.plants import Plant
from app.models.watering import Watering
from app.models.users import User
from app.services.watering_schedule import get_watering_schedule

def test_weather_adjustment_db_flow(db: Session):
    """Test the database operations for weather-based schedule adjustments"""
    # Create test data
    today = date.today()
    user_id = 1
    plant_id = 1
    
    # Create a user first
    user = User(
        id=user_id,
        email="test@example.com",
        hashed_password="testpassword",
        is_active=True
    )
    db.add(user)
    db.flush()  # Flush to get the user ID
    
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
    
    # Verify the data was saved correctly
    saved_schedule = db.query(WateringSchedule).filter(
        WateringSchedule.user_id == user_id,
        WateringSchedule.plant_id == plant_id
    ).first()
    
    assert saved_schedule is not None
    assert saved_schedule.scheduled_date == today + timedelta(days=1)
    assert saved_schedule.water_needed == True
    assert saved_schedule.completed == False

def test_multiple_weather_conditions_db(db: Session):
    """Test different weather conditions in the database"""
    today = date.today()
    user_id = 1
    plant_id = 1
    
    # Create a user first
    user = User(
        id=user_id,
        email="test@example.com",
        hashed_password="testpassword",
        is_active=True
    )
    db.add(user)
    db.flush()  # Flush to get the user ID
    
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
    
    # Verify the data was saved correctly
    saved_schedules = db.query(WateringSchedule).filter(
        WateringSchedule.user_id == user_id,
        WateringSchedule.plant_id == plant_id
    ).all()
    
    assert len(saved_schedules) == 3
    
    saved_forecasts = db.query(WeatherForecast).order_by(WeatherForecast.timestamp).all()
    assert len(saved_forecasts) == 3
    
    # Verify weather conditions
    for i, (temp, precip, wind) in enumerate(weather_conditions):
        assert saved_forecasts[i].temperature == temp
        assert saved_forecasts[i].precipitation == precip
        assert saved_forecasts[i].wind_speed == wind 