from fastapi import FastAPI, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.watering_schedule import WateringSchedule
from datetime import date
from app.routes import plants, plant_guides, watering, pruning, sunlight, attracts, users, watering_schedule, weather_forecast
# Temporarily comment out plant_guides import
# from app.routes import plant_guides
from app.core.scheduler import update_weather_periodic
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import watering_schedule
import os
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Define allowed origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Local development
    "https://plant-management-frontend.onrender.com",  # Production frontend
]

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Remove the root level route
# @app.get("/watering-schedule/")
# def get_schedule(db: Session = Depends(get_db)):
#     schedules = db.query(WateringSchedule).filter(WateringSchedule.scheduled_date >= date.today()).all()
#     return schedules

app.include_router(plants.router, prefix="/api/plants", tags=["plants"])
app.include_router(plant_guides.router, prefix="/plant-guides", tags=["plant_guides"])
# Temporarily comment out plant_guides router
# app.include_router(plant_guides.router, prefix="/plant-guides", tags=["plant_guides"])
app.include_router(watering.router, prefix="/watering", tags=["watering"])
app.include_router(pruning.router, prefix="/api/pruning", tags=["pruning"])
app.include_router(sunlight.router, prefix="/sunlight", tags=["sunlight"])
app.include_router(attracts.router, prefix="/attracts", tags=["attracts"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(watering_schedule.router, prefix="/api", tags=["watering_schedule"])
app.include_router(
    weather_forecast.router,
    prefix="/api/weather",
    tags=["weather"]
)

# Add root path handler
@app.get("/")
async def root():
    return {"message": "Plant Management API", "status": "healthy"}

# Start scheduler on app startup
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting application...")
        # Create a background task for weather updates without blocking
        task = asyncio.create_task(update_weather_periodic(BackgroundTasks()))
        # Add error handling for the task
        task.add_done_callback(lambda t: logger.error(f"Weather update task failed: {t.exception()}") if t.exception() else None)
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Don't raise the exception, allow the app to start even if weather updates fail
        pass

@app.on_event("startup")
async def list_routes_on_startup():
    print("=== Registered Routes ===")
    for route in app.routes:
        print(f"{route.path} [{','.join(route.methods)}]")
    print("=========================")

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

#uvicorn app.main:app --reload
