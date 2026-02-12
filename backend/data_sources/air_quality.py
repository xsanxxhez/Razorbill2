import requests
from typing import Dict, Optional

class AirQualityAPI:
    def __init__(self):
        self.base_url = "https://api.openaq.org/v2"
        
    def get_air_quality(self, lat: float, lon: float, radius_km: int = 100) -> Optional[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/latest",
                params={
                    'limit': 50,
                    'coordinates': f"{lat},{lon}",
                    'radius': radius_km * 1000,
                    'parameter': 'pm25'
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data['results']:
                    stations = []
                    for result in data['results']:
                        for measurement in result.get('measurements', []):
                            if measurement['parameter'] == 'pm25':
                                stations.append({
                                    'lat': result['coordinates']['latitude'],
                                    'lon': result['coordinates']['longitude'],
                                    'pm25': measurement['value'],
                                    'location': result.get('location', 'Unknown'),
                                    'city': result.get('city', 'Unknown'),
                                    'updated': measurement.get('lastUpdated', '')
                                })
                    
                    return {'stations': stations}
        except Exception as e:
            print(f"Air Quality API error: {e}")
        
        return None
