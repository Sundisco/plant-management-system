from pydantic import EmailStr
from typing import List, Optional
from datetime import datetime
from app.schemas.base import BaseSchema
from app.schemas.plants import Plant

class UserBase(BaseSchema):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

class UserPlantAdd(BaseSchema):
    plant_id: int

class UserWithPlants(User):
    plants: List[Plant] = [] 