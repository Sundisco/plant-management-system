from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, configure_mappers
from app.core.config import settings
from sqlalchemy import event
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Create engine with connection testing
    engine = create_engine(
        settings.get_database_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_pre_ping=True  # Enable connection testing
    )
    
    # Test the connection
    with engine.connect() as conn:
        logger.info("Successfully connected to the database")
except Exception as e:
    logger.error(f"Failed to connect to the database: {str(e)}")
    raise

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Import all models to ensure they are registered with Base
from app.models.users import User
from app.models.plants import Plant
from app.models.user_plants import UserPlant
from app.models.watering_schedule import WateringSchedule
from app.models.watering import Watering
from app.models.pruning import Pruning
from app.models.sunlight import Sunlight
from app.models.attracts import Attracts
from app.models.plant_guides import PlantGuide

# Configure all mappers
configure_mappers()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()
