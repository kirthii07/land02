import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or "92aaf33258cf7d088b4e1789e04ff782"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude, longitude):
    """
    Fetch current real-time weather using OpenWeather API with graceful fallbacks.
    Does not crash if network or key is unavailable.
    """
    # 1. Primary: OpenWeather API
    if OPENWEATHER_API_KEY:
        try:
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            }
            response = requests.get(OPENWEATHER_URL, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                main = data.get("main", {})
                wind = data.get("wind", {})
                rain = data.get("rain", {})
                weather_list = data.get("weather", [{}])

                rain_1h = rain.get("1h", rain.get("3h", 0))

                return {
                    "success": True,
                    "source": "OpenWeather",
                    "city": data.get("name", ""),
                    "temperature": main.get("temp"),
                    "humidity": main.get("humidity"),
                    "pressure": main.get("pressure"),
                    "wind_speed": wind.get("speed"),
                    "precipitation": rain_1h,
                    "rain": rain_1h,
                    "description": weather_list[0].get("description", "Clear") if weather_list else "Clear"
                }
        except Exception:
            pass

    # 2. Secondary: Open-Meteo (optional fallback, non-blocking)
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m",
            "forecast_days": 1,
            "timezone": "auto"
        }
        response = requests.get(OPEN_METEO_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            return {
                "success": True,
                "source": "Open-Meteo",
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "precipitation": current.get("precipitation"),
                "rain": current.get("rain"),
                "wind_speed": current.get("wind_speed_10m"),
                "description": "Monitored Conditions"
            }
    except Exception:
        pass

    # 3. Graceful fallback when no internet/APIs are reachable
    return {
        "success": False,
        "source": "Unavailable",
        "message": "Weather telemetry temporarily offline",
        "temperature": None,
        "humidity": None,
        "precipitation": None,
        "rain": None,
        "wind_speed": None,
        "description": "Offline"
    }
