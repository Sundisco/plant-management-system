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
from typing import List, Optional, Dict
from collections import defaultdict
import functools
from cachetools import TTLCache, cached
from app.models.weather_forecast import WeatherForecast
from app.core.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cache for user plants data (5 minutes TTL)
user_plants_cache = TTLCache(maxsize=100, ttl=300)

@cached(cache=user_plants_cache)
def _get_user_plants(db: Session, user_id: int) -> List[UserPlant]:
    """Get user plants with their watering info (cached)"""
    return (
            db.query(UserPlant)
            .filter(UserPlant.user_id == user_id)
            .options(
                joinedload(UserPlant.plant).joinedload(Plant.watering_info)
            )
            .all()
        )

def get_user_watering_schedule(db: Session, user_id: int) -> dict:
    """Get simplified watering schedule for all plants of a user"""
    try:
        logger.info(f"Getting watering schedule for user {user_id}")
        
        # Get user plants from cache
        user_plants = _get_user_plants(db, user_id)
        
        if not user_plants:
            logger.info(f"No plants found for user {user_id}")
            return {"schedule": [], "last_updated": datetime.now().isoformat()}
        
        # Get all watering schedules for these plants
        plant_ids = [up.plant_id for up in user_plants]
        schedules = db.query(WateringSchedule).filter(
                WateringSchedule.user_id == user_id,
            WateringSchedule.plant_id.in_(plant_ids)
        ).order_by(WateringSchedule.scheduled_date).all()

        today = datetime.now().date()
        # Build a mapping: (date, section) -> list of plant dicts
        day_section_plants: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))

        for user_plant in user_plants:
            section = user_plant.section if user_plant.section else "Unassigned"
            if not user_plant.plant or not user_plant.plant.watering_info:
                continue
            plant_schedules = [s for s in schedules if s.plant_id == user_plant.plant_id]
            # 1. Add completed schedule for today (if exists)
            for sched in plant_schedules:
                if sched.completed and sched.completion_timestamp and sched.completion_timestamp.date() == today:
                    day_section_plants[today.isoformat()][section].append({
                        "plant_id": user_plant.plant_id,
                        "plant_name": user_plant.plant.common_name,
                        "image_url": user_plant.plant.image_url,
                        "frequency_days": user_plant.plant.watering_info.frequency_days,
                        "depth_mm": user_plant.plant.watering_info.depth_mm,
                        "volume_feet": user_plant.plant.watering_info.volume_feet,
                        "next_watering": today.isoformat(),
                        "last_watered": today.isoformat()
                    })
            # 2. Add all future, uncompleted schedules
            for sched in plant_schedules:
                if not sched.completed and sched.scheduled_date >= today:
                    day_section_plants[sched.scheduled_date.isoformat()][section].append({
                        "plant_id": user_plant.plant_id,
                        "plant_name": user_plant.plant.common_name,
                        "image_url": user_plant.plant.image_url,
                        "frequency_days": user_plant.plant.watering_info.frequency_days,
                        "depth_mm": user_plant.plant.watering_info.depth_mm,
                        "volume_feet": user_plant.plant.watering_info.volume_feet,
                        "next_watering": sched.scheduled_date.isoformat(),
                        "last_watered": sched.completion_timestamp.date().isoformat() if sched.completion_timestamp else None
                    })

        # Create a schedule for the next 21 days (to accommodate the highest interval)
        schedule = []
        for day in range(21):  # Show three weeks
            current_date = today + timedelta(days=day)
            day_str = current_date.strftime("%Y-%m-%d")
        
            # Get weather forecast for this day
            weather_forecast = get_weather_forecast(db)

            # Create day schedule
            day_schedule = {
                "date": day_str,
                "sections": []
            }

            # Add weather data if forecast exists
            if weather_forecast and day < 7:  # Only add weather data for next 7 days
                day_schedule["weather"] = {
                    "temperature": round(weather_forecast[day_str]["temperature"], 1),
                    "precipitation": round(weather_forecast[day_str]["precipitation"], 1),
                    "wind_speed": round(weather_forecast[day_str]["wind_speed"], 1)
                }
                # Determine weather icons based on conditions
                weather_icons = weather_forecast[day_str]["weather_icons"]
                day_schedule["weather_icons"] = weather_icons

            # Add sections if they exist for this day
            for section, plants in day_section_plants[day_str].items():
                if plants:
                    section_plants = []
                    total_plants = len(plants)
                    watered_plants = sum(1 for plant in plants if plant.get("last_watered") == day_str)
                    for plant in plants:
                        section_plants.append({
                            "plant_id": plant["plant_id"],
                            "plant_name": plant["plant_name"],
                            "image_url": plant["image_url"],
                            "watering_info": {
                                "frequency_days": plant["frequency_days"],
                                "depth_mm": plant["depth_mm"],
                                "volume_feet": plant["volume_feet"]
                            },
                            "last_watered": plant.get("last_watered"),
                            "is_watered": plant.get("last_watered") == day_str
                        })
                    day_schedule["sections"].append({
                        "section": section,
                        "groups": [{"plants": section_plants}],
                        "watering_stats": {
                            "total_plants": total_plants,
                            "watered_plants": watered_plants,
                            "percentage": (watered_plants / total_plants) * 100 if total_plants > 0 else 0
                        }
                    })

            # Always add the day to the schedule, even if there are no plants
            schedule.append(day_schedule)

        return {
            "schedule": schedule,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting watering schedule: {str(e)}")
        raise

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

        today = datetime.now().date()
        
        # Check if a schedule already exists for this plant
        existing_schedule = db.query(WateringSchedule).filter(
            WateringSchedule.user_id == user_id,
            WateringSchedule.plant_id == plant_id,
            WateringSchedule.scheduled_date == today
        ).first()
        
        if existing_schedule:
            logger.info(f"Schedule already exists for plant {plant_id} on {today}")
            return existing_schedule
        
        # Create a schedule for today
        schedule = WateringSchedule(
            user_id=user_id,
            plant_id=plant_id,
            scheduled_date=today,
            water_needed=True,
            volume_needed=watering_info.volume_feet,
            weather_dependent=False,
            completed=False,  # Never completed by default
            completion_timestamp=None,  # No completion timestamp
            next_scheduled_date=None  # Don't set next scheduled date until plant is watered
        )
        
        # Ensure the schedule is not marked as completed
        if schedule.completed:
            schedule.completed = False
            schedule.completion_timestamp = None
        
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

def calculate_weather_impact(temperature: float, precipitation: float) -> tuple[float, int]:
    """Calculate the impact of weather conditions on watering needs"""
    volume_adjustment = 1.0
    date_adjustment = 0
    
    # Temperature impact
    if temperature > 30:
        volume_adjustment *= 1.2  # Increase volume by 20%
        date_adjustment -= 1  # Water one day earlier
    elif temperature < 10:
        volume_adjustment *= 0.8  # Decrease volume by 20%
        date_adjustment += 1  # Water one day later
    
    # Precipitation impact
    if precipitation > 10:
        volume_adjustment *= 0.5  # Decrease volume by 50%
        date_adjustment += 1  # Water one day later
    
    return volume_adjustment, date_adjustment

def adjust_watering_date(scheduled_date: date, adjustment_days: int) -> date:
    """Adjust a watering date by the specified number of days"""
    return scheduled_date + timedelta(days=adjustment_days)

def update_schedule(db: Session, schedule_id: int, schedule_update: WateringScheduleUpdate):
    """Update a watering schedule and handle next watering date"""
    try:
        logger.info(f"Updating schedule {schedule_id}")
        db_schedule = get_schedule(db, schedule_id)
        if not db_schedule:
            logger.error(f"Schedule {schedule_id} not found")
            return None

        update_data = schedule_update.model_dump(exclude_unset=True)
        today = datetime.now().date()

        # Handle completion status changes
        if schedule_update.completed and not db_schedule.completed:
            # If marking as completed, set completion timestamp to now
            update_data["completion_timestamp"] = datetime.utcnow()
            
            # Get plant and its watering requirements
            plant = db.query(Plant).filter(Plant.id == db_schedule.plant_id).first()
            if not plant or not plant.watering_info:
                logger.error(f"Plant or watering info not found for plant {db_schedule.plant_id}")
                return None

            # Calculate base next date from frequency
            next_date = today + timedelta(days=plant.watering_info.frequency_days)
            
            # Get weather forecast for the next date
            forecast = db.query(WeatherForecast).filter(
                WeatherForecast.timestamp >= next_date,
                WeatherForecast.timestamp < next_date + timedelta(days=1)
            ).order_by(WeatherForecast.timestamp).first()
            
            if forecast:
                # Adjust based on temperature
                if forecast.temperature > 30:
                    next_date = next_date - timedelta(days=1)
                    logger.info(f"Adjusted next watering date due to high temperature")
                
                # Adjust based on precipitation
                if forecast.precipitation > 10:
                    next_date = next_date + timedelta(days=1)
                    logger.info(f"Adjusted next watering date due to high precipitation")

            # Check if a schedule already exists for the next date
            existing_schedule = db.query(WateringSchedule).filter(
                WateringSchedule.user_id == db_schedule.user_id,
                WateringSchedule.plant_id == db_schedule.plant_id,
                WateringSchedule.scheduled_date == next_date
            ).first()

            if not existing_schedule:
                # Create next schedule with weather adjustment info
                next_schedule = WateringSchedule(
                    user_id=db_schedule.user_id,
                    plant_id=db_schedule.plant_id,
                    scheduled_date=next_date,
                    water_needed=True,
                    volume_needed=plant.watering_info.volume_feet,
                    weather_dependent=True,
                    completed=False,
                    completion_timestamp=None,
                    weather_adjusted=forecast is not None and (forecast.temperature > 30 or forecast.precipitation > 10),
                    frequency_days=plant.watering_info.frequency_days,
                    depth_mm=plant.watering_info.depth_mm,
                    volume_feet=plant.watering_info.volume_feet
                )
                db.add(next_schedule)
                db.commit()  # Commit to ensure the next schedule is saved
                logger.info(f"Created next schedule for {next_date}")

            # Only adjust all schedules for weather if batch_update is not True
            if not getattr(schedule_update, 'batch_update', False):
                adjust_all_schedules_for_weather(db, db_schedule.user_id)

        elif not schedule_update.completed and db_schedule.completed:
            # If unmarking as completed, clear completion timestamp
            update_data["completion_timestamp"] = None

        # If not completed and scheduled date is in the past, update to today
        if not schedule_update.completed and db_schedule.scheduled_date < today:
            update_data["scheduled_date"] = today
            update_data["water_needed"] = True

        # Update the schedule
        for key, value in update_data.items():
            setattr(db_schedule, key, value)

        db.commit()
        db.refresh(db_schedule)
        return db_schedule

    except Exception as e:
        logger.error(f"Error updating schedule: {str(e)}")
        db.rollback()
        raise

def adjust_all_schedules_for_weather(db: Session, user_id: int):
    """Adjust all schedules for a user based on real weather data"""
    try:
        today = datetime.now().date()
        # Get all incomplete schedules for the user
        schedules = db.query(WateringSchedule).filter(
            WateringSchedule.user_id == user_id,
            WateringSchedule.completed == False,
            WateringSchedule.scheduled_date >= today
        ).all()
        
        # Get weather forecasts for the next 7 days
        forecasts = db.query(WeatherForecast).filter(
            WeatherForecast.timestamp >= today,
            WeatherForecast.timestamp < today + timedelta(days=7)
        ).order_by(WeatherForecast.timestamp).all()
        
        # Group forecasts by day
        daily_forecasts = {}
        for forecast in forecasts:
            date_str = forecast.timestamp.date().isoformat()
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    "temperatures": [],
                    "precipitations": [],
                    "wind_speeds": []
                }
            daily_forecasts[date_str]["temperatures"].append(forecast.temperature)
            daily_forecasts[date_str]["precipitations"].append(forecast.precipitation)
            daily_forecasts[date_str]["wind_speeds"].append(forecast.wind_speed)
        
        # Calculate daily averages
        weather_data = {}
        for date_str, data in daily_forecasts.items():
            avg_temp = sum(data["temperatures"]) / len(data["temperatures"])
            avg_precip = sum(data["precipitations"]) / len(data["precipitations"])
            avg_wind = sum(data["wind_speeds"]) / len(data["wind_speeds"])
            
            weather_data[date_str] = {
                "temperature": round(avg_temp, 1),
                "precipitation": round(avg_precip, 1),
                "wind_speed": round(avg_wind, 1)
            }
        
        for schedule in schedules:
            original_date = schedule.scheduled_date
            date_str = original_date.isoformat()
            
            # Get weather data for the scheduled date
            if date_str in weather_data:
                weather = weather_data[date_str]
                
                # Adjust based on temperature
                if weather["temperature"] > 30:
                    schedule.scheduled_date = original_date - timedelta(days=1)
                    schedule.weather_adjusted = True
                    logger.info(f"Adjusted schedule {schedule.id} from {original_date} to {schedule.scheduled_date} due to high temperature")
                
                # Adjust based on precipitation
                if weather["precipitation"] > 10:
                    schedule.scheduled_date = original_date + timedelta(days=1)
                    schedule.weather_adjusted = True
                    logger.info(f"Adjusted schedule {schedule.id} from {original_date} to {schedule.scheduled_date} due to high precipitation")
        
        db.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error adjusting schedules for weather: {str(e)}")
        db.rollback()
        return False

