from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with plants through user_plants
    plants = relationship("Plant", secondary="user_plants", back_populates="users")

    # Add to User class
    watering_schedules = relationship("WateringSchedule", back_populates="user") 