from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.models.watering_schedule import WateringSchedule
from app.schemas.watering_schedule import WateringScheduleCreate, WateringScheduleUpdate
from fastapi import HTTPException
from datetime import date, datetime, timedelta
from app.models.user_plants import UserPlant
from app.models.plants import Plant
from app.models.watering import Watering
from app.models.users import User
import logging
from typing import List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_user_watering_schedule(db: Session, user_id: int) -> List[dict]:
    """Get simplified watering schedule for all plants of a user"""
    try:
        logger.info(f"Getting watering schedule for user {user_id}")
        
        # Get all user plants with their watering info in a single query
        user_plants = (
            db.query(UserPlant)
            .filter(UserPlant.user_id == user_id)
            .options(
                joinedload(UserPlant.plant).joinedload(Plant.watering_info)
            )
            .all()
        )
        
        if not user_plants:
            logger.info(f"No plants found for user {user_id}")
            return []
        
        # Get last watering dates for all plants in a single query
        last_waterings = (
            db.query(WateringSchedule)
            .filter(
                WateringSchedule.user_id == user_id,
                WateringSchedule.completed == True
            )
            .order_by(WateringSchedule.completion_timestamp.desc())
            .all()
        )
        
        # Create a map of last watering dates
        last_watering_dates = {}
        for watering in last_waterings:
            if watering.plant_id not in last_watering_dates:
                last_watering_dates[watering.plant_id] = watering.completion_timestamp
        
        # Process each plant
        schedule = []
        for user_plant in user_plants:
            try:
                if not user_plant.plant or not user_plant.plant.watering_info:
                    logger.warning(f"Missing plant or watering info for user_plant {user_plant.id}")
                    continue
                
                # Get watering info
                watering_info = user_plant.plant.watering_info
                
                # Get last watering date
                last_watering = last_watering_dates.get(user_plant.plant_id)
                
                # Calculate next watering date
                if last_watering:
                    next_watering = last_watering + timedelta(days=watering_info.frequency_days)
                else:
                    # If never watered, schedule for tomorrow
                    next_watering = datetime.now() + timedelta(days=1)
                
                # Only add to schedule if next watering is within next 7 days
                if next_watering <= datetime.now() + timedelta(days=7):
                    schedule.append({
                        "plant_id": user_plant.plant_id,
                        "plant_name": user_plant.plant.common_name,
                        "next_watering": next_watering,
                        "section": user_plant.section,
                        "frequency_days": watering_info.frequency_days,
                        "last_watering": last_watering
                    })
            except Exception as e:
                logger.error(f"Error processing plant {user_plant.plant_id}: {str(e)}")
                continue
        
        # Sort schedule by next watering date
        schedule.sort(key=lambda x: x["next_watering"])
        
        logger.info(f"Generated watering schedule with {len(schedule)} entries")
        return schedule
    except Exception as e:
        logger.error(f"Error in get_user_watering_schedule: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating watering schedule: {str(e)}"
        )

def create_watering_schedule(db: Session, user_id: int, plant_id: int):
    """Create a new watering schedule for a plant"""
    try:
        logger.info(f"Creating watering schedule for user {user_id}, plant {plant_id}")
        
        # Get plant and its watering requirements
        plant = db.query(Plant).filter(Plant.id == plant_id).first()
        if not plant:
            logger.error(f"Plant {plant_id} not found")
            raise ValueError("Plant not found")
        
        watering_info = db.query(Watering).filter(Watering.plant_id == plant_id).first()
        if not watering_info:
            logger.error(f"No watering information found for plant {plant_id}")
            raise ValueError("Plant watering information not found")

        # Create a simple schedule based on frequency
        schedule = WateringSchedule(
            user_id=user_id,
            plant_id=plant_id,
            scheduled_date=datetime.now() + timedelta(days=watering_info.frequency_days),
            water_needed=True,
            volume_needed=watering_info.volume_feet,
            weather_dependent=False
        )
        
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        
        logger.info("Successfully created watering schedule")
        return schedule
    except Exception as e:
        logger.error(f"Error creating watering schedule: {str(e)}")
        raise

def get_schedule(db: Session, schedule_id: int):
    return db.query(WateringSchedule).filter(WateringSchedule.id == schedule_id).first()

def get_user_schedules(db: Session, user_id: int, date_from: date = None, date_to: date = None):
    query = db.query(WateringSchedule).filter(WateringSchedule.user_id == user_id)
    
    if date_from:
        query = query.filter(WateringSchedule.scheduled_date >= date_from)
    if date_to:
        query = query.filter(WateringSchedule.scheduled_date <= date_to)
        
    return query.order_by(WateringSchedule.scheduled_date).all()

def get_user_plant_schedules(
    db: Session, user_id: int, plant_id: int, 
    date_from: date = None, date_to: date = None
):
    query = db.query(WateringSchedule).filter(
        WateringSchedule.user_id == user_id,
        WateringSchedule.plant_id == plant_id
    )
    
    if date_from:
        query = query.filter(WateringSchedule.scheduled_date >= date_from)
    if date_to:
        query = query.filter(WateringSchedule.scheduled_date <= date_to)
        
    return query.order_by(WateringSchedule.scheduled_date).all()

def update_schedule(db: Session, schedule_id: int, schedule_update: WateringScheduleUpdate):
    db_schedule = get_schedule(db, schedule_id)
    if not db_schedule:
        return None
    
    update_data = schedule_update.model_dump(exclude_unset=True)
    
    if schedule_update.completed:
        update_data["completion_timestamp"] = datetime.utcnow()
        
        # Create next schedule if completed
        if db_schedule.plant_id:
            plant = db.query(Plant).filter(Plant.id == db_schedule.plant_id).first()
            if plant and plant.watering_info:
                next_schedule = WateringSchedule(
                    user_id=db_schedule.user_id,
                    plant_id=db_schedule.plant_id,
                    scheduled_date=datetime.utcnow() + timedelta(days=plant.watering_info.frequency_days),
                    water_needed=True,
                    volume_needed=plant.watering_info.volume_feet,
                    weather_dependent=False
                )
                db.add(next_schedule)
    
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_schedule(db: Session, schedule_id: int):
    db_schedule = get_schedule(db, schedule_id)
    if not db_schedule:
        return False
    
    db.delete(db_schedule)
    db.commit()
    return True

def get_upcoming_schedules(db: Session, user_id: int, days: int = 7):
    today = date.today()
    end_date = today + timedelta(days=days)
    return db.query(WateringSchedule).filter(
        WateringSchedule.user_id == user_id,
        WateringSchedule.scheduled_date >= today,
        WateringSchedule.scheduled_date <= end_date,
        WateringSchedule.completed == False
    ).order_by(WateringSchedule.scheduled_date).all()
