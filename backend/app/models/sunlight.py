from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Sunlight(Base):
    __tablename__ = "sunlight"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))
    condition = Column(Text, default='Unknown')

    # Relationship with Plant model
    plant = relationship("Plant", back_populates="sunlight_info")
