import os
import uvicorn
from dotenv import load_dotenv

# Load development environment variables
load_dotenv('.env.development')

if __name__ == "__main__":
    # Run the FastAPI application with development settings
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload on code changes
        workers=1,    # Single worker for development
        log_level="debug"
    ) 