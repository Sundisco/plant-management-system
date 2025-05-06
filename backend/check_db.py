from app.database import SessionLocal
from app.models.weather_forecast import WeatherForecast
from app.models.plants import Plant
from app.models.watering import Watering
from app.models.user_plants import UserPlant

def check_database():
    db = SessionLocal()
    try:
        print("Database Statistics:")
        print(f"Plants: {db.query(Plant).count()}")
        print(f"User Plants: {db.query(UserPlant).count()}")
        print(f"Watering Info: {db.query(Watering).count()}")
        print(f"Weather Forecasts: {db.query(WeatherForecast).count()}")
        
        # Check if we have any weather data
        latest_forecast = db.query(WeatherForecast)\
            .order_by(WeatherForecast.timestamp.desc())\
            .first()
        
        if latest_forecast:
            print(f"\nLatest weather forecast:")
            print(f"Timestamp: {latest_forecast.timestamp}")
            print(f"Location: {latest_forecast.location}")
            print(f"Temperature: {latest_forecast.temperature}°C")
            print(f"Precipitation: {latest_forecast.precipitation}mm")
            print(f"Wind Speed: {latest_forecast.wind_speed}km/h")
        else:
            print("\nNo weather forecasts found in the database")
            
        # Check watering data for user plants
        print("\nChecking watering data for user plants:")
        user_plants = db.query(UserPlant).all()
        for user_plant in user_plants:
            plant = db.query(Plant).filter(Plant.id == user_plant.plant_id).first()
            watering = db.query(Watering).filter(Watering.plant_id == user_plant.plant_id).first()
            print(f"\nPlant: {plant.common_name if plant else 'Unknown'}")
            print(f"Section: {user_plant.section}")
            if watering:
                print(f"Watering Info:")
                print(f"  Frequency: {watering.frequency_days} days")
                print(f"  Depth: {watering.depth_mm}mm")
                print(f"  Volume: {watering.volume_feet} feet")
                print(f"  Period: {watering.period}")
                print(f"  Drought Tolerant: {watering.drought_tolerant}")
                print(f"  Soil: {watering.soil}")
            else:
                print("No watering info found")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_database() 