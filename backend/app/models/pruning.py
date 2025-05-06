from sqlalchemy import Column, Integer, Text, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Pruning(Base):
    __tablename__ = "pruning"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))
    frequency = Column(Integer)
    months = Column(ARRAY(Text))
    interval = Column(Text, default='Unknown')

    # Relationship with Plant model
    plant = relationship("Plant", back_populates="pruning_info")
