from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class WeatherForecastBase(BaseModel):
    timestamp: datetime
    location: str
    temperature: Optional[float] = None
    precipitation: Optional[float] = None
    wind_speed: Optional[float] = None

class WeatherForecastCreate(WeatherForecastBase):
    pass

class WeatherForecast(WeatherForecastBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True) 