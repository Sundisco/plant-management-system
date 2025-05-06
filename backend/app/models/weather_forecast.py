from sqlalchemy import Column, Integer, Float, String, DateTime, UniqueConstraint
from app.database import Base

class WeatherForecast(Base):
    __tablename__ = "weather_forecast"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True))
    location = Column(String(255))
    temperature = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)

    __table_args__ = (
        UniqueConstraint('timestamp', 'location', name='unique_weather'),
    ) 