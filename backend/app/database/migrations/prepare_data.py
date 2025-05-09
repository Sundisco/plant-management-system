from sqlalchemy import create_engine, text
from app.core.config import settings

def prepare_data():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        # First, ensure we have the default user
        conn.execute(text("""
            INSERT INTO users (id, email, hashed_password)
            VALUES (1, 'default@example.com', 'temporary_hashed_password')
            ON CONFLICT (id) DO NOTHING;
        """))

        # Clear existing data to avoid conflicts
        conn.execute(text("DELETE FROM watering_schedules;"))
        conn.execute(text("DELETE FROM user_plants;"))
        conn.execute(text("DELETE FROM plants;"))
        
        conn.commit()
        print("Data preparation completed successfully!")

if __name__ == "__main__":
    prepare_data() 