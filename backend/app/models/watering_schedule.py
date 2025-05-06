from sqlalchemy import Column, Integer, Date, Boolean, Float, DateTime, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import date, datetime

class WateringSchedule(Base):
    __tablename__ = "watering_schedule"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    day = Column(String)  # MON, TUE, etc.
    amount = Column(Float)  # Percentage or specific amount
    weather_dependent = Column(Boolean, default=True)
    scheduled_date = Column(Date, nullable=False)
    water_needed = Column(Boolean, nullable=False, default=True)
    volume_needed = Column(Float)  # double precision
    completed = Column(Boolean, nullable=False, default=False)
    completion_timestamp = Column(DateTime)
    next_scheduled_date = Column(Date)

    # Relationships
    user = relationship("User", back_populates="watering_schedules")
    plant = relationship("Plant", back_populates="watering_schedules")

    # Unique constraint for user_id, plant_id, and scheduled_date
    __table_args__ = (
        UniqueConstraint('user_id', 'plant_id', 'scheduled_date', 
                        name='watering_schedule_user_id_plant_id_scheduled_date_key'),
    )
