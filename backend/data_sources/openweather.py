import requests
from typing import Dict, Optional

class OpenWeatherAPI:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        
    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/forecast",
                params={
                    'latitude': lat,
                    'longitude': lon,
                    'current': 'temperature_2m,precipitation,wind_speed_10m',
                    'timezone': 'auto'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current', {})
                
                return {
                    'temperature': current.get('temperature_2m'),
                    'precipitation': current.get('precipitation'),
                    'wind_speed': current.get('wind_speed_10m'),
                    'time': current.get('time'),
                    'source': 'Open-Meteo'
                }
        except Exception as e:
            print(f"OpenWeather error: {e}")
        
        return None
