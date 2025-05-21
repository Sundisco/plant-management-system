import pytest
from fastapi import FastAPI
from httpx import Client
import sys
import logging
import httpx
from fastapi.testclient import TestClient

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a minimal FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

def test_minimal_client(caplog):
    """Test with a minimal client setup"""
    caplog.set_level(logging.INFO)
    
    # Print versions
    import fastapi
    import starlette
    print("\nVersions:")
    print(f"FastAPI: {fastapi.__version__}")
    print(f"Starlette: {starlette.__version__}")
    print(f"httpx: {httpx.__version__}")
    
    # Method 1: FastAPI TestClient
    try:
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}
        logger.info(f"Method 1 (FastAPI TestClient) - Status: {response.status_code}")
        logger.info(f"Response: {response.json()}")
    except Exception as e:
        pytest.fail(f"Method 1 (FastAPI TestClient) failed: {str(e)}")
    
    # Method 2: Custom TestClient
    try:
        from conftest import CustomTestClient
        client = CustomTestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}
        logger.info(f"Method 2 (CustomTestClient) - Status: {response.status_code}")
        logger.info(f"Response: {response.json()}")
    except Exception as e:
        pytest.fail(f"Method 2 (CustomTestClient) failed: {str(e)}")
    
    # Print TestClient source
    print("\nTestClient source:")
    import inspect
    print(inspect.getsource(TestClient)) 