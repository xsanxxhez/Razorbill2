import requests
from typing import Dict, List, Optional

class NaturalEarthAPI:
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson"
        
    def get_country_borders(self, country_name: str) -> Optional[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/ne_110m_admin_0_countries.geojson",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for feature in data['features']:
                    name = feature['properties'].get('NAME', '').lower()
                    if country_name.lower() in name:
                        return {
                            'type': 'FeatureCollection',
                            'features': [feature]
                        }
        except Exception as e:
            print(f"Natural Earth error: {e}")
        
        return None
