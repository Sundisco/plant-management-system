from sqlalchemy import Column, Integer, ForeignKey, String
from app.database import Base
from sqlalchemy.schema import Sequence

class UserPlant(Base):
    __tablename__ = "user_plants"

    id = Column(Integer, Sequence('user_plant_id_seq'), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    section = Column(String, nullable=True) 