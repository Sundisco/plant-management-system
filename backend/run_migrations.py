import os
import sys
from alembic.config import Config
from alembic import command
import logging
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    try:
        # Print all environment variables (excluding sensitive data)
        logger.info("Environment variables:")
        for key, value in os.environ.items():
            if 'SECRET' not in key and 'KEY' not in key and 'PASS' not in key:
                logger.info(f"{key}: {value}")

        # Get the directory containing this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Current directory: {current_dir}")
        
        # Create Alembic configuration
        alembic_cfg = Config(os.path.join(current_dir, "alembic.ini"))
        
        # Set the script location
        alembic_cfg.set_main_option("script_location", os.path.join(current_dir, "alembic"))
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        logger.info("Raw DATABASE_URL from environment: %s", database_url)
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
            
        # Ensure the URL uses postgresql:// instead of postgres://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            logger.info("Converted postgres:// to postgresql://")
        
        # Remove any localhost references
        if "localhost" in database_url:
            logger.warning("Found localhost in database URL, this might cause issues")
            # Try to get the actual database URL from Render's environment
            render_db_url = os.getenv("RENDER_DATABASE_URL")
            if render_db_url:
                logger.info("Found RENDER_DATABASE_URL, using that instead")
                database_url = render_db_url
        
        # Set the database URL
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run the migration
        logger.info("Running database migrations...")
        logger.info("Using database URL: %s", database_url)
        
        # Test database connection before running migrations
        try:
            from sqlalchemy import create_engine
            engine = create_engine(database_url)
            with engine.connect() as conn:
                logger.info("Successfully connected to database")
        except Exception as e:
            logger.error("Failed to connect to database: %s", str(e))
            raise
        
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully")
        
    except Exception as e:
        logger.error("Error running migrations: %s", str(e))
        sys.exit(1)

if __name__ == "__main__":
    run_migrations() 