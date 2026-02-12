import requests
from typing import Dict, Optional

class NASAAPI:
    def __init__(self):
        self.base_url = "https://power.larc.nasa.gov/api/temporal"
        
    def get_temperature_data(self, lat: float, lon: float) -> Optional[Dict]:
        try:
            url = f"{self.base_url}/monthly/point"
            params = {
                'parameters': 'T2M',
                'community': 'AG',
                'longitude': lon,
                'latitude': lat,
                'start': '2023',
                'end': '2023',
                'format': 'JSON'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'properties' in data and 'parameter' in data['properties']:
                    temps = data['properties']['parameter']['T2M']
                    avg_temp = sum(temps.values()) / len(temps)
                    
                    return {
                        'temperature': round(avg_temp, 1),
                        'unit': '°C',
                        'year': '2023',
                        'source': 'NASA POWER'
                    }
        except Exception as e:
            print(f"NASA API error: {e}")
        
        return None
