from sqlalchemy.orm import Session
from app.models.users import User
from app.models.plants import Plant
from app.models.user_plants import UserPlant
from app.schemas.users import UserCreate
from fastapi import HTTPException
from passlib.context import CryptContext
from app.scripts.initialize_watering_schedules import sync_watering_schedules

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def add_plant_to_user(db: Session, user_id: int, plant_id: int):
    # Check if user and plant exist
    user = get_user(db, user_id)
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    
    if not user or not plant:
        raise HTTPException(status_code=404, detail="User or plant not found")
    
    # Check if association already exists
    exists = db.query(UserPlant).filter_by(
        user_id=user_id, plant_id=plant_id
    ).first()
    
    if exists:
        raise HTTPException(status_code=400, detail="Plant already in user's garden")
    
    user_plant = UserPlant(user_id=user_id, plant_id=plant_id)
    db.add(user_plant)
    db.commit()
    
    # Create initial watering schedule
    try:
        from app.services.watering_schedule import create_watering_schedule
        create_watering_schedule(db, user_id, plant_id)
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Error creating watering schedule: {str(e)}")
    
    return user_plant

def remove_plant_from_user(db: Session, user_id: int, plant_id: int):
    user_plant = db.query(UserPlant).filter_by(
        user_id=user_id, plant_id=plant_id
    ).first()
    
    if not user_plant:
        return False
    
    db.delete(user_plant)
    db.commit()
    
    # Sync watering schedules after removing plant
    try:
        sync_watering_schedules()
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Error syncing watering schedules: {str(e)}")
    
    return True

def get_user_plants(db: Session, user_id: int):
    return db.query(Plant).join(UserPlant).filter(UserPlant.user_id == user_id).all() 