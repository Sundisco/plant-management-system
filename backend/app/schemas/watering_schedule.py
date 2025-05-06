from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from app.schemas.base import BaseSchema

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
