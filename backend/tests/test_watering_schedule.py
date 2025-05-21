import pytest
from fastapi.testclient import TestClient
import sys
import os
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.models.watering_schedule import WateringSchedule
from app.models.weather_forecast import WeatherForecast
from app.services.watering_schedule import (
    get_watering_schedule,
    calculate_weather_impact,
    adjust_watering_date,
    update_schedule_for_weather
)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use the same database setup as in other tests
SQLALCHEMY_DATABASE_URL = "postgresql://sune:Byy44tvfjan1994@127.0.0.1/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/users/", json=user_data)
    return response.json()

@pytest.fixture
def test_plant():
    plant_data = {
        "common_name": "Test Plant",
        "scientific_name": ["Test Scientific"]
    }
    response = client.post("/plants/", json=plant_data)
    return response.json()

@pytest.fixture
def schedule_data(test_user, test_plant):
    return {
        "user_id": test_user["id"],
        "plant_id": test_plant["id"],
        "scheduled_date": str(date.today()),
        "water_needed": True,
        "volume_needed": 0.5,
        "completed": False
    }

@pytest.fixture
def created_schedule(schedule_data):
    response = client.post("/watering-schedule/", json=schedule_data)
    return response.json()

def test_create_schedule(created_schedule, schedule_data):
    assert created_schedule["user_id"] == schedule_data["user_id"]
    assert created_schedule["plant_id"] == schedule_data["plant_id"]
    assert created_schedule["scheduled_date"] == schedule_data["scheduled_date"]
    assert created_schedule["water_needed"] == schedule_data["water_needed"]
    assert created_schedule["volume_needed"] == schedule_data["volume_needed"]
    assert created_schedule["completed"] == schedule_data["completed"]

def test_create_duplicate_schedule(schedule_data):
    # Create first schedule
    response1 = client.post("/watering-schedule/", json=schedule_data)
    assert response1.status_code == 200

    # Try to create duplicate schedule
    response2 = client.post("/watering-schedule/", json=schedule_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

def test_get_user_schedules(test_user, created_schedule):
    response = client.get(f"/watering-schedule/user/{test_user['id']}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == created_schedule["id"]

def test_get_user_schedules_with_date_range(test_user, test_plant):
    # Create schedules for different dates
    dates = [
        date.today(),
        date.today() + timedelta(days=1),
        date.today() + timedelta(days=5)
    ]
    
    for scheduled_date in dates:
        schedule_data = {
            "user_id": test_user["id"],
            "plant_id": test_plant["id"],
            "scheduled_date": str(scheduled_date),
            "water_needed": True,
            "volume_needed": 0.5
        }
        client.post("/watering-schedule/", json=schedule_data)

    # Test date range query
    date_from = str(date.today())
    date_to = str(date.today() + timedelta(days=2))
    response = client.get(
        f"/watering-schedule/user/{test_user['id']}",
        params={"date_from": date_from, "date_to": date_to}
    )
    
    assert response.status_code == 200
    assert len(response.json()) == 2  # Should only get first two schedules

def test_get_upcoming_schedules(test_user, test_plant):
    # Create past, current, and future schedules
    dates = [
        date.today() - timedelta(days=1),  # Past
        date.today(),                      # Today
        date.today() + timedelta(days=3),  # Future
        date.today() + timedelta(days=10)  # Far future
    ]
    
    for scheduled_date in dates:
        schedule_data = {
            "user_id": test_user["id"],
            "plant_id": test_plant["id"],
            "scheduled_date": str(scheduled_date),
            "water_needed": True
        }
        client.post("/watering-schedule/", json=schedule_data)

    # Get upcoming schedules for next 7 days
    response = client.get(f"/watering-schedule/user/{test_user['id']}/upcoming")
    assert response.status_code == 200
    schedules = response.json()
    assert len(schedules) == 2  # Should only get today and +3 days schedules

def test_update_schedule(created_schedule):
    update_data = {
        "completed": True,
        "next_scheduled_date": str(date.today() + timedelta(days=7))
    }
    
    response = client.put(f"/watering-schedule/{created_schedule['id']}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["completed"] == True
    assert updated["next_scheduled_date"] == str(date.today() + timedelta(days=7))
    assert updated["completion_timestamp"] is not None

def test_delete_schedule(created_schedule):
    response = client.delete(f"/watering-schedule/{created_schedule['id']}")
    assert response.status_code == 200
    
    # Verify schedule is deleted
    get_response = client.get(f"/watering-schedule/user/{created_schedule['user_id']}")
    assert len(get_response.json()) == 0

def test_get_user_plant_schedules(test_user, test_plant, created_schedule):
    response = client.get(
        f"/watering-schedule/user/{test_user['id']}/plant/{test_plant['id']}"
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == created_schedule["id"]

def test_invalid_date_range():
    # Test with end date before start date
    response = client.get(
        "/watering-schedule/user/1",
        params={
            "date_from": str(date.today()),
            "date_to": str(date.today() - timedelta(days=1))
        }
    )
    assert response.status_code == 200
    assert len(response.json()) == 0  # Should return empty list for invalid range 

def test_weather_impact_calculation():
    """Test weather impact calculation for different conditions"""
    # Test high temperature
    impact, days = calculate_weather_impact(30.0, 0.0)
    assert impact > 0
    assert days > 0

    # Test heavy rain
    impact, days = calculate_weather_impact(20.0, 15.0)
    assert impact < 0
    assert days < 0

    # Test normal conditions
    impact, days = calculate_weather_impact(22.0, 2.0)
    assert abs(impact) < 0.4
    assert days == 0

def test_adjust_watering_date():
    """Test watering date adjustments"""
    today = date.today()
    future_date = today + timedelta(days=5)
    
    # Test forward adjustment
    adjusted = adjust_watering_date(future_date, 2)
    assert adjusted == future_date + timedelta(days=2)
    
    # Test backward adjustment
    adjusted = adjust_watering_date(future_date, -2)
    assert adjusted == future_date - timedelta(days=2)
    
    # Test adjustment before today
    adjusted = adjust_watering_date(today, -1)
    assert adjusted == today  # Should not go before today

def test_weather_schedule_adjustment(db: Session):
    """Test full weather-based schedule adjustment"""
    # Create test data
    today = date.today()
    user_id = 1
    plant_id = 1
    
    # Create a schedule for tomorrow
    schedule = WateringSchedule(
        user_id=user_id,
        plant_id=plant_id,
        scheduled_date=today + timedelta(days=1),
        water_needed=True,
        completed=False
    )
    db.add(schedule)
    db.commit()
    
    # Create weather forecast with high temperature
    forecast = WeatherForecast(
        timestamp=datetime.now(),
        temperature=30.0,
        precipitation=0.0,
        wind_speed=5.0
    )
    db.add(forecast)
    db.commit()
    
    # Get watering schedule
    result = get_watering_schedule(db, user_id)
    
    # Verify schedule was adjusted
    assert result["schedule"]
    for day in result["schedule"]:
        if day["date"] == (today + timedelta(days=1)).isoformat():
            for section in day["sections"]:
                for plant in section["plants"]:
                    if plant["plant_id"] == plant_id:
                        assert plant["weather_adjusted"] == True
                        break 