def get_schedules(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all watering schedules for a user"""
    try:
        # First adjust all schedules for weather
        adjust_all_schedules_for_weather(db, user_id)
        
        # Then get the adjusted schedules
        schedules = db.query(WateringSchedule).filter(
            WateringSchedule.user_id == user_id
        ).offset(skip).limit(limit).all()
        
        return schedules
    except Exception as e:
        logger.error(f"Error getting schedules: {str(e)}")
        return []

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

def get_weather_forecast(db: Session) -> dict:
    """Get weather forecast for the next 7 days"""
    try:
        # Get weather forecasts from database
        forecasts = db.query(WeatherForecast)\
            .filter(WeatherForecast.timestamp >= datetime.now())\
            .filter(WeatherForecast.timestamp <= datetime.now() + timedelta(days=7))\
            .order_by(WeatherForecast.timestamp)\
            .all()
        
        # Group forecasts by day and calculate daily averages
        daily_forecasts = {}
        for forecast in forecasts:
            date_str = forecast.timestamp.date().isoformat()
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    "temperatures": [],
                    "precipitations": [],
                    "wind_speeds": []
                }
            
            daily_forecasts[date_str]["temperatures"].append(forecast.temperature)
            daily_forecasts[date_str]["precipitations"].append(forecast.precipitation)
            daily_forecasts[date_str]["wind_speeds"].append(forecast.wind_speed)
        
        # Calculate daily averages and determine weather icons
        result = {}
        for date_str, data in daily_forecasts.items():
            avg_temp = sum(data["temperatures"]) / len(data["temperatures"])
            avg_precip = sum(data["precipitations"]) / len(data["precipitations"])
            avg_wind = sum(data["wind_speeds"]) / len(data["wind_speeds"])
            
            # Determine weather icons based on conditions
            weather_icons = []
            if avg_precip > 0:
                weather_icons.append("rainy")
            elif avg_temp > 25:
                weather_icons.append("hot")
            elif avg_temp < 10:
                weather_icons.append("cold")
            elif avg_wind > 15:
                weather_icons.append("windy")
            else:
                weather_icons.append("sunny")
            
            result[date_str] = {
                "temperature": round(avg_temp, 1),
                "precipitation": round(avg_precip, 1),
                "wind_speed": round(avg_wind, 1),
                "weather_icons": weather_icons
            }
        
        return result
    except Exception as e:
        logger.error(f"Error getting weather forecast: {str(e)}")
        # Return empty forecast if there's an error
        return {}

def update_schedule_for_weather(db: Session, schedule: WateringSchedule, adjusted_date: date) -> WateringSchedule:
    """Update a watering schedule with weather-adjusted date"""
    try:
        # Only update if the date has changed
        if schedule.scheduled_date != adjusted_date:
            schedule.scheduled_date = adjusted_date
            schedule.weather_adjusted = True
            db.commit()
            db.refresh(schedule)
            logger.info(f"Updated schedule {schedule.id} from {schedule.scheduled_date} to {adjusted_date} due to weather")
        return schedule
    except Exception as e:
        logger.error(f"Error updating schedule for weather: {str(e)}")
        return schedule

def adjust_schedule_for_weather(db: Session, schedule: WateringSchedule, forecast: WeatherForecast) -> WateringSchedule:
    """Adjust watering schedule based on weather forecast."""
    # Check if weather conditions require adjustment
    needs_adjustment = False
    
    # High temperature adjustment (above 30°C)
    if forecast.temperature > 30:
        needs_adjustment = True
        schedule.scheduled_date = schedule.scheduled_date - timedelta(days=1)
    
    # High precipitation adjustment (above 10mm)
    if forecast.precipitation > 10:
        needs_adjustment = True
        schedule.scheduled_date = schedule.scheduled_date + timedelta(days=1)
    
    # Update adjustment status
    if needs_adjustment:
        schedule.weather_adjusted = True
    
    return schedule

def get_watering_schedule(db: Session, user_id: int, date: str = None):
    """Get the watering schedule for a user."""
    try:
        logger.info(f"Getting watering schedule for user {user_id}")
        
        # Parse the date if provided, otherwise use today
        if date:
            try:
                target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            except ValueError:
                logger.error(f"Invalid date format: {date}")
                raise ValueError(f"Invalid date format: {date}")
        else:
            target_date = datetime.utcnow()
        
        # Get all user plants
        user_plants = db.query(UserPlant).filter(UserPlant.user_id == user_id).all()
        
        # Get weather forecasts for the next 21 days (3 weeks)
        forecasts = db.query(WeatherForecast).filter(
            WeatherForecast.timestamp >= target_date,
            WeatherForecast.timestamp < target_date + timedelta(days=21)
        ).order_by(WeatherForecast.timestamp).all()
        
        # Group forecasts by day
        daily_forecasts = {}
        for forecast in forecasts:
            date_str = forecast.timestamp.date().isoformat()
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    "temperatures": [],
                    "precipitations": [],
                    "wind_speeds": []
                }
            daily_forecasts[date_str]["temperatures"].append(forecast.temperature)
            daily_forecasts[date_str]["precipitations"].append(forecast.precipitation)
            daily_forecasts[date_str]["wind_speeds"].append(forecast.wind_speed)
        
        # Calculate daily averages and determine weather icons
        weather_data = {}
        for date_str, data in daily_forecasts.items():
            avg_temp = sum(data["temperatures"]) / len(data["temperatures"])
            avg_precip = sum(data["precipitations"]) / len(data["precipitations"])
            avg_wind = sum(data["wind_speeds"]) / len(data["wind_speeds"])
            
            # Determine weather icons based on conditions
            weather_icons = []
            if avg_precip > 0:
                weather_icons.append("rainy")
            elif avg_temp > 25:
                weather_icons.append("hot")
            elif avg_temp < 10:
                weather_icons.append("cold")
            elif avg_wind > 15:
                weather_icons.append("windy")
            else:
                weather_icons.append("sunny")
            
            weather_data[date_str] = {
                "temperature": round(avg_temp, 1),
                "precipitation": round(avg_precip, 1),
                "wind_speed": round(avg_wind, 1),
                "weather_icons": weather_icons
            }
        
        # Initialize schedules for all days in the forecast period
        schedules_by_date = {}
        for i in range(21):  # Show 3 weeks
            current_date = (target_date + timedelta(days=i)).date()
            date_str = current_date.isoformat()
            schedules_by_date[date_str] = {
                "date": date_str,
                "sections": [],
                "weather": weather_data.get(date_str)
            }
        
        # Get all schedules for the user's plants within the date range
        plant_ids = [up.plant_id for up in user_plants]
        start_date = target_date.date()
        end_date = start_date + timedelta(days=21)  # Look ahead 3 weeks
        
        all_schedules = db.query(WateringSchedule).filter(
            WateringSchedule.user_id == user_id,
            WateringSchedule.plant_id.in_(plant_ids),
            WateringSchedule.scheduled_date >= start_date,
            WateringSchedule.scheduled_date < end_date
        ).all()
        
        # Create a mapping of plant_id to its schedule for each date
        plant_schedules = {}
        for schedule in all_schedules:
            date_str = schedule.scheduled_date.isoformat()
            if schedule.plant_id not in plant_schedules:
                plant_schedules[schedule.plant_id] = {}
            plant_schedules[schedule.plant_id][date_str] = schedule
        
        # Add plant schedules
        for user_plant in user_plants:
            plant_schedules_for_plant = plant_schedules.get(user_plant.plant_id, {})
            
            # Get plant details
            plant = db.query(Plant).filter(Plant.id == user_plant.plant_id).first()
            
            # For each date in our range
            for date_str in schedules_by_date.keys():
                schedule = plant_schedules_for_plant.get(date_str)
                
                if schedule:
                    # Find or create section
                    section_name = user_plant.section or "Unassigned"
                    section = next((s for s in schedules_by_date[date_str]["sections"] if s["section"] == section_name), None)
                    
                    if not section:
                        section = {
                            "section": section_name,
                            "groups": [{"plants": []}],
                            "watering_stats": {
                                "total_plants": 0,
                                "watered_plants": 0,
                                "percentage": 0
                            }
                        }
                        schedules_by_date[date_str]["sections"].append(section)
                    
                    # Add plant to section
                    plant_data = {
                        "plant_id": plant.id,
                        "plant_name": plant.common_name,
                        "image_url": plant.image_url,
                        "watering_info": {
                            "frequency_days": plant.watering_info.frequency_days if plant.watering_info else 7,
                            "depth_mm": plant.watering_info.depth_mm if plant.watering_info else 0,
                            "volume_feet": plant.watering_info.volume_feet if plant.watering_info else 0
                        },
                        "last_watered": schedule.completion_timestamp.date().isoformat() if schedule.completion_timestamp else None,
                        "is_watered": schedule.completed,
                        "weather_adjusted": schedule.weather_adjusted,
                        "next_watering": schedule.scheduled_date.isoformat(),
                        "weather_info": {
                            "is_adjusted": schedule.weather_adjusted,
                            "original_date": (schedule.scheduled_date + timedelta(days=1)).isoformat() if schedule.weather_adjusted and schedule.scheduled_date > start_date else None
                        }
                    }
                    section["groups"][0]["plants"].append(plant_data)
                    
                    # Update watering stats
                    section["watering_stats"]["total_plants"] += 1
                    if schedule.completed:
                        section["watering_stats"]["watered_plants"] += 1
                    section["watering_stats"]["percentage"] = (
                        (section["watering_stats"]["watered_plants"] / section["watering_stats"]["total_plants"]) * 100
                        if section["watering_stats"]["total_plants"] > 0 else 0
                    )
        
        # Convert dictionary to list and sort by date
        schedule_list = list(schedules_by_date.values())
        schedule_list.sort(key=lambda x: x["date"])
        
        return {
            "schedule": schedule_list,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting watering schedule: {str(e)}")
        raise

