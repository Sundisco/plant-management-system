from sqlalchemy import create_engine, text
from app.core.config import settings

def add_completion_timestamp():
    """Add completion_timestamp column to watering_schedule table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Add completion_timestamp column if it doesn't exist
        conn.execute(text("""
            ALTER TABLE watering_schedule 
            ADD COLUMN IF NOT EXISTS completion_timestamp TIMESTAMP;
        """))
        
        conn.commit()
        print("Added completion_timestamp column to watering_schedule table")

if __name__ == "__main__":
    add_completion_timestamp() 