import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db
from app.schemas.plants import Plant
from app.schemas.plant_guides import PlantGuide, PlantGuideCreate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use the same database setup as in test_plants.py
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
def guide_data(test_plant):
    return {
        "plant_id": test_plant["id"],
        "type": "sunlight",
        "description": "Place in bright, indirect sunlight"
    }

@pytest.fixture
def created_guide(guide_data):
    response = client.post("/plant-guides/", json=guide_data)
    return response.json()

def test_create_guide(created_guide, guide_data):
    assert created_guide["type"] == guide_data["type"]
    assert created_guide["description"] == guide_data["description"]
    assert created_guide["plant_id"] == guide_data["plant_id"]

def test_create_guide_invalid_type():
    invalid_data = {
        "plant_id": 1,
        "type": "invalid_type",
        "description": "Test description"
    }
    response = client.post("/plant-guides/", json=invalid_data)
    assert response.status_code == 422

def test_get_guides_for_plant(test_plant, created_guide):
    response = client.get(f"/plants/{test_plant['id']}/guides")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["type"] == created_guide["type"]

def test_get_guide(created_guide):
    response = client.get(f"/plant-guides/{created_guide['id']}")
    assert response.status_code == 200
    assert response.json() == created_guide

def test_delete_guide(created_guide):
    response = client.delete(f"/plant-guides/{created_guide['id']}")
    assert response.status_code == 200
    
    # Verify guide is deleted
    get_response = client.get(f"/plant-guides/{created_guide['id']}")
    assert get_response.status_code == 404

def test_cascade_delete(test_plant, created_guide):
    # Delete plant should delete associated guides
    response = client.delete(f"/plants/{test_plant['id']}")
    assert response.status_code == 200
    
    # Verify guide is deleted
    get_response = client.get(f"/plant-guides/{created_guide['id']}")
    assert get_response.status_code == 404 