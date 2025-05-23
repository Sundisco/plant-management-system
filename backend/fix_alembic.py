import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is not set")
    sys.exit(1)

def fix_alembic_version():
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Connect to database
        with engine.connect() as conn:
            # Start transaction
            with conn.begin():
                # First, let's see what's in the alembic_version table
                result = conn.execute(text("SELECT * FROM alembic_version"))
                print("Current alembic_version table contents:")
                for row in result:
                    print(row)
                
                # Clean up any stale references
                conn.execute(text("""
                    DELETE FROM alembic_version 
                    WHERE version_num IN ('merge_heads', 'add_timestamps_to_user_plants')
                """))
                
                # Ensure we have the correct version
                conn.execute(text("""
                    INSERT INTO alembic_version (version_num)
                    VALUES ('fix_all_migrations')
                    ON CONFLICT (version_num) DO NOTHING
                """))
                
                # Verify the changes
                result = conn.execute(text("SELECT * FROM alembic_version"))
                print("\nUpdated alembic_version table contents:")
                for row in result:
                    print(row)
                
                print("\nSuccessfully fixed alembic_version table")
    except Exception as e:
        print(f"Error fixing alembic_version table: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    fix_alembic_version() 