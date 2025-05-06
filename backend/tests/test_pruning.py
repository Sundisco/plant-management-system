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
def pruning_data(test_plant):
    return {
        "plant_id": test_plant["id"],
        "frequency": 2,
        "months": ["March", "September"],
        "interval": "Biannual"
    }

@pytest.fixture
def created_pruning(pruning_data):
    response = client.post("/pruning/", json=pruning_data)
    return response.json()

def test_create_pruning(created_pruning, pruning_data):
    assert created_pruning["plant_id"] == pruning_data["plant_id"]
    assert created_pruning["frequency"] == pruning_data["frequency"]
    assert created_pruning["months"] == pruning_data["months"]
    assert created_pruning["interval"] == pruning_data["interval"]

def test_create_pruning_invalid_frequency():
    invalid_data = {
        "plant_id": 1,
        "frequency": 0,  # Invalid frequency
        "months": ["January"],
        "interval": "Annual"
    }
    response = client.post("/pruning/", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_create_duplicate_pruning(created_pruning, pruning_data):
    # Try to create another pruning for the same plant
    response = client.post("/pruning/", json=pruning_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Pruning information already exists for this plant"

def test_get_pruning(created_pruning):
    response = client.get(f"/pruning/{created_pruning['id']}")
    assert response.status_code == 200
    assert response.json() == created_pruning

def test_get_plant_pruning(test_plant, created_pruning):
    response = client.get(f"/pruning/plant/{test_plant['id']}")
    assert response.status_code == 200
    assert response.json() == created_pruning

def test_get_nonexistent_pruning():
    response = client.get("/pruning/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pruning not found"

def test_update_pruning(created_pruning):
    update_data = {
        "plant_id": created_pruning["plant_id"],
        "frequency": 4,  # Changed
        "months": ["March", "June", "September", "December"],  # Changed
        "interval": "Quarterly"  # Changed
    }
    response = client.put(f"/pruning/{created_pruning['id']}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["frequency"] == 4
    assert updated["months"] == ["March", "June", "September", "December"]
    assert updated["interval"] == "Quarterly"

def test_delete_pruning(created_pruning):
    response = client.delete(f"/pruning/{created_pruning['id']}")
    assert response.status_code == 200
    
    # Verify pruning is deleted
    get_response = client.get(f"/pruning/{created_pruning['id']}")
    assert get_response.status_code == 404

def test_cascade_delete(test_plant, created_pruning):
    # Delete plant should delete associated pruning
    response = client.delete(f"/plants/{test_plant['id']}")
    assert response.status_code == 200
    
    # Verify pruning is deleted
    get_response = client.get(f"/pruning/{created_pruning['id']}")
    assert get_response.status_code == 404

def test_invalid_values():
    invalid_data = {
        "plant_id": 1,
        "frequency": -1,  # Invalid negative value
        "months": [],  # Empty months list
        "interval": ""  # Empty interval
    }
    response = client.post("/pruning/", json=invalid_data)
    assert response.status_code == 422  # Validation error 