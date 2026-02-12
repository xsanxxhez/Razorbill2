import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class USGSAPI:
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        
    def get_earthquakes(self, lat: float, lon: float, radius_km: int = 1000, days: int = 30) -> Optional[Dict]:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        try:
            response = requests.get(
                self.base_url,
                params={
                    'format': 'geojson',
                    'starttime': start_time.strftime('%Y-%m-%d'),
                    'endtime': end_time.strftime('%Y-%m-%d'),
                    'latitude': lat,
                    'longitude': lon,
                    'maxradiuskm': radius_km,
                    'minmagnitude': 2.5,
                    'orderby': 'magnitude'
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for feature in data['features']:
                    props = feature['properties']
                    props['magnitude'] = props.get('mag', 0)
                    props['location'] = props.get('place', 'Unknown')
                    props['time_readable'] = datetime.fromtimestamp(props['time']/1000).strftime('%Y-%m-%d %H:%M')
                
                return data
                
        except Exception as e:
            print(f"USGS error: {e}")
        
        return None
