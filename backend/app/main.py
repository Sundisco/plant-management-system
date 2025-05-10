from fastapi import FastAPI, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.watering_schedule import WateringSchedule
from datetime import date
from app.routes import plants, plant_guides, watering, pruning, sunlight, attracts, users, watering_schedule, weather_forecast
# Temporarily comment out plant_guides import
# from app.routes import plant_guides
from app.core.scheduler import update_weather_periodic, start_scheduler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import watering_schedule
import os
import asyncio
import logging
from app.core.config import settings
from app.api.api_v1.api import api_router

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

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

# Global variable to store the scheduler task
scheduler_task = None

@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    global scheduler_task
    try:
        logger.info("Starting application...")
        # Start the scheduler
        scheduler_task = start_scheduler()
        logger.info("Background tasks started successfully")
    except Exception as e:
        logger.error(f"Error starting background tasks: {str(e)}")

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

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up background tasks on shutdown"""
    global scheduler_task
    if scheduler_task:
        try:
            scheduler_task.cancel()
            await scheduler_task
        except asyncio.CancelledError:
            logger.info("Scheduler task cancelled successfully")
        except Exception as e:
            logger.error(f"Error cancelling scheduler task: {str(e)}")

#uvicorn app.main:app --reload
