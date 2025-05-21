import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
import inspect

# Print TestClient's __init__ signature
print("TestClient __init__ signature:")
print(inspect.signature(TestClient.__init__))

# Try to create a TestClient instance
try:
    client = TestClient(app)
    print("\nSuccessfully created TestClient with app")
except Exception as e:
    print("\nError creating TestClient:")
    print(f"Type: {type(e)}")
    print(f"Message: {str(e)}")

# Print TestClient's source code
print("\nTestClient source code:")
print(inspect.getsource(TestClient)) 