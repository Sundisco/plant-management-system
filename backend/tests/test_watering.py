import pytest
from fastapi.testclient import TestClient
import sys
import os
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
def test_plant():
    plant_data = {
        "common_name": "Test Plant",
        "scientific_name": ["Test Scientific"]
    }
    response = client.post("/plants/", json=plant_data)
    return response.json()

@pytest.fixture
def watering_data(test_plant):
    return {
        "plant_id": test_plant["id"],
        "frequency_days": 7,
        "depth_mm": 25,
        "volume_feet": 0.5,
        "period": "morning",
        "drought_tolerant": False,
        "soil": ["well-draining", "loamy"]
    }

@pytest.fixture
def created_watering(watering_data):
    response = client.post("/watering/", json=watering_data)
    return response.json()

def test_create_watering(created_watering, watering_data):
    assert created_watering["plant_id"] == watering_data["plant_id"]
    assert created_watering["frequency_days"] == watering_data["frequency_days"]
    assert created_watering["depth_mm"] == watering_data["depth_mm"]
    assert created_watering["volume_feet"] == watering_data["volume_feet"]
    assert created_watering["period"] == watering_data["period"]
    assert created_watering["drought_tolerant"] == watering_data["drought_tolerant"]
    assert created_watering["soil"] == watering_data["soil"]

def test_create_watering_invalid_period():
    invalid_data = {
        "plant_id": 1,
        "frequency_days": 7,
        "depth_mm": 25,
        "volume_feet": 0.5,
        "period": "invalid_period",  # Invalid period
        "drought_tolerant": False,
        "soil": ["well-draining"]
    }
    response = client.post("/watering/", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_create_duplicate_watering(created_watering, watering_data):
    # Try to create another watering for the same plant
    response = client.post("/watering/", json=watering_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Watering information already exists for this plant"

def test_get_watering(created_watering):
    response = client.get(f"/watering/{created_watering['id']}")
    assert response.status_code == 200
    assert response.json() == created_watering

def test_get_plant_watering(test_plant, created_watering):
    response = client.get(f"/watering/plant/{test_plant['id']}")
    assert response.status_code == 200
    assert response.json() == created_watering

def test_get_nonexistent_watering():
    response = client.get("/watering/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Watering not found"

def test_update_watering(created_watering):
    update_data = {
        "plant_id": created_watering["plant_id"],
        "frequency_days": 14,  # Changed
        "depth_mm": 30,  # Changed
        "volume_feet": 0.75,  # Changed
        "period": "evening",  # Changed
        "drought_tolerant": True,  # Changed
        "soil": ["sandy", "well-draining"]  # Changed
    }
    response = client.put(f"/watering/{created_watering['id']}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["frequency_days"] == 14
    assert updated["depth_mm"] == 30
    assert updated["volume_feet"] == 0.75
    assert updated["period"] == "evening"
    assert updated["drought_tolerant"] == True
    assert updated["soil"] == ["sandy", "well-draining"]

def test_delete_watering(created_watering):
    response = client.delete(f"/watering/{created_watering['id']}")
    assert response.status_code == 200
    
    # Verify watering is deleted
    get_response = client.get(f"/watering/{created_watering['id']}")
    assert get_response.status_code == 404

def test_cascade_delete(test_plant, created_watering):
    # Delete plant should delete associated watering
    response = client.delete(f"/plants/{test_plant['id']}")
    assert response.status_code == 200
    
    # Verify watering is deleted
    get_response = client.get(f"/watering/{created_watering['id']}")
    assert get_response.status_code == 404

def test_invalid_values():
    invalid_data = {
        "plant_id": 1,
        "frequency_days": -1,  # Invalid negative value
        "depth_mm": 0,  # Invalid zero value
        "volume_feet": -0.5,  # Invalid negative value
        "period": "morning",
        "drought_tolerant": False,
        "soil": []  # Empty soil list
    }
    response = client.post("/watering/", json=invalid_data)
    assert response.status_code == 422  # Validation error 