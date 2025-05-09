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

# Add middleware to handle CORS preflight requests
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "https://plant-management-frontend.onrender.com"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

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

# Start scheduler on app startup
@app.on_event("startup")
async def startup_event():
    try:
        # Create a background task for weather updates without blocking
        asyncio.create_task(update_weather_periodic(BackgroundTasks()))
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        # Don't raise the exception, allow the app to start even if weather updates fail
        pass

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Add CORS preflight handler
@app.options("/{full_path:path}")
async def options_handler():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "https://plant-management-frontend.onrender.com",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

#uvicorn app.main:app --reload
