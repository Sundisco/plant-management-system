from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.watering_schedule import WateringSchedule
from app.schemas.watering_schedule import WateringScheduleCreate, WateringScheduleUpdate
from fastapi import HTTPException
from datetime import date, datetime, timedelta
from app.models.user_plants import UserPlant
from app.models.plants import Plant
from app.models.watering import Watering
from app.models.users import User
from app.schemas.watering import WateringBase
from app.services.weather_service import get_weather_forecast, update_weather_forecasts, should_update_forecast
from app.services.watering_adjustment import WateringAdjustment
from app.core.config import settings
import logging
import asyncio
import traceback
from sqlalchemy.orm import joinedload

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_watering_schedule(db: Session, user_id: int, plant_id: int):
    """Create a new watering schedule for a plant"""
    try:
        logger.info(f"Creating watering schedule for user {user_id}, plant {plant_id}")
        
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            raise ValueError("User not found")
        
        # Get plant and its watering requirements
        plant = db.query(Plant).filter(Plant.id == plant_id).first()
        if not plant:
            logger.error(f"Plant {plant_id} not found")
            raise ValueError("Plant not found")
        
        watering_info = db.query(Watering).filter(Watering.plant_id == plant_id).first()
        if not watering_info:
            logger.error(f"No watering information found for plant {plant_id}")
            raise ValueError("Plant watering information not found")

        # Update weather forecasts if needed
        if should_update_forecast(db, settings.WEATHER_LOCATION):
            logger.info("Updating weather forecasts")
            asyncio.run(update_weather_forecasts(db, settings.WEATHER_LOCATION))

        # Get weather forecast for the next week
        weather_forecasts = get_weather_forecast(
            db,
            settings.WEATHER_LOCATION,
            datetime.now(),
            datetime.now() + timedelta(days=7)
        )
        logger.debug(f"Got {len(weather_forecasts)} weather forecasts")

        # Create base watering requirements
        base_watering = WateringBase(
            plant_id=plant_id,
            frequency_days=watering_info.frequency_days,
            depth_mm=watering_info.depth_mm,
            volume_feet=watering_info.volume_feet,
            period=watering_info.period,
            drought_tolerant=watering_info.drought_tolerant,
            soil=watering_info.soil
        )

        # Get adjusted schedule
        adjusted_schedule = WateringAdjustment.get_adjusted_schedule(
            base_watering,
            weather_forecasts
        )
        logger.info(f"Generated adjusted schedule with {len(adjusted_schedule)} entries")

        # Create watering schedule entries
        for day_schedule in adjusted_schedule:
            if not day_schedule["skip_watering"]:
                schedule = WateringSchedule(
                    user_id=user_id,
                    plant_id=plant_id,
                    scheduled_date=day_schedule["date"],
                    water_needed=True,
                    volume_needed=day_schedule["adjusted_volume"],
                    weather_dependent=True,
                    next_scheduled_date=day_schedule["date"] + timedelta(days=watering_info.frequency_days)
                )
                db.add(schedule)

        db.commit()
        logger.info("Successfully created watering schedule")
        return adjusted_schedule
    except Exception as e:
        logger.error(f"Error creating watering schedule: {str(e)}")
        raise

