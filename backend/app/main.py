from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.watering_schedule import WateringSchedule
from datetime import date
from app.routes import plants, plant_guides, watering, pruning, sunlight, attracts, users, watering_schedule, weather_forecast
# Temporarily comment out plant_guides import
# from app.routes import plant_guides
from app.core.scheduler import update_weather_periodic
from fastapi.middleware.cors import CORSMiddleware
from app.routes import watering_schedule
import os

app = FastAPI()

# Get frontend URL from environment variable, default to localhost for development
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Frontend URL from environment variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Start scheduler on app startup
@app.on_event("startup")
async def startup_event():
    await update_weather_periodic()

#uvicorn app.main:app --reload
