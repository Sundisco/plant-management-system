from sqlalchemy import Column, Integer, Float, Text, Boolean, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Watering(Base):
    __tablename__ = "watering"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))
    frequency_days = Column(Integer)
    depth_mm = Column(Integer)
    volume_feet = Column(Float)
    period = Column(Text)
    drought_tolerant = Column(Boolean, default=False)
    soil = Column(ARRAY(Text))

    # Update relationship name to match Plant model
    plant = relationship("Plant", back_populates="watering_info")
