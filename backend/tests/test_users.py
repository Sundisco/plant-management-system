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
def user_data():
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def created_user(user_data):
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

def test_create_user(created_user, user_data):
    assert created_user["email"] == user_data["email"]
    assert "id" in created_user
    assert "created_at" in created_user
    assert "password" not in created_user  # Password should not be in response

def test_create_duplicate_user(user_data):
    # Create first user
    response1 = client.post("/users/", json=user_data)
    assert response1.status_code == 200

    # Try to create duplicate user
    response2 = client.post("/users/", json=user_data)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Email already registered"

def test_get_user(created_user):
    response = client.get(f"/users/{created_user['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == created_user["email"]
    assert "plants" in response.json()

def test_get_nonexistent_user():
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_add_plant_to_user(created_user, test_plant):
    response = client.post(
        f"/users/{created_user['id']}/plants",
        json={"plant_id": test_plant["id"]}
    )
    assert response.status_code == 200

    # Verify plant is in user's garden
    get_response = client.get(f"/users/{created_user['id']}/plants")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 1
    assert get_response.json()[0]["id"] == test_plant["id"]

def test_add_duplicate_plant_to_user(created_user, test_plant):
    # Add plant first time
    response1 = client.post(
        f"/users/{created_user['id']}/plants",
        json={"plant_id": test_plant["id"]}
    )
    assert response1.status_code == 200

    # Try to add same plant again
    response2 = client.post(
        f"/users/{created_user['id']}/plants",
        json={"plant_id": test_plant["id"]}
    )
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Plant already in user's garden"

def test_add_nonexistent_plant_to_user(created_user):
    response = client.post(
        f"/users/{created_user['id']}/plants",
        json={"plant_id": 999}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User or plant not found"

def test_remove_plant_from_user(created_user, test_plant):
    # First add plant to user
    client.post(
        f"/users/{created_user['id']}/plants",
        json={"plant_id": test_plant["id"]}
    )

    # Then remove it
    response = client.delete(f"/users/{created_user['id']}/plants/{test_plant['id']}")
    assert response.status_code == 200

    # Verify plant is removed
    get_response = client.get(f"/users/{created_user['id']}/plants")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0

def test_remove_nonexistent_plant_from_user(created_user):
    response = client.delete(f"/users/{created_user['id']}/plants/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Plant not found in user's garden"

def test_get_user_plants_empty(created_user):
    response = client.get(f"/users/{created_user['id']}/plants")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_get_user_plants_multiple(created_user):
    # Create multiple plants
    plants = []
    for i in range(3):
        plant_data = {
            "common_name": f"Test Plant {i}",
            "scientific_name": [f"Test Scientific {i}"]
        }
        plant_response = client.post("/plants/", json=plant_data)
        plants.append(plant_response.json())

    # Add all plants to user's garden
    for plant in plants:
        client.post(
            f"/users/{created_user['id']}/plants",
            json={"plant_id": plant["id"]}
        )

    # Get user's plants
    response = client.get(f"/users/{created_user['id']}/plants")
    assert response.status_code == 200
    assert len(response.json()) == len(plants) 