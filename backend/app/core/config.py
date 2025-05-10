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
        extra = "allow"

settings = Settings() 