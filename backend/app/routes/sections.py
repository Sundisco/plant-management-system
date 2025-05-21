from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.sections import Section
from app.schemas.sections import SectionCreate, SectionUpdate, SectionOut
from app.database import get_db

router = APIRouter()

@router.get("/{user_id}", response_model=List[SectionOut])
def get_sections(user_id: int, db: Session = Depends(get_db)):
    """Get all sections for a user"""
    return db.query(Section).filter(Section.user_id == user_id).all()

@router.post("/{user_id}", response_model=SectionOut)
def create_section(user_id: int, section: SectionCreate, db: Session = Depends(get_db)):
    """Create a new section for a user"""
    db_section = Section(user_id=user_id, **section.model_dump())
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

@router.put("/{section_id}", response_model=SectionOut)
def update_section(section_id: int, section: SectionUpdate, db: Session = Depends(get_db)):
    """Update a section's name"""
    db_section = db.query(Section).filter(Section.id == section_id).first()
    if not db_section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    for key, value in section.model_dump().items():
        setattr(db_section, key, value)
    
    db.commit()
    db.refresh(db_section)
    return db_section

@router.delete("/{section_id}")
def delete_section(section_id: int, db: Session = Depends(get_db)):
    """Delete a section"""
    db_section = db.query(Section).filter(Section.id == section_id).first()
    if not db_section:
        raise HTTPException(status_code=404, detail="Section not found")
    db.delete(db_section)
    db.commit()
    return {"detail": "Section deleted"}
