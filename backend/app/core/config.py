from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:Byy44tvfjan1994@localhost:5432/plant_db"
    TEST_DATABASE_URL: str = "postgresql://postgres:Byy44tvfjan1994@localhost:5432/test_db"
    
    # Weather settings
    WEATHER_LAT: float = 56.0
    WEATHER_LON: float = 10.0
    WEATHER_LOCATION: str = "Denmark"
    WEATHER_UPDATE_INTERVAL: int = 6  # hours

    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Plant Watering System"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 