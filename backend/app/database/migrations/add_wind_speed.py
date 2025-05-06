from sqlalchemy import create_engine, text
from app.core.config import settings

def upgrade():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        # Add wind_speed column if it doesn't exist
        conn.execute(text("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'weather_forecast' 
                    AND column_name = 'wind_speed'
                ) THEN
                    ALTER TABLE weather_forecast 
                    ADD COLUMN wind_speed FLOAT;
                END IF;
            END $$;
        """))
        conn.commit()

if __name__ == "__main__":
    upgrade() 