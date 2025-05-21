from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: Optional[str] = None
    LOCAL_DB_PASSWORD: Optional[str] = None
    RENDER_DATABASE_URL: Optional[str] = None
    
    @property
    def LOCAL_DATABASE_URL(self) -> str:
        return f"postgresql://sune:{self.LOCAL_DB_PASSWORD}@localhost:5432/plant_db"
    
    @property
    def TEST_DATABASE_URL(self) -> str:
        return f"postgresql://sune:{self.LOCAL_DB_PASSWORD}@localhost:5432/test_db"
    
    @property
    def get_database_url(self) -> str:
        # First try DATABASE_URL, then RENDER_DATABASE_URL, finally fallback to local
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if os.getenv("RENDER") and self.RENDER_DATABASE_URL:
            return self.RENDER_DATABASE_URL
        return self.LOCAL_DATABASE_URL
    
    # Weather settings
    WEATHER_LOCATION: str = "Copenhagen"  # Default location
    WEATHER_LAT: float = 55.676098  # Copenhagen latitude
    WEATHER_LON: float = 12.568337  # Copenhagen longitude
    WEATHER_API_URL: str = "https://api.open-meteo.com/v1/forecast"
    WEATHER_UPDATE_INTERVAL: int = 21600  # 6 hours in seconds

    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Plant Watering System"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields in the settings

settings = Settings() 