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
        # Get the directory containing this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create Alembic configuration
        alembic_cfg = Config(os.path.join(current_dir, "alembic.ini"))
        
        # Set the script location
        alembic_cfg.set_main_option("script_location", os.path.join(current_dir, "alembic"))
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
            
        # Ensure the URL uses postgresql:// instead of postgres://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        # Set the database URL
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run the migration
        logger.info("Running database migrations...")
        logger.info(f"Using database URL: {database_url}")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations() 