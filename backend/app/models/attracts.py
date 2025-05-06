from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Attracts(Base):
    __tablename__ = "attracts"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))
    species = Column(Text, nullable=False)

    # Relationship with Plant model
    plant = relationship("Plant", back_populates="attracts")
