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
        "common_name": "Butterfly Bush",
        "scientific_name": ["Buddleja davidii"]
    }
    response = client.post("/plants/", json=plant_data)
    return response.json()

@pytest.fixture
def attracts_data(test_plant):
    return {
        "plant_id": test_plant["id"],
        "species": "Monarch Butterfly"
    }

@pytest.fixture
def created_attracts(attracts_data):
    response = client.post("/attracts/", json=attracts_data)
    return response.json()

def test_create_attracts(created_attracts, attracts_data):
    assert created_attracts["plant_id"] == attracts_data["plant_id"]
    assert created_attracts["species"] == attracts_data["species"]

def test_create_multiple_attracts(test_plant):
    species_list = ["Monarch Butterfly", "Swallowtail Butterfly", "Honeybee"]
    created_entries = []
    
    for species in species_list:
        data = {
            "plant_id": test_plant["id"],
            "species": species
        }
        response = client.post("/attracts/", json=data)
        assert response.status_code == 200
        created_entries.append(response.json())
    
    # Verify all entries were created
    response = client.get(f"/attracts/plant/{test_plant['id']}")
    assert response.status_code == 200
    assert len(response.json()) == len(species_list)

def test_get_attracts(created_attracts):
    response = client.get(f"/attracts/{created_attracts['id']}")
    assert response.status_code == 200
    assert response.json() == created_attracts

def test_get_plant_attracts(test_plant, created_attracts):
    response = client.get(f"/attracts/plant/{test_plant['id']}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0] == created_attracts

def test_get_plant_attracts_species(test_plant):
    # Create multiple attracts entries
    species = ["Monarch Butterfly", "Swallowtail Butterfly", "Honeybee"]
    for s in species:
        client.post("/attracts/", json={"plant_id": test_plant["id"], "species": s})
    
    response = client.get(f"/attracts/plant/{test_plant['id']}/species")
    assert response.status_code == 200
    result = response.json()
    assert result["plant_id"] == test_plant["id"]
    assert len(result["species_list"]) == len(species)
    assert all(s in result["species_list"] for s in species)

def test_get_nonexistent_attracts():
    response = client.get("/attracts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Attracts entry not found"

def test_delete_single_attracts(created_attracts):
    response = client.delete(f"/attracts/{created_attracts['id']}")
    assert response.status_code == 200
    
    # Verify attracts is deleted
    get_response = client.get(f"/attracts/{created_attracts['id']}")
    assert get_response.status_code == 404

def test_delete_all_plant_attracts(test_plant):
    # Create multiple attracts entries
    species = ["Monarch Butterfly", "Swallowtail Butterfly", "Honeybee"]
    for s in species:
        client.post("/attracts/", json={"plant_id": test_plant["id"], "species": s})
    
    # Delete all attracts for the plant
    response = client.delete(f"/attracts/plant/{test_plant['id']}")
    assert response.status_code == 200
    
    # Verify all attracts are deleted
    get_response = client.get(f"/attracts/plant/{test_plant['id']}")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0

def test_cascade_delete(test_plant, created_attracts):
    # Delete plant should delete associated attracts
    response = client.delete(f"/plants/{test_plant['id']}")
    assert response.status_code == 200
    
    # Verify attracts is deleted
    get_response = client.get(f"/attracts/{created_attracts['id']}")
    assert get_response.status_code == 404

def test_create_attracts_invalid_plant():
    invalid_data = {
        "plant_id": 999,  # Non-existent plant ID
        "species": "Monarch Butterfly"
    }
    response = client.post("/attracts/", json=invalid_data)
    assert response.status_code == 404  # Changed from 400 to 404
    assert response.json()["detail"] == "Plant not found"

def test_empty_species():
    # First create a valid plant
    plant_data = {
        "common_name": "Test Plant",
        "scientific_name": ["Test Scientific"]
    }
    plant_response = client.post("/plants/", json=plant_data)
    plant_id = plant_response.json()["id"]
    
    invalid_data = {
        "plant_id": plant_id,  # Use valid plant ID
        "species": ""  # Empty species should not be allowed
    }
    response = client.post("/attracts/", json=invalid_data)
    assert response.status_code == 422  # Validation error 