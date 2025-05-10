from sqlalchemy import Column, Integer, Date, Boolean, Float, DateTime, ForeignKey, UniqueConstraint, String, Index
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import date, datetime

class WateringSchedule(Base):
    __tablename__ = "watering_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False, index=True)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    completion_timestamp = Column(DateTime, nullable=True)
    water_needed = Column(Boolean, default=True)
    volume_needed = Column(Float, nullable=True)
    weather_dependent = Column(Boolean, default=False)
    next_scheduled_date = Column(DateTime, nullable=True)

    # Add composite indexes for common queries
    __table_args__ = (
        Index('idx_user_scheduled_date', 'user_id', 'scheduled_date'),
        Index('idx_user_plant_scheduled', 'user_id', 'plant_id', 'scheduled_date'),
        Index('idx_completion_status', 'user_id', 'scheduled_date', 'water_needed'),
    )

    # Relationships
    user = relationship("User", back_populates="watering_schedules")
    plant = relationship("Plant", back_populates="watering_schedules")

    # Unique constraint for user_id, plant_id, and scheduled_date
    __table_args__ = (
        UniqueConstraint('user_id', 'plant_id', 'scheduled_date', 
                        name='watering_schedule_user_id_plant_id_scheduled_date_key'),
    )
