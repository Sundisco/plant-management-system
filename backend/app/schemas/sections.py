from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SectionBase(BaseModel):
    section_id: str
    name: str
    glyph: Optional[str] = None

class SectionCreate(BaseModel):
    section_id: str
    name: str
    glyph: Optional[str] = None

class SectionUpdate(BaseModel):
    name: str
    glyph: Optional[str] = None

class SectionOut(SectionBase):
    id: int
    user_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
