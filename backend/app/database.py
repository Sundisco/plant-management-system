from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy import event
from sqlalchemy.orm import mapper
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

# Configure mappers
@event.listens_for(Base.metadata, 'after_create')
def configure_mappers(target, connection, **kw):
    """Configure all mappers after tables are created"""
    mapper.configure_mappers()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()

# Import all models to ensure they are registered with Base
from app.models import *  # This will import all models and register them with Base
