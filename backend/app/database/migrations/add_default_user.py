from sqlalchemy import create_engine, text
from app.core.config import settings

def add_default_user():
    """Add a default user if it doesn't exist"""
    engine = create_engine(settings.get_database_url)
    with engine.connect() as conn:
        # Add default user if it doesn't exist
        conn.execute(text("""
            INSERT INTO users (id, email, hashed_password)
            VALUES (1, 'default@example.com', 'temporary_hashed_password')
            ON CONFLICT (id) DO NOTHING;
        """))
        conn.commit()

if __name__ == "__main__":
    add_default_user() 