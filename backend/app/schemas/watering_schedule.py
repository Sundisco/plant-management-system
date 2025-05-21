from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from app.schemas.base import BaseSchema

# Original schemas for backward compatibility
class WateringScheduleBase(BaseSchema):
    user_id: int
    plant_id: int
    scheduled_date: date
    water_needed: bool = True
    volume_needed: Optional[float] = None
    completed: bool = False
    next_scheduled_date: Optional[date] = None

class WateringScheduleCreate(WateringScheduleBase):
    pass

class WateringSchedule(WateringScheduleBase):
    id: int
    completion_timestamp: Optional[datetime] = None

class WateringScheduleUpdate(BaseSchema):
    completed: bool
    completion_timestamp: Optional[datetime] = None
    next_scheduled_date: Optional[date] = None
    batch_update: Optional[bool] = None

# New schemas for weather-based adjustments
class WeatherData(BaseModel):
    temperature: float
    precipitation: float
    wind_speed: float
    is_forecast: bool = True

class PlantSchedule(BaseModel):
    plant_id: int
    plant_name: str
    image_url: Optional[str]
    watering_info: Dict[str, Any]
    last_watered: Optional[str]
    is_watered: bool
    weather_adjusted: bool = False

class SectionSchedule(BaseModel):
    section: str
    groups: List[Dict[str, List[PlantSchedule]]]
    watering_stats: Dict[str, Any]

class DaySchedule(BaseModel):
    date: str
    sections: List[SectionSchedule]
    weather: Optional[WeatherData]
    weather_icons: List[str] = []

class WateringScheduleOverview(BaseModel):
    schedule: List[DaySchedule]
    last_updated: str

# New response model for weather-adjusted schedules
class WateringScheduleResponse(BaseModel):
    id: int
    user_plant_id: int
    next_watering: datetime
    is_adjusted: bool = False

    class Config:
        from_attributes = True
