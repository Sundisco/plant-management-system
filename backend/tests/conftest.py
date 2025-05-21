import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient, Client, Response
from app.database import Base, get_db
from app.main import app
from app.core.config import settings
import asyncio
from fastapi import FastAPI

# Set up test environment variables
os.environ["LOCAL_DB_PASSWORD"] = "Byy44tvfjan1994"  # Use your actual password
os.environ["ENVIRONMENT"] = "test"

def ensure_test_db():
    """Ensure test database exists"""
    # Connect to default postgres database
    default_engine = create_engine("postgresql://sune:Byy44tvfjan1994@localhost:5432/postgres")
    with default_engine.connect() as conn:
        # Check if test_db exists
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='test_db'"))
        if not result.scalar():
            # Create test_db if it doesn't exist
            conn.execute(text("COMMIT"))  # Close any open transaction
            conn.execute(text("CREATE DATABASE test_db"))
    default_engine.dispose()

# Ensure test database exists
ensure_test_db()

# Test database engine
engine = create_engine(settings.TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

class CustomTestClient:
    def __init__(self, app):
        self.client = TestClient(app)
    
    def get(self, url, **kwargs):
        return self.client.get(url, **kwargs)
    
    def post(self, url, **kwargs):
        return self.client.post(url, **kwargs)
    
    def put(self, url, **kwargs):
        return self.client.put(url, **kwargs)
    
    def delete(self, url, **kwargs):
        return self.client.delete(url, **kwargs)

@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a fresh database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield CustomTestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client():
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
async def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 