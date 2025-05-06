from app.database import SessionLocal
from app.models import User, Plant, UserPlant, WateringSchedule

def test_db_connection():
    try:
        db = SessionLocal()
        print("Successfully connected to database")
        
        # Test User query
        users = db.query(User).all()
        print(f"Found {len(users)} users")
        
        # Test Plant query
        plants = db.query(Plant).all()
        print(f"Found {len(plants)} plants")
        
        # Test UserPlant query
        user_plants = db.query(UserPlant).all()
        print(f"Found {len(user_plants)} user-plant associations")
        
        # Test WateringSchedule query
        schedules = db.query(WateringSchedule).all()
        print(f"Found {len(schedules)} watering schedules")
        
        db.close()
        print("Database connection closed successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    test_db_connection() 