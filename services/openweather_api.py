"""
OpenWeatherMap API Service - FIXED VERSION
FREE weather data (requires API key - 1000 calls/day free)
"""

import os
import requests
import logging
from datetime import datetime, timedelta

# ✅ FIX: import typing helpers
from typing import Optional, Dict, List

# ✅ Load environment variables
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError(
        "OPENWEATHER_API_KEY not loaded. "
        "Check your .env file and ensure it contains:\n"
        "OPENWEATHER_API_KEY=your_api_key_here"
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class OpenWeatherAPI:
    """
    Interface for OpenWeatherMap API
    Provides current weather, forecasts, and historical data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenWeatherMap API client
        
        Args:
            api_key: API key (or set OPENWEATHER_API_KEY in .env)
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "OpenWeather API key required. Get free key at: "
                "https://openweathermap.org/api\n"
                "Then create .env file with: OPENWEATHER_API_KEY=your_key_here"
            )
            
        # FIXED: Use correct free tier endpoint
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        logger.info(f"OpenWeather API initialized with key: {self.api_key[:8]}...")
        
    def get_current_weather(self, city: str, country_code: Optional[str] = None) -> Optional[Dict]:
        """
        Get current weather for a city
        
        Args:
            city: City name
            country_code: Optional 2-letter country code (e.g., 'US', 'FR')
            
        Returns:
            Dictionary with current weather data
        """
        # Build location string
        location = city
        if country_code:
            location = f"{city},{country_code}"
            
        params = {
            'q': location,
            'appid': self.api_key,
            'units': 'metric'  # Use Celsius
        }
        
        # FIXED: Use correct endpoint
        url = f"{self.base_url}/weather"
        
        try:
            logger.info(f"Requesting weather for: {location}")
            response = requests.get(
                url,
                params=params,
                timeout=10
            )
            
            # Log status for debugging
            logger.info(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'temp_min': data['main']['temp_min'],
                'temp_max': data['main']['temp_max'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'weather': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg'),
                'clouds': data['clouds']['all'],
                'visibility': data.get('visibility'),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']),
                'timestamp': datetime.fromtimestamp(data['dt']),
                'coordinates': {
                    'latitude': data['coord']['lat'],
                    'longitude': data['coord']['lon']
                }
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("❌ API key invalid or not activated yet. Wait 10-15 minutes after creating new key.")
            elif e.response.status_code == 404:
                logger.error(f"❌ City not found: {location}")
            else:
                logger.error(f"❌ HTTP error: {e}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching weather for {location}: {str(e)}")
            return None
            
    def get_forecast(self, city: str, country_code: Optional[str] = None, 
                    days: int = 5) -> Optional[List[Dict]]:
        """
        Get weather forecast for a city (up to 5 days)
        
        Args:
            city: City name
            country_code: Optional 2-letter country code
            days: Number of days to forecast (1-5)
            
        Returns:
            List of forecast data dictionaries
        """
        location = city
        if country_code:
            location = f"{city},{country_code}"
            
        params = {
            'q': location,
            'appid': self.api_key,
            'units': 'metric',
            'cnt': min(days * 8, 40)  # API returns 3-hour intervals
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/forecast",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            forecasts = []
            for item in data['list']:
                forecasts.append({
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'temp_min': item['main']['temp_min'],
                    'temp_max': item['main']['temp_max'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'weather': item['weather'][0]['main'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'wind_speed': item['wind']['speed'],
                    'clouds': item['clouds']['all'],
                    'rain_3h': item.get('rain', {}).get('3h', 0),
                    'snow_3h': item.get('snow', {}).get('3h', 0),
                    'pop': item.get('pop', 0)  # Probability of precipitation
                })
                
            logger.info(f"Retrieved {len(forecasts)} forecast periods for {location}")
            return forecasts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching forecast for {location}: {str(e)}")
            return None
            
    def get_daily_forecast_summary(self, city: str, country_code: Optional[str] = None,
                                  days: int = 5) -> Optional[List[Dict]]:
        """
        Get simplified daily forecast summary
        
        Args:
            city: City name
            country_code: Optional 2-letter country code
            days: Number of days (1-5)
            
        Returns:
            List of daily summaries
        """
        forecasts = self.get_forecast(city, country_code, days)
        
        if not forecasts:
            return None
            
        # Group by date
        daily_data = {}
        for forecast in forecasts:
            date = forecast['datetime'].date()
            
            if date not in daily_data:
                daily_data[date] = {
                    'temps': [],
                    'humidity': [],
                    'weather': [],
                    'rain': [],
                    'wind': []
                }
                
            daily_data[date]['temps'].append(forecast['temperature'])
            daily_data[date]['humidity'].append(forecast['humidity'])
            daily_data[date]['weather'].append(forecast['weather'])
            daily_data[date]['rain'].append(forecast['rain_3h'])
            daily_data[date]['wind'].append(forecast['wind_speed'])
            
        # Create summaries
        summaries = []
        for date, data in sorted(daily_data.items())[:days]:
            # Most common weather condition
            weather = max(set(data['weather']), key=data['weather'].count)
            
            summaries.append({
                'date': date,
                'temp_min': min(data['temps']),
                'temp_max': max(data['temps']),
                'temp_avg': sum(data['temps']) / len(data['temps']),
                'humidity_avg': sum(data['humidity']) / len(data['humidity']),
                'weather': weather,
                'total_rain': sum(data['rain']),
                'wind_avg': sum(data['wind']) / len(data['wind'])
            })
            
        return summaries
        
    def get_weather_by_coordinates(self, latitude: float, 
                                   longitude: float) -> Optional[Dict]:
        """
        Get current weather by geographic coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with weather data
        """
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/weather",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'location': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'weather': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'coordinates': {
                    'latitude': data['coord']['lat'],
                    'longitude': data['coord']['lon']
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather for ({latitude}, {longitude}): {str(e)}")
            return None
            
    def is_good_weather_for_travel(self, city: str, 
                                   country_code: Optional[str] = None) -> Dict:
        """
        Determine if weather is suitable for travel
        
        Args:
            city: City name
            country_code: Optional country code
            
        Returns:
            Dictionary with suitability assessment
        """
        weather = self.get_current_weather(city, country_code)
        
        if not weather:
            return {
                'suitable': None,
                'reason': 'Unable to fetch weather data'
            }
            
        temp = weather['temperature']
        condition = weather['weather'].lower()
        wind = weather['wind_speed']
        
        # Simple heuristics
        issues = []
        
        if temp < 0:
            issues.append('Very cold temperature')
        elif temp > 35:
            issues.append('Very hot temperature')
            
        if condition in ['thunderstorm', 'tornado', 'hurricane']:
            issues.append('Severe weather conditions')
        elif condition in ['rain', 'drizzle', 'snow']:
            issues.append('Precipitation expected')
            
        if wind > 15:
            issues.append('Strong winds')
            
        suitable = len(issues) == 0
        
        return {
            'suitable': suitable,
            'temperature': temp,
            'condition': weather['description'],
            'issues': issues if issues else ['Clear conditions'],
            'recommendation': 'Good for travel' if suitable else 'Consider weather conditions'
        }


if __name__ == "__main__":
    # Test the API
    print("=" * 60)
    print("Testing OpenWeather API - FIXED VERSION")
    print("=" * 60)
    
    try:
        api = OpenWeatherAPI()
        
        # Test 1: Current weather
        print("\n1. Getting current weather for Paris...")
        weather = api.get_current_weather("Paris", "FR")
        if weather:
            print(f"   ✅ Temperature: {weather['temperature']}°C")
            print(f"   Condition: {weather['description']}")
            print(f"   Humidity: {weather['humidity']}%")
        else:
            print("   ❌ Failed to get weather")
        
        # Test 2: Forecast
        print("\n2. Getting 3-day forecast for London...")
        forecast = api.get_daily_forecast_summary("London", "GB", days=3)
        if forecast:
            print(f"   ✅ Retrieved {len(forecast)} days")
            for day in forecast:
                print(f"   {day['date']}: {day['temp_min']:.1f}°C - {day['temp_max']:.1f}°C")
        else:
            print("   ❌ Failed to get forecast")
        
        # Test 3: Travel suitability
        print("\n3. Checking travel suitability for Tokyo...")
        suitability = api.is_good_weather_for_travel("Tokyo", "JP")
        print(f"   ✅ Suitable: {suitability['suitable']}")
        print(f"   Recommendation: {suitability['recommendation']}")
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 TO FIX:")
        print("1. Get free API key: https://openweathermap.org/api")
        print("2. Create .env file in project root:")
        print("   OPENWEATHER_API_KEY=your_key_here")
        print("3. Wait 10-15 minutes after creating key")
        print("4. Run: pip install python-dotenv")