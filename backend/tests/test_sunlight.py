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
def sunlight_data(test_plant):
    return {
        "plant_id": test_plant["id"],
        "condition": "full sun"
    }

@pytest.fixture
def created_sunlight(sunlight_data):
    response = client.post("/sunlight/", json=sunlight_data)
    return response.json()

def test_create_sunlight(created_sunlight, sunlight_data):
    assert created_sunlight["plant_id"] == sunlight_data["plant_id"]
    assert created_sunlight["condition"] == sunlight_data["condition"]

def test_create_sunlight_invalid_condition():
    invalid_data = {
        "plant_id": 1,
        "condition": "invalid_condition"  # Invalid condition
    }
    response = client.post("/sunlight/", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_create_duplicate_sunlight(created_sunlight, sunlight_data):
    # Try to create another sunlight for the same plant
    response = client.post("/sunlight/", json=sunlight_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Sunlight information already exists for this plant"

def test_get_sunlight(created_sunlight):
    response = client.get(f"/sunlight/{created_sunlight['id']}")
    assert response.status_code == 200
    assert response.json() == created_sunlight

def test_get_plant_sunlight(test_plant, created_sunlight):
    response = client.get(f"/sunlight/plant/{test_plant['id']}")
    assert response.status_code == 200
    assert response.json() == created_sunlight

def test_get_nonexistent_sunlight():
    response = client.get("/sunlight/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Sunlight not found"

def test_update_sunlight(created_sunlight):
    update_data = {
        "plant_id": created_sunlight["plant_id"],
        "condition": "part shade"  # Changed condition
    }
    response = client.put(f"/sunlight/{created_sunlight['id']}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["condition"] == "part shade"

def test_update_sunlight_invalid_condition(created_sunlight):
    update_data = {
        "plant_id": created_sunlight["plant_id"],
        "condition": "invalid_condition"  # Invalid condition
    }
    response = client.put(f"/sunlight/{created_sunlight['id']}", json=update_data)
    assert response.status_code == 422  # Validation error

def test_delete_sunlight(created_sunlight):
    response = client.delete(f"/sunlight/{created_sunlight['id']}")
    assert response.status_code == 200
    
    # Verify sunlight is deleted
    get_response = client.get(f"/sunlight/{created_sunlight['id']}")
    assert get_response.status_code == 404

def test_cascade_delete(test_plant, created_sunlight):
    # Delete plant should delete associated sunlight
    response = client.delete(f"/plants/{test_plant['id']}")
    assert response.status_code == 200
    
    # Verify sunlight is deleted
    get_response = client.get(f"/sunlight/{created_sunlight['id']}")
    assert get_response.status_code == 404

def test_all_condition_values():
    # Test all valid condition values
    conditions = ["full sun", "part shade", "filtered shade", "shade", "Unknown"]
    plant_response = client.post("/plants/", json={
        "common_name": "Test Plant",
        "scientific_name": ["Test Scientific"]
    })
    plant_id = plant_response.json()["id"]
    
    for condition in conditions:
        # Delete previous sunlight if exists
        sunlights = client.get(f"/sunlight/plant/{plant_id}")
        if sunlights.status_code == 200:
            client.delete(f"/sunlight/{sunlights.json()['id']}")
            
        data = {
            "plant_id": plant_id,
            "condition": condition
        }
        response = client.post("/sunlight/", json=data)
        assert response.status_code == 200
        assert response.json()["condition"] == condition 