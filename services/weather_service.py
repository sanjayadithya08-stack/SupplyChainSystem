from dataclasses import dataclass
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config

@dataclass
class WeatherReport:
    region: str
    condition: str
    severity: str
    wind_kph: float
    visibility_km: float
    alerts: list[str]

_WEATHER_DATA = {
    "us-west-coast": WeatherReport("us-west-coast", "Wildfires", "HIGH", 45.0, 1.0, ["Air quality warning", "Highway closures"]),
    "us-east-coast": WeatherReport("us-east-coast", "Hurricane", "CRITICAL", 180.0, 0.5, ["Evacuation order", "Port closed"]),
    "southeast-asia": WeatherReport("southeast-asia", "Typhoon", "CRITICAL", 120.0, 1.5, ["Flooding expected"]),
    "europe": WeatherReport("europe", "Heavy Rain", "MEDIUM", 45.0, 5.0, ["Minor flooding"]),
    "middle-east": WeatherReport("middle-east", "Sandstorm", "HIGH", 85.0, 0.5, ["Flights delayed"]),
    "east-asia": WeatherReport("east-asia", "Cloudy", "LOW", 20.0, 8.0, []),
    "global": WeatherReport("global", "Mixed", "MEDIUM", 30.0, 6.0, [])
}

def fetch_weather(region: str) -> WeatherReport:
    """
    # TO SWAP FOR REAL API (e.g. OpenWeatherMap):
    # import requests
    # API_KEY = os.getenv("WEATHER_API_KEY")
    # url = f"https://api.openweathermap.org/data/2.5/weather?q={region}&appid={API_KEY}"
    # response = requests.get(url)
    """
    try:
        return _WEATHER_DATA.get(region, WeatherReport(region, "Clear", "LOW", 10.0, 10.0, []))
    except Exception:
        return WeatherReport(region, "Unknown", "UNKNOWN", 0.0, 0.0, [])

def get_severe_regions() -> list[str]:
    try:
        return [region for region, report in _WEATHER_DATA.items() if report.severity in ["HIGH", "CRITICAL"]]
    except Exception:
        return []