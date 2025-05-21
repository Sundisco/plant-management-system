from fastapi import FastAPI, Depends, BackgroundTasks, Request, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.watering_schedule import WateringSchedule
from datetime import date
from app.routes import plants, plant_guides, watering, pruning, sunlight, attracts, users, watering_schedule, weather_forecast
from app.core.scheduler import update_weather_periodic, start_scheduler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import asyncio
import logging
from app.core.config import settings
from app.routes.sections import router as sections_router
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json"
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
app.include_router(plant_guides.router, prefix="/api/plant_guides", tags=["plant_guides"])
app.include_router(watering.router, prefix="/api/watering", tags=["watering"])
app.include_router(watering_schedule.router, prefix="/api/watering-schedule", tags=["watering-schedule"])
app.include_router(pruning.router, prefix="/api/pruning", tags=["pruning"])
app.include_router(sunlight.router, prefix="/api/sunlight", tags=["sunlight"])
app.include_router(attracts.router, prefix="/api/attracts", tags=["attracts"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(weather_forecast.router, prefix="/api/weather", tags=["weather"])
app.include_router(sections_router, prefix="/api/sections", tags=["sections"])

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
        # Start the scheduler and await the task
        scheduler_task = await start_scheduler()
        if scheduler_task:
            logger.info("Background tasks started successfully")
        else:
            logger.warning("Background tasks failed to start, but application will continue running")
    except Exception as e:
        logger.error(f"Error starting background tasks: {str(e)}")
        logger.warning("Application will continue running without background tasks")

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
            # Cancel the task
            scheduler_task.cancel()
            # Wait for the task to be cancelled
            await scheduler_task
        except asyncio.CancelledError:
            logger.info("Scheduler task cancelled successfully")
        except Exception as e:
            logger.error(f"Error cancelling scheduler task: {str(e)}")

#uvicorn app.main:app --reload

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/api/plants/{plant_id}/attracts")
async def get_plant_attracts(plant_id: int):
    try:
        with SessionLocal() as session:
            result = session.execute(
                text("""
                    SELECT birds, butterflies, bees, hummingbirds, other_animals
                    FROM attracts
                    WHERE plant_id = :plant_id
                """),
                {"plant_id": plant_id}
            )
            attracts_data = result.fetchone()
            
            if attracts_data:
                data = dict(attracts_data._mapping)
                # Convert other_animals from string to list if it's stored as comma-separated values
                if data['other_animals']:
                    data['other_animals'] = [animal.strip() for animal in data['other_animals'].split(',')]
                else:
                    data['other_animals'] = []
                return data
            raise HTTPException(status_code=404, detail="No attracts data found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/plants/{plant_id}/sunlight")
async def get_plant_sunlight(plant_id: int):
    try:
        with SessionLocal() as session:
            result = session.execute(
                text("""
                    SELECT full_sun, partial_shade, full_shade, notes
                    FROM sunlight
                    WHERE plant_id = :plant_id
                """),
                {"plant_id": plant_id}
            )
            sunlight_data = result.fetchone()
            
            if sunlight_data:
                return dict(sunlight_data._mapping)
            raise HTTPException(status_code=404, detail="No sunlight data found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 5000))
    uvicorn.run(app, host='0.0.0.0', port=port)
