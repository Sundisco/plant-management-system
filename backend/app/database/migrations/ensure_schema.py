from sqlalchemy import create_engine, text
from app.core.config import settings

def ensure_schema():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        # Create plants table if it doesn't exist
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS plants (
                id SERIAL PRIMARY KEY,
                common_name TEXT,
                scientific_name TEXT[],
                other_names TEXT[],
                family TEXT,
                type TEXT,
                description TEXT,
                growth_rate TEXT,
                maintenance TEXT,
                hardiness_zone TEXT,
                image_url TEXT,
                cycle TEXT,
                watering TEXT,
                is_evergreen BOOLEAN DEFAULT FALSE,
                edible_fruit BOOLEAN DEFAULT FALSE
            );
        """))

        # Create users table if it doesn't exist
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR UNIQUE,
                hashed_password VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # Create user_plants junction table if it doesn't exist
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_plants (
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                plant_id INTEGER REFERENCES plants(id) ON DELETE CASCADE,
                section VARCHAR,
                PRIMARY KEY (user_id, plant_id)
            );
        """))

        # Create watering_schedules table if it doesn't exist
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS watering_schedules (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                plant_id INTEGER REFERENCES plants(id) ON DELETE CASCADE,
                scheduled_date DATE,
                next_scheduled_date DATE,
                completed BOOLEAN DEFAULT FALSE
            );
        """))

        conn.commit()
        print("Schema ensured successfully!")

if __name__ == "__main__":
    ensure_schema() 