# /backend/app/models/plant_guides.py
from sqlalchemy import Column, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint
from app.database import Base

class PlantGuide(Base):
    __tablename__ = "plant_guides"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))
    type = Column(Text)
    description = Column(Text, nullable=False)

    plant = relationship("Plant", back_populates="guides")  # Define relationship to Plant model
