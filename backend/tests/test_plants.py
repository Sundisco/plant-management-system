# /backend/tests/test_plants.py
import sys
import os
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.database import Base, get_db

# Try one of these alternative connection strings:

# Option 1: Use different host
SQLALCHEMY_DATABASE_URL = "postgresql://sune:Byy44tvfjan1994@127.0.0.1/test_db"

# Option 2: Include port explicitly
#SQLALCHEMY_DATABASE_URL = "postgresql://sune:Byy44tvfjan1994@localhost:5432/test_db"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override
app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)  # Clear existing tables
    Base.metadata.create_all(bind=engine)  # Create fresh tables
    yield
    Base.metadata.drop_all(bind=engine)  # Clean up after tests

@pytest.fixture
def plant_data():
    return {
        "common_name": "Rose",
        "scientific_name": ["Rosa"],
        "other_names": ["Garden Rose"],
        "family": "Rosaceae",
        "type": "shrub",
        "description": "A woody perennial flowering plant",
        "growth_rate": "Moderate",
        "maintenance": "High",
        "hardiness_zone": "5-9",
        "image_url": "https://example.com/rose.jpg",
        "cycle": "Perennial",
        "watering": "Moderate",
        "is_evergreen": False,
        "edible_fruit": False
    }

@pytest.fixture
def created_plant(plant_data):
    response = client.post("/plants/", json=plant_data)
    return response.json()

def test_create_plant_full(created_plant, plant_data):
    for key, value in plant_data.items():
        assert created_plant[key] == value
    assert "id" in created_plant
    assert "created_at" in created_plant
    assert "updated_at" in created_plant

def test_create_plant_minimal():
    minimal_data = {
        "common_name": "Minimal Rose",
        "scientific_name": ["Rosa minima"]
        # All other fields will use their default values
    }
    response = client.post("/plants/", json=minimal_data)
    assert response.status_code == 200
    assert response.json()["common_name"] == "Minimal Rose"

def test_update_plant_full(created_plant, plant_data):
    plant_id = created_plant["id"]
    updated_data = plant_data.copy()
    updated_data["common_name"] = "Updated Rose"
    updated_data["light"] = "Partial Shade"
    
    response = client.put(f"/plants/{plant_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["common_name"] == "Updated Rose"
    assert response.json()["light"] == "Partial Shade"

def test_get_plants(created_plant):
    response = client.get("/plants/")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["common_name"] == "Rose"

def test_get_plant(created_plant):
    plant_id = created_plant["id"]
    response = client.get(f"/plants/{plant_id}")
    assert response.status_code == 200
    assert response.json()["id"] == plant_id

def test_create_plant_invalid_data():
    response = client.post(
        "/plants/",
        json={"common_name": "", "scientific_name": [], "watering": ""}  # Invalid data
    )
    assert response.status_code == 422  # Validation error

def test_get_nonexistent_plant():
    response = client.get("/plants/999")  # Non-existent ID
    assert response.status_code == 404
    assert response.json()["detail"] == "Plant not found"

def test_delete_plant(created_plant):
    plant_id = created_plant["id"]
    response = client.delete(f"/plants/{plant_id}")
    assert response.status_code == 200
    
    # Verify plant is deleted
    get_response = client.get(f"/plants/{plant_id}")
    assert get_response.status_code == 404

def test_create_plant_invalid_type():
    invalid_data = {
        "common_name": "Invalid Plant",
        "scientific_name": ["Test"],
        "type": "invalid_type"  # This should fail validation
    }
    response = client.post("/plants/", json=invalid_data)
    assert response.status_code == 422  # Validation error
