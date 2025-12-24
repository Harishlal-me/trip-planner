"""
Weather endpoints - api/routes/weather.py
Uses free Open-Meteo API (no API key required)
"""

from fastapi import APIRouter, HTTPException
import logging
import aiohttp
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/current")
async def get_current_weather(city: str, country_code: str = None):
    """Get current weather for a city"""
    try:
        # Geocoding to get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(geo_url) as resp:
                geo_data = await resp.json()
        
        if not geo_data.get('results'):
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
        
        location = geo_data['results'][0]
        lat, lon = location['latitude'], location['longitude']
        
        # Get weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m&timezone=auto"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(weather_url) as resp:
                weather_data = await resp.json()
        
        current = weather_data.get('current', {})
        
        # Weather code to description mapping
        weather_descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Light snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Thunderstorm with hail"
        }
        
        weather_code = current.get('weather_code', 0)
        weather_desc = weather_descriptions.get(weather_code, "Unknown")
        
        return {
            "city": city,
            "country": location.get('country'),
            "latitude": lat,
            "longitude": lon,
            "temperature": current.get('temperature_2m'),
            "unit": "°C",
            "weather": weather_desc,
            "weather_code": weather_code,
            "wind_speed": current.get('wind_speed_10m'),
            "humidity": current.get('relative_humidity_2m'),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Weather error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
async def get_weather_forecast(city: str, days: int = 5):
    """Get weather forecast for a city"""
    try:
        if days > 7:
            days = 7
        if days < 1:
            days = 1
        
        # Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(geo_url) as resp:
                geo_data = await resp.json()
        
        if not geo_data.get('results'):
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
        
        location = geo_data['results'][0]
        lat, lon = location['latitude'], location['longitude']
        
        # Get forecast
        forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum&timezone=auto&forecast_days={days}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(forecast_url) as resp:
                forecast_data = await resp.json()
        
        daily = forecast_data.get('daily', {})
        forecast = []
        
        weather_descriptions = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Foggy", 51: "Light drizzle", 53: "Moderate drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain"
        }
        
        for i in range(min(days, len(daily.get('time', [])))):
            weather_code = daily['weather_code'][i]
            forecast.append({
                "date": daily['time'][i],
                "temp_max": daily['temperature_2m_max'][i],
                "temp_min": daily['temperature_2m_min'][i],
                "weather": weather_descriptions.get(weather_code, "Unknown"),
                "precipitation_mm": daily['precipitation_sum'][i]
            })
        
        return {
            "city": city,
            "country": location.get('country'),
            "forecast_days": days,
            "forecast": forecast,
            "unit": "°C"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))