from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.sections import Section
from app.schemas.sections import SectionCreate, SectionUpdate, SectionOut
from app.database import get_db
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{user_id}", response_model=List[SectionOut])
def get_sections(user_id: int, db: Session = Depends(get_db)):
    """Get all sections for a user"""
    try:
        logger.info(f"Fetching sections for user {user_id}")
        sections = db.query(Section).filter(Section.user_id == user_id).all()
        logger.info(f"Found {len(sections)} sections")
        return sections
    except Exception as e:
        logger.error(f"Error fetching sections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}", response_model=SectionOut)
def create_section(user_id: int, section: SectionCreate, db: Session = Depends(get_db)):
    """Create a new section for a user"""
    try:
        logger.info(f"Creating section for user {user_id}: {section.dict()}")
        db_section = Section(user_id=user_id, **section.dict())
        db.add(db_section)
        db.commit()
        db.refresh(db_section)
        logger.info(f"Created section with ID {db_section.id}")
        return db_section
    except Exception as e:
        logger.error(f"Error creating section: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{section_id}", response_model=SectionOut)
def update_section(section_id: int, section: SectionUpdate, db: Session = Depends(get_db)):
    """Update a section's name"""
    try:
        logger.info(f"Updating section {section_id}: {section.dict()}")
        db_section = db.query(Section).filter(Section.id == section_id).first()
        if not db_section:
            logger.warning(f"Section {section_id} not found")
            raise HTTPException(status_code=404, detail="Section not found")
        
        for key, value in section.dict().items():
            setattr(db_section, key, value)
        
        db.commit()
        db.refresh(db_section)
        logger.info(f"Updated section {section_id}")
        return db_section
    except Exception as e:
        logger.error(f"Error updating section: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{section_id}")
def delete_section(section_id: int, db: Session = Depends(get_db)):
    """Delete a section"""
    try:
        logger.info(f"Deleting section {section_id}")
        db_section = db.query(Section).filter(Section.id == section_id).first()
        if not db_section:
            logger.warning(f"Section {section_id} not found")
            raise HTTPException(status_code=404, detail="Section not found")
        db.delete(db_section)
        db.commit()
        logger.info(f"Deleted section {section_id}")
        return {"detail": "Section deleted"}
    except Exception as e:
        logger.error(f"Error deleting section: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
