from datetime import datetime, timedelta
from typing import Dict, List
from app.schemas.watering import WateringBase
from app.schemas.weather_forecast import WeatherForecast
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WateringAdjustment:
    # Temperature thresholds (in Celsius)
    TEMP_HIGH = 25
    TEMP_VERY_HIGH = 30
    
    # Wind speed thresholds (in km/h)
    WIND_HIGH = 20
    WIND_VERY_HIGH = 30
    
    # Precipitation thresholds (in mm)
    RAIN_LIGHT = 2
    RAIN_MODERATE = 5
    RAIN_HEAVY = 10

    @staticmethod
    def calculate_adjustment(
        base_watering: WateringBase,
        weather: WeatherForecast
    ) -> Dict:
        """
        Calculate watering adjustments based on weather conditions
        Returns a dict with adjusted values and recommendations
        """
        try:
            logger.debug(f"Calculating adjustment for plant {base_watering.plant_id} with weather: {weather.__dict__}")
            
            adjustment = {
                "skip_watering": False,
                "frequency_adjustment": 0,  # Days to add/subtract
                "volume_adjustment": 1.0,   # Multiplier for volume
                "reason": []
            }

            # Check precipitation
            if weather.precipitation >= WateringAdjustment.RAIN_HEAVY:
                adjustment["skip_watering"] = True
                adjustment["reason"].append("Heavy rain expected")
            elif weather.precipitation >= WateringAdjustment.RAIN_MODERATE:
                adjustment["volume_adjustment"] *= 0.5
                adjustment["reason"].append("Moderate rain expected")
            elif weather.precipitation >= WateringAdjustment.RAIN_LIGHT:
                adjustment["volume_adjustment"] *= 0.75
                adjustment["reason"].append("Light rain expected")

            # Check temperature
            if weather.temperature >= WateringAdjustment.TEMP_VERY_HIGH:
                adjustment["frequency_adjustment"] -= 1
                adjustment["volume_adjustment"] *= 1.5
                adjustment["reason"].append("Very high temperature")
            elif weather.temperature >= WateringAdjustment.TEMP_HIGH:
                adjustment["frequency_adjustment"] -= 0.5
                adjustment["volume_adjustment"] *= 1.25
                adjustment["reason"].append("High temperature")

            # Check wind
            if weather.wind_speed >= WateringAdjustment.WIND_VERY_HIGH:
                adjustment["frequency_adjustment"] -= 1
                adjustment["volume_adjustment"] *= 1.5
                adjustment["reason"].append("Very high winds")
            elif weather.wind_speed >= WateringAdjustment.WIND_HIGH:
                adjustment["frequency_adjustment"] -= 0.5
                adjustment["volume_adjustment"] *= 1.25
                adjustment["reason"].append("High winds")

            # Adjust for drought tolerance
            if base_watering.drought_tolerant:
                adjustment["frequency_adjustment"] += 1
                adjustment["volume_adjustment"] *= 0.75
                adjustment["reason"].append("Drought tolerant plant")

            logger.debug(f"Calculated adjustment: {adjustment}")
            return adjustment
        except Exception as e:
            logger.error(f"Error calculating adjustment: {str(e)}\n{traceback.format_exc()}")
            raise

    @staticmethod
    def get_adjusted_schedule(
        base_watering: WateringBase,
        weather_forecasts: List[WeatherForecast]
    ) -> List[Dict]:
        """
        Generate a week's worth of adjusted watering schedule
        """
        try:
            logger.debug(f"Generating adjusted schedule for plant {base_watering.plant_id}")
            schedule = []
            current_date = datetime.now().date()
            
            # Group forecasts by date
            forecasts_by_date = {}
            for forecast in weather_forecasts:
                date_key = forecast.timestamp.date()
                if date_key not in forecasts_by_date:
                    forecasts_by_date[date_key] = []
                forecasts_by_date[date_key].append(forecast)
            
            for i in range(7):
                forecast_date = current_date + timedelta(days=i)
                # Get all forecasts for this date
                day_forecasts = forecasts_by_date.get(forecast_date, [])
                
                if day_forecasts:
                    # Use the forecast closest to noon
                    forecast = min(day_forecasts, 
                                 key=lambda x: abs(x.timestamp.hour - 12))
                    
                    logger.debug(f"Using forecast for {forecast_date} at {forecast.timestamp}")
                    try:
                        adjustment = WateringAdjustment.calculate_adjustment(
                            base_watering,
                            forecast
                        )
                        
                        # Calculate adjusted volume based on the adjustment factors
                        adjusted_volume = base_watering.volume_feet * adjustment["volume_adjustment"]
                        
                        schedule.append({
                            "date": forecast_date,
                            "skip_watering": adjustment["skip_watering"],
                            "adjusted_volume": adjusted_volume,
                            "reason": adjustment["reason"],
                            "original_volume": base_watering.volume_feet,
                            "weather_forecast": {
                                "temperature": forecast.temperature,
                                "precipitation": forecast.precipitation,
                                "wind_speed": forecast.wind_speed
                            }
                        })
                        
                        logger.debug(f"Added schedule entry for {forecast_date}: {schedule[-1]}")
                    except Exception as e:
                        logger.error(f"Error calculating adjustment for {forecast_date}: {str(e)}")
                        continue
                else:
                    logger.warning(f"No forecast found for date {forecast_date}")
                    # Use default values when no forecast is available
                    schedule.append({
                        "date": forecast_date,
                        "skip_watering": False,
                        "adjusted_volume": base_watering.volume_feet,
                        "reason": ["No weather forecast available"],
                        "original_volume": base_watering.volume_feet,
                        "weather_forecast": None
                    })
            
            return schedule
        except Exception as e:
            logger.error(f"Error generating adjusted schedule: {str(e)}")
            raise 