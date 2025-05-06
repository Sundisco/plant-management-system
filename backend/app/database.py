from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Database connection string (update user, password, and db name)
SQLALCHEMY_DATABASE_URL = "postgresql://sune:Byy44tvfjan1994@localhost/plant_db"

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models to ensure they are registered with Base
from app.models import *  # This will import all models and register them with Base
