"""
GreenTech - Weather Service

Provides current weather data for Madanapalli using OpenWeatherMap API.
Helps farmers make informed decisions based on local weather conditions.
"""

import requests
from typing import Optional
from utils.config import WEATHER_API_KEY, WEATHER_CITY, WEATHER_COUNTRY_CODE


def get_current_weather() -> dict:
    """
    Get current weather for Madanapalli.
    
    Returns:
        {
            "success": True,
            "temperature": 28.5,      # Celsius
            "humidity": 65,           # Percentage
            "weather": "Clear",       # Description
            "icon": "01d",           # Weather icon code
            "wind_speed": 3.2,       # m/s
            "city": "Madanapalli",
            "feels_like": 32.1       # Celsius
        }
        
        Or on error:
        {
            "success": False,
            "error": "Error message"
        }
    """
    
    if not WEATHER_API_KEY:
        return {
            "success": False,
            "error": "Weather API key not configured. Add WEATHER_API_KEY to .env file."
        }
    
    try:
        # OpenWeatherMap current weather API
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{WEATHER_CITY},{WEATHER_COUNTRY_CODE}",
            "appid": WEATHER_API_KEY,
            "units": "metric"  # Celsius
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True,
            "temperature": round(data["main"]["temp"], 1),
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["main"],
            "description": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            "wind_speed": round(data["wind"]["speed"], 1),
            "city": data["name"],
            "feels_like": round(data["main"]["feels_like"], 1),
            "pressure": data["main"]["pressure"],
            "visibility": data.get("visibility", 0) // 1000  # Convert to km
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Weather API request timed out. Please try again."
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {
                "success": False,
                "error": "Invalid weather API key. Please check configuration."
            }
        elif e.response.status_code == 404:
            return {
                "success": False,
                "error": f"City '{WEATHER_CITY}' not found in weather database."
            }
        else:
            return {
                "success": False,
                "error": f"Weather API error: {e.response.status_code}"
            }
    except requests.exceptions.RequestException:
        return {
            "success": False,
            "error": "Could not connect to weather service. Check internet connection."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Weather service error: {str(e)}"
        }


def get_weather_icon_emoji(icon_code: str) -> str:
    """Convert OpenWeatherMap icon codes to emojis."""
    icon_map = {
        "01d": "☀️",  # Clear sky day
        "01n": "🌙",  # Clear sky night
        "02d": "⛅",  # Few clouds day
        "02n": "☁️",  # Few clouds night  
        "03d": "☁️",  # Scattered clouds
        "03n": "☁️",  # Scattered clouds night
        "04d": "☁️",  # Broken clouds
        "04n": "☁️",  # Broken clouds night
        "09d": "🌧️",  # Shower rain
        "09n": "🌧️",  # Shower rain night
        "10d": "🌦️",  # Rain day
        "10n": "🌧️",  # Rain night
        "11d": "⛈️",  # Thunderstorm
        "11n": "⛈️",  # Thunderstorm night
        "13d": "🌨️",  # Snow
        "13n": "🌨️",  # Snow night
        "50d": "🌫️",  # Mist
        "50n": "🌫️",  # Mist night
    }
    return icon_map.get(icon_code, "🌤️")


def get_farming_advice_for_weather(weather_data: dict) -> str:
    """
    Provide farming advice based on current weather conditions.
    """
    if not weather_data.get("success"):
        return ""
    
    temp = weather_data["temperature"]
    humidity = weather_data["humidity"] 
    weather = weather_data["weather"].lower()
    
    advice = []
    
    # Temperature-based advice
    if temp > 35:
        advice.append("🌡️ Very hot day - ensure adequate irrigation and shade for crops")
    elif temp > 30:
        advice.append("☀️ Hot weather - monitor soil moisture levels")
    elif temp < 15:
        advice.append("❄️ Cool weather - protect sensitive crops from cold")
    
    # Humidity-based advice
    if humidity > 80:
        advice.append("💧 High humidity - watch for fungal diseases")
    elif humidity < 40:
        advice.append("🏜️ Low humidity - increase watering frequency")
    
    # Weather-based advice
    if "rain" in weather:
        advice.append("🌧️ Rainy conditions - avoid fertilizer application, check drainage")
    elif "clear" in weather or "sun" in weather:
        advice.append("☀️ Clear weather - good for harvesting and field operations")
    elif "cloud" in weather:
        advice.append("☁️ Cloudy weather - ideal for transplanting seedlings")
    elif "thunder" in weather:
        advice.append("⛈️ Thunderstorm warning - secure equipment and avoid field work")
    
    return " • ".join(advice) if advice else "🌤️ Normal weather conditions for farming"


def check_weather_status() -> dict:
    """Quick weather API connectivity check."""
    if not WEATHER_API_KEY:
        return {
            "configured": False,
            "message": "Weather API key not configured"
        }
    
    try:
        # Quick test request
        weather = get_current_weather()
        if weather["success"]:
            return {
                "configured": True,
                "message": f"Weather API connected - {weather['city']}"
            }
        else:
            return {
                "configured": False, 
                "message": f"Weather API error: {weather['error']}"
            }
    except Exception as e:
        return {
            "configured": False,
            "message": f"Weather service unavailable: {str(e)}"
        }