from fastapi import FastAPI, Depends, BackgroundTasks, Request
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
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

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
    "https://1cff-89-150-165-188.ngrok-free.app",  # Current ngrok URL
    "http://localhost:3000",  # Local serve
    "http://localhost:10000",  # Render serve
]

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Accept",
        "Authorization",
        "X-Requested-With",
        "ngrok-skip-browser-warning",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Credentials",
    ],
    expose_headers=["*"],
    max_age=3600,
)

# Add error handling middleware
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
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
