from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with plants through user_plants
    plants = relationship("Plant", secondary="user_plants", back_populates="users")

    # Add to User class
    watering_schedules = relationship("WateringSchedule", back_populates="user")
    user_plants = relationship("UserPlant", back_populates="user", cascade="all, delete-orphan") 