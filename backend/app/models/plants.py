# /backend/app/models/plants.py
from sqlalchemy import Column, Integer, String, ARRAY, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    common_name = Column(Text)
    scientific_name = Column(ARRAY(Text))
    other_names = Column(ARRAY(Text))
    family = Column(Text)
    type = Column(Text)
    description = Column(Text)
    growth_rate = Column(Text)
    maintenance = Column(Text)
    hardiness_zone = Column(Text)
    image_url = Column(Text)
    cycle = Column(Text)
    watering = Column(Text)
    is_evergreen = Column(Boolean, default=False)
    edible_fruit = Column(Boolean, default=False)

    # Add checks for the growth_rate, maintenance, and type columns (not implemented in SQLAlchemy directly)
    # These can be managed at the database level as constraints

    guides = relationship("PlantGuide", back_populates="plant", cascade="all, delete")
    watering_info = relationship("Watering", back_populates="plant", uselist=False, cascade="all, delete-orphan")
    pruning_info = relationship("Pruning", back_populates="plant", uselist=False, cascade="all, delete-orphan")
    sunlight_info = relationship("Sunlight", back_populates="plant", cascade="all, delete-orphan")
    attracts = relationship("Attracts", back_populates="plant", cascade="all, delete-orphan")
    users = relationship("User", secondary="user_plants", back_populates="plants", overlaps="user_plants")
    watering_schedules = relationship("WateringSchedule", back_populates="plant")
    user_plants = relationship("UserPlant", back_populates="plant", cascade="all, delete-orphan", overlaps="plants,users")
