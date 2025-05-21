import os
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command

# Load development environment variables
load_dotenv('.env.development')

def run_migrations():
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Set the database URL in the configuration
    alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
    
    # Run the migration
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    run_migrations() 