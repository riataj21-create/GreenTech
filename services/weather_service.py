"""
GreenTech - Weather Service
Fetches current weather from OpenWeatherMap.
City can be overridden by the user at runtime.
"""

import requests
from utils.config import WEATHER_API_KEY, WEATHER_CITY, WEATHER_COUNTRY_CODE


def get_current_weather(city: str = None) -> dict:
    """
    Get current weather.
    city -- user-supplied city name; falls back to WEATHER_CITY from .env
    """
    if not WEATHER_API_KEY:
        return {"success": False, "error": "Weather API key not configured."}

    target_city = (city.strip() if city and city.strip() else WEATHER_CITY)

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{target_city},{WEATHER_COUNTRY_CODE}",
            "appid": WEATHER_API_KEY,
            "units": "metric",
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
            "visibility": data.get("visibility", 0) // 1000,
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Weather request timed out."}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {"success": False, "error": "Invalid weather API key."}
        elif e.response.status_code == 404:
            return {"success": False, "error": f"City '{target_city}' not found. Check spelling."}
        else:
            return {"success": False, "error": f"Weather API error {e.response.status_code}."}
    except requests.exceptions.RequestException:
        return {"success": False, "error": "Could not connect to weather service."}
    except Exception as e:
        return {"success": False, "error": f"Weather error: {str(e)}"}


def get_weather_icon_emoji(icon_code: str) -> str:
    icon_map = {
        "01d": "☀️", "01n": "🌙",
        "02d": "⛅", "02n": "☁️",
        "03d": "☁️", "03n": "☁️",
        "04d": "☁️", "04n": "☁️",
        "09d": "🌧️", "09n": "🌧️",
        "10d": "🌦️", "10n": "🌧️",
        "11d": "⛈️", "11n": "⛈️",
        "13d": "🌨️", "13n": "🌨️",
        "50d": "🌫️", "50n": "🌫️",
    }
    return icon_map.get(icon_code, "🌤️")


def get_farming_advice_for_weather(weather_data: dict) -> str:
    if not weather_data.get("success"):
        return ""

    temp    = weather_data["temperature"]
    humidity = weather_data["humidity"]
    weather  = weather_data["weather"].lower()

    advice = []

    if temp > 35:
        advice.append("🌡️ Very hot — ensure irrigation and shade for crops")
    elif temp > 30:
        advice.append("☀️ Hot weather — monitor soil moisture levels")
    elif temp < 15:
        advice.append("❄️ Cool weather — protect sensitive crops from cold")

    if humidity > 80:
        advice.append("💧 High humidity — watch for fungal diseases")
    elif humidity < 40:
        advice.append("🏜️ Low humidity — increase watering frequency")

    if "rain" in weather:
        advice.append("🌧️ Rainy — avoid fertilizer, check drainage")
    elif "clear" in weather or "sun" in weather:
        advice.append("☀️ Clear sky — good for harvesting and field work")
    elif "cloud" in weather:
        advice.append("☁️ Cloudy — ideal for transplanting seedlings")
    elif "thunder" in weather:
        advice.append("⛈️ Thunderstorm — secure equipment, avoid field work")

    return "  •  ".join(advice) if advice else "🌤️ Normal conditions for farming"


def check_weather_status() -> dict:
    if not WEATHER_API_KEY:
        return {"configured": False, "message": "Weather API key not configured"}
    try:
        w = get_current_weather()
        if w["success"]:
            return {"configured": True, "message": f"Connected — {w['city']}"}
        return {"configured": False, "message": w["error"]}
    except Exception as e:
        return {"configured": False, "message": str(e)}
