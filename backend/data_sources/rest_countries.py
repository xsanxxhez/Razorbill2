import requests
from typing import Dict, Optional

class RestCountriesAPI:
    def __init__(self):
        self.base_url = "https://restcountries.com/v3.1"
        
    def get_country_data(self, location_name: str) -> Optional[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/name/{location_name}",
                params={'fields': 'name,population,area,capital,latlng'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    country = data[0]
                    population = country.get('population', 0)
                    area = country.get('area', 1)
                    density = population / area if area > 0 else 0
                    
                    print(f"✅ REST Countries: {country['name']['common']} - Pop: {population:,.0f}")
                    
                    return {
                        'country': country['name']['common'],
                        'population': population,
                        'density': density,
                        'area': area,
                        'capital': country.get('capital', ['Unknown'])[0],
                        'latlng': country.get('latlng', [0, 0]),
                        'year': '2024',
                        'source': 'REST Countries'
                    }
        except Exception as e:
            print(f"REST Countries error: {e}")
        
        return None
