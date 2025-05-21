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
from fastapi.testclient import TestClient
import json
from app.main import app
from app.core.security import get_password_hash

def create_test_user(db: Session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_test_plant(db: Session):
    """Create a test plant"""
    plant = Plant(
        name="Test Plant",
        species="Test Species",
        water_frequency_days=7,
        water_amount_ml=100,
        sunlight_hours=6,
        temperature_min=15,
        temperature_max=25,
        humidity_min=40,
        humidity_max=60
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant

def create_test_user_plant(db: Session, user_id: int, plant_id: int):
    """Create a test user plant"""
    user_plant = UserPlant(
        user_id=user_id,
        plant_id=plant_id,
        nickname="Test Plant",
        location="Test Location",
        last_watered=datetime.utcnow() - timedelta(days=3)
    )
    db.add(user_plant)
    db.commit()
    db.refresh(user_plant)
    return user_plant

def create_test_watering_schedule(db: Session, user_plant_id: int):
    """Create a test watering schedule"""
    schedule = WateringSchedule(
        user_plant_id=user_plant_id,
        next_watering=datetime.utcnow() + timedelta(days=4),
        water_amount_ml=100,
        is_adjusted=False
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule

def create_test_weather_forecast(db: Session):
    """Create a test weather forecast"""
    forecast = WeatherForecast(
        date=datetime.utcnow() + timedelta(days=1),
        temperature=20,
        humidity=50,
        precipitation_mm=0,
        wind_speed_mps=5,
        cloud_coverage_percent=30
    )
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    return forecast

def test_weather_adjustment_flow(client: TestClient, db: Session):
    """Test the complete flow of weather-based watering schedule adjustments"""
    # Create test data
    user = create_test_user(db)
    plant = create_test_plant(db)
    user_plant = create_test_user_plant(db, user.id, plant.id)
    schedule = create_test_watering_schedule(db, user_plant.id)
    forecast = create_test_weather_forecast(db)
    
    # Test the weather adjustment endpoint
    response = client.post(
        f"/api/weather/adjust-schedules",
        json={"date": forecast.date.isoformat()}
    )
    assert response.status_code == 200
    
    # Verify the schedule was adjusted
    updated_schedule = db.query(WateringSchedule).filter(
        WateringSchedule.user_plant_id == user_plant.id
    ).first()
    assert updated_schedule.is_adjusted == True
    assert updated_schedule.next_watering != schedule.next_watering

def test_multiple_weather_conditions(client: TestClient, db: Session):
    """Test watering schedule adjustments with different weather conditions"""
    # Create test data
    user = create_test_user(db)
    plant = create_test_plant(db)
    user_plant = create_test_user_plant(db, user.id, plant.id)
    schedule = create_test_watering_schedule(db, user_plant.id)
    
    # Test with high temperature
    hot_forecast = WeatherForecast(
        date=datetime.utcnow() + timedelta(days=1),
        temperature=30,  # High temperature
        humidity=40,
        precipitation_mm=0,
        wind_speed_mps=5,
        cloud_coverage_percent=10
    )
    db.add(hot_forecast)
    db.commit()
    
    response = client.post(
        f"/api/weather/adjust-schedules",
        json={"date": hot_forecast.date.isoformat()}
    )
    assert response.status_code == 200
    
    # Test with high precipitation
    rainy_forecast = WeatherForecast(
        date=datetime.utcnow() + timedelta(days=2),
        temperature=20,
        humidity=80,
        precipitation_mm=20,  # High precipitation
        wind_speed_mps=5,
        cloud_coverage_percent=90
    )
    db.add(rainy_forecast)
    db.commit()
    
    response = client.post(
        f"/api/weather/adjust-schedules",
        json={"date": rainy_forecast.date.isoformat()}
    )
    assert response.status_code == 200
    
    # Verify the schedule was adjusted differently for each condition
    updated_schedule = db.query(WateringSchedule).filter(
        WateringSchedule.user_plant_id == user_plant.id
    ).first()
    assert updated_schedule.is_adjusted == True

def test_extreme_weather_conditions(client: TestClient, db: Session):
    """Test how the system handles extreme weather conditions"""
    today = date.today()
    user_id = 1
    plant_id = 1
    
    # Create user
    user = User(
        id=user_id,
        email="test@example.com",
        hashed_password="testpassword",
        is_active=True
    )
    db.add(user)
    db.flush()
    
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
    
    # Create extreme weather conditions
    extreme_conditions = [
        (40.0, 0.0, 30.0),  # Extreme heat and high winds
        (5.0, 50.0, 5.0),   # Heavy rain and cold
        (35.0, 0.0, 0.0),   # Just extreme heat
        (15.0, 0.0, 40.0),  # Just extreme winds
    ]
    
    for i, (temp, precip, wind) in enumerate(extreme_conditions):
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
    
    # Verify adjustments for extreme conditions
    for i, (temp, precip, wind) in enumerate(extreme_conditions):
        day = today + timedelta(days=i+1)
        day_str = day.isoformat()
        
        for schedule_day in data["schedule"]:
            if schedule_day["date"] == day_str:
                for section in schedule_day["sections"]:
                    if section["name"] == "A":
                        for plant in section["plants"]:
                            if plant["plant_id"] == plant_id:
                                # All extreme conditions should trigger adjustments
                                assert plant["weather_adjusted"] == True
                                # Verify the adjustment direction
                                if temp > 35 or wind > 20:
                                    assert plant["water_needed"] == True
                                elif precip > 20:
                                    assert plant["water_needed"] == False

def test_consecutive_rainy_days(client: TestClient, db: Session):
    """Test how the system handles consecutive rainy days"""
    today = date.today()
    user_id = 1
    plant_id = 1
    
    # Create user
    user = User(
        id=user_id,
        email="test@example.com",
        hashed_password="testpassword",
        is_active=True
    )
    db.add(user)
    db.flush()
    
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
    
    user_plant = UserPlant(
        user_id=user_id,
        plant_id=plant_id,
        section="A"
    )
    db.add(user_plant)
    
    # Create initial schedule
    schedule = WateringSchedule(
        user_id=user_id,
        plant_id=plant_id,
        scheduled_date=today + timedelta(days=1),
        water_needed=True,
        completed=False
    )
    db.add(schedule)
    
    # Create 5 consecutive rainy days
    for i in range(5):
        forecast = WeatherForecast(
            timestamp=datetime.now() + timedelta(days=i),
            temperature=20.0,
            precipitation=25.0,  # Heavy rain
            wind_speed=5.0
        )
        db.add(forecast)
    
    db.commit()
    
    # Test API endpoint
    response = client.get(f"/api/watering-schedule/watering-schedule/user/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "schedule" in data
    
    # Verify that the schedule is adjusted for the rainy period
    found_adjusted = False
    for day in data["schedule"]:
        for section in day["sections"]:
            if section["name"] == "A":
                for plant in section["plants"]:
                    if plant["plant_id"] == plant_id:
                        if plant["weather_adjusted"]:
                            found_adjusted = True
                            # Verify the schedule is pushed forward
                            assert plant["water_needed"] == False
    
    assert found_adjusted, "No weather adjustments found for consecutive rainy days"

def test_multiple_plants_different_needs(client: TestClient, db: Session):
    """Test how the system handles multiple plants with different watering needs"""
    today = date.today()
    user_id = 1
    
    # Create user
    user = User(
        id=user_id,
        email="test@example.com",
        hashed_password="testpassword",
        is_active=True
    )
    db.add(user)
    db.flush()
    
    # Create two plants with different watering needs
    plants = [
        Plant(id=1, common_name="Drought Tolerant", scientific_name=["Drought Plant"]),
        Plant(id=2, common_name="Water Loving", scientific_name=["Water Plant"])
    ]
    for plant in plants:
        db.add(plant)
    
    watering_infos = [
        Watering(plant_id=1, frequency_days=14, depth_mm=5, volume_feet=0.5),  # Drought tolerant
        Watering(plant_id=2, frequency_days=3, depth_mm=20, volume_feet=2.0)   # Water loving
    ]
    for info in watering_infos:
        db.add(info)
    
    # Create user plants
    user_plants = [
        UserPlant(user_id=user_id, plant_id=1, section="A"),
        UserPlant(user_id=user_id, plant_id=2, section="A")
    ]
    for user_plant in user_plants:
        db.add(user_plant)
    
    # Create schedules for both plants
    schedules = []
    for plant_id in [1, 2]:
        schedule = WateringSchedule(
            user_id=user_id,
            plant_id=plant_id,
            scheduled_date=today + timedelta(days=1),
            water_needed=True,
            completed=False
        )
        schedules.append(schedule)
        db.add(schedule)
    
    # Create weather forecast with moderate conditions
    forecast = WeatherForecast(
        timestamp=datetime.now(),
        temperature=25.0,
        precipitation=10.0,
        wind_speed=10.0
    )
    db.add(forecast)
    db.commit()
    
    # Test API endpoint
    response = client.get(f"/api/watering-schedule/watering-schedule/user/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "schedule" in data
    
    # Verify different adjustments for different plants
    found_plants = {1: False, 2: False}
    for day in data["schedule"]:
        for section in day["sections"]:
            if section["name"] == "A":
                for plant in section["plants"]:
                    plant_id = plant["plant_id"]
                    if plant_id in [1, 2]:
                        found_plants[plant_id] = True
                        # Water loving plant should be adjusted more significantly
                        if plant_id == 2:
                            assert plant["weather_adjusted"] == True
                            # Verify the adjustment is appropriate for water-loving plant
                            assert plant["water_needed"] == True
                        # Drought tolerant plant might not need adjustment
                        else:
                            assert plant["weather_adjusted"] == False
    
    assert all(found_plants.values()), "Not all plants were found in the schedule" 