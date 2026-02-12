import requests
from typing import Dict, List, Optional

class SubdivisionAPI:
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson"
        
    def get_subdivisions(self, country_name: str) -> Optional[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/ne_10m_admin_1_states_provinces.geojson",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                country_features = []
                
                country_lower = country_name.lower()
                
                for feature in data['features']:
                    admin = feature['properties'].get('admin', '').lower()
                    if country_lower in admin or admin in country_lower:
                        country_features.append(feature)
                
                if country_features:
                    return {
                        'type': 'FeatureCollection',
                        'features': country_features
                    }
        except Exception as e:
            print(f"Subdivision API error: {e}")
        
        return None