def get_user_watering_schedule(db: Session, user_id: int):
    """Get watering schedule for a user with weather adjustments"""
    try:
        logger.info(f"Getting watering schedule for user {user_id}")
        
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            raise ValueError("User not found")
        
        # Get all user plants with their last watering date - optimized query
        user_plants = (
            db.query(UserPlant)
            .filter(UserPlant.user_id == user_id)
            .options(
                joinedload(UserPlant.plant).joinedload(Plant.watering)  # Eager load plant and watering data
            )
            .all()
        )
        logger.debug(f"Found {len(user_plants)} plants for user")
        
        if not user_plants:
            logger.info(f"No plants found for user {user_id}")
            return []  # Return empty schedule if no plants
        
        # Update weather forecasts if needed - with timeout
        if should_update_forecast(db, settings.WEATHER_LOCATION):
            logger.info("Updating weather forecasts")
            try:
                # Set a timeout for weather update
                async def update_with_timeout():
                    try:
                        async with asyncio.timeout(10):  # 10 second timeout
                            await update_weather_forecasts(db, settings.WEATHER_LOCATION)
                    except asyncio.TimeoutError:
                        logger.error("Weather forecast update timed out")
                    except Exception as e:
                        logger.error(f"Error updating weather forecasts: {str(e)}")
                
                asyncio.run(update_with_timeout())
            except Exception as e:
                logger.error(f"Error in weather update: {str(e)}")
                # Continue without weather data
        
        # Get weather forecast - with timeout
        try:
            async def get_forecast_with_timeout():
                try:
                    async with asyncio.timeout(5):  # 5 second timeout
                        return get_weather_forecast(
                            db,
                            settings.WEATHER_LOCATION,
                            datetime.now(),
                            datetime.now() + timedelta(days=7)
                        )
                except asyncio.TimeoutError:
                    logger.error("Weather forecast fetch timed out")
                    return []
                except Exception as e:
                    logger.error(f"Error getting weather forecast: {str(e)}")
                    return []
            
            weather_forecasts = asyncio.run(get_forecast_with_timeout())
            logger.debug(f"Got {len(weather_forecasts)} weather forecasts")
        except Exception as e:
            logger.error(f"Error in weather forecast: {str(e)}")
            weather_forecasts = []  # Continue without weather data

        # Get last watering dates for all plants - optimized query
        last_watering_dates = {}
        try:
            # Get all completed waterings for this user in one query
            last_waterings = (
                db.query(WateringSchedule)
                .filter(
                    WateringSchedule.user_id == user_id,
                    WateringSchedule.completed == True
                )
                .order_by(WateringSchedule.completion_timestamp.desc())
                .all()
            )
            
            # Group by plant_id and take the most recent for each
            for watering in last_waterings:
                if watering.plant_id not in last_watering_dates:
                    last_watering_dates[watering.plant_id] = watering.completion_timestamp.date()
        except Exception as e:
            logger.error(f"Error getting last watering dates: {str(e)}")

        # Generate schedule for each day
        schedule = []
        current_date = datetime.now().date()
        
        for i in range(7):
            try:
                forecast_date = current_date + timedelta(days=i)
                day_schedule = {
                    "date": forecast_date,
                    "sections": [],
                    "weather": None,
                    "weather_icons": []
                }
                
                # Get weather for this day
                day_forecasts = [f for f in weather_forecasts if f.timestamp.date() == forecast_date]
                if day_forecasts:
                    forecast = min(day_forecasts, key=lambda x: abs(x.timestamp.hour - 12))
                    day_schedule["weather"] = {
                        "temperature": forecast.temperature,
                        "precipitation": forecast.precipitation,
                        "wind_speed": forecast.wind_speed
                    }
                    
                    # Add weather icons
                    if forecast.precipitation >= 5:
                        day_schedule["weather_icons"].append("🌧")
                    if forecast.temperature >= 25:
                        day_schedule["weather_icons"].append("🌡")
                    if forecast.wind_speed >= 20:
                        day_schedule["weather_icons"].append("💨")
                
                # Group plants by section - using already loaded plant data
                sections = {}
                for user_plant in user_plants:
                    try:
                        plant = user_plant.plant  # Use the eagerly loaded plant
                        if not plant:
                            logger.warning(f"Plant {user_plant.plant_id} not found")
                            continue

                        watering_info = plant.watering  # Use the eagerly loaded watering info
                        if not watering_info:
                            logger.warning(f"No watering info found for plant {plant.id}")
                            continue

                        # Calculate base frequency (adjusted for drought tolerance)
                        base_frequency = watering_info.frequency_days
                        if watering_info.drought_tolerant:
                            base_frequency = int(base_frequency * 1.5)  # Drought tolerant plants can wait 50% longer

                        # Get last watering date
                        last_watering = last_watering_dates.get(plant.id)
                        logger.debug(f"Plant {plant.id} ({plant.common_name}):")
                        logger.debug(f"  Last watering: {last_watering}")
                        logger.debug(f"  Base frequency: {base_frequency} days")
                        
                        # Calculate days since last watering
                        if last_watering:
                            days_since_last_watering = (forecast_date - last_watering).days
                            logger.debug(f"  Days since last watering: {days_since_last_watering}")
                        else:
                            # If never watered, assume it needs watering
                            days_since_last_watering = base_frequency
                            logger.debug("  Never watered before")

                        # Create base watering requirements
                        base_watering = WateringBase(
                            plant_id=plant.id,
                            frequency_days=base_frequency,
                            depth_mm=watering_info.depth_mm,
                            volume_feet=watering_info.volume_feet,
                            period=watering_info.period,
                            drought_tolerant=watering_info.drought_tolerant,
                            soil=watering_info.soil
                        )

                        # Get weather adjustment
                        if day_forecasts:
                            adjustment = WateringAdjustment.calculate_adjustment(base_watering, forecast)
                            
                            # Skip if heavy rain is expected
                            if adjustment["skip_watering"]:
                                logger.debug("  Skipping due to heavy rain")
                                continue
                            
                            # Adjust frequency based on weather
                            adjusted_frequency = max(1, base_frequency + adjustment["frequency_adjustment"])
                            logger.debug(f"  Adjusted frequency: {adjusted_frequency} days")
                        else:
                            adjustment = {
                                "volume_adjustment": 1.0,
                                "reason": ["No weather forecast available"]
                            }
                            adjusted_frequency = base_frequency
                            logger.debug("  No weather forecast available")

                        # Check if plant needs watering on this day
                        # A plant needs watering if:
                        # 1. It has never been watered (last_watering is None)
                        # 2. The days since last watering equals the frequency (exact day)
                        # 3. The days since last watering is 1 day past the frequency (slightly overdue)
                        needs_watering = (
                            last_watering is None or
                            days_since_last_watering >= adjusted_frequency
                        )
                        
                        logger.debug(f"  Needs watering: {needs_watering}")
                        if not needs_watering:
                            logger.debug("  Skipping - not due for watering")
                            continue

                        # Calculate next watering date based on the adjusted frequency
                        next_watering_date = forecast_date + timedelta(days=adjusted_frequency)
                        logger.debug(f"  Next watering date: {next_watering_date}")
                        
                        section = user_plant.section or "Unassigned"  # Default section if none assigned
                        if section not in sections:
                            sections[section] = {
                                "high_need": [],
                                "medium_need": [],
                                "low_need": []
                            }
                        
                        # Calculate adjusted volume
                        adjusted_volume = watering_info.volume_feet * adjustment["volume_adjustment"]
                        
                        # Add plant to appropriate need level
                        plant_data = {
                            "plant_id": plant.id,
                            "plant_name": plant.common_name,
                            "watering_info": watering_info,
                            "adjusted_volume": adjusted_volume,
                            "adjustment_reason": adjustment["reason"],
                            "days_since_last_watering": days_since_last_watering,
                            "base_frequency": base_frequency,
                            "adjusted_frequency": adjusted_frequency,
                            "next_watering_date": next_watering_date.isoformat(),
                            "last_watering_date": last_watering.isoformat() if last_watering else None
                        }
                        
                        if watering_info.frequency_days <= 2:
                            sections[section]["high_need"].append(plant_data)
                        elif watering_info.frequency_days <= 4:
                            sections[section]["medium_need"].append(plant_data)
                        else:
                            sections[section]["low_need"].append(plant_data)
                    except Exception as e:
                        logger.error(f"Error processing plant {user_plant.plant_id}: {str(e)}")
                        continue
                
                # Add sections to day schedule
                for section, groups in sections.items():
                    section_schedule = {
                        "section": section,
                        "groups": []
                    }
                    
                    # Add each need level group if it has plants
                    for need_level in ["high_need", "medium_need", "low_need"]:
                        if groups[need_level]:
                            section_schedule["groups"].append({
                                "need_level": need_level.replace("_need", ""),
                                "plants": groups[need_level],
                                "total_volume": sum(p["adjusted_volume"] for p in groups[need_level])
                            })
                    
                    if section_schedule["groups"]:
                        day_schedule["sections"].append(section_schedule)
                
                schedule.append(day_schedule)
            except Exception as e:
                logger.error(f"Error processing day {i}: {str(e)}")
                continue
        
        logger.info(f"Generated schedule with {len(schedule)} days")
        return schedule
    except Exception as e:
        logger.error(f"Error in get_user_watering_schedule: {str(e)}\n{traceback.format_exc()}")
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
