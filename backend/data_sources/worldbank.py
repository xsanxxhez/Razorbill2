import requests
from typing import Dict, Optional
import time

class WorldBankAPI:
    def __init__(self):
        self.base_url = "https://api.worldbank.org/v2"
        
    def get_population_data(self, country_code: str) -> Optional[Dict]:
        try:
            url = f"{self.base_url}/country/{country_code}/indicator/SP.POP.TOTL"
            response = requests.get(url, params={
                'format': 'json',
                'date': 'MRV:1',
                'per_page': 1
            }, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1] and len(data[1]) > 0:
                    item = data[1][0]
                    if item.get('value'):
                        print(f"✅ WB Population: {item['value']:,.0f} ({item['date']})")
                        return {
                            'population': item['value'],
                            'year': item['date'],
                            'country': item['country']['value']
                        }
            
            print(f"⚠️ WB: No population data for {country_code}")
        except Exception as e:
            print(f"❌ WB error: {e}")
        
        return None
    
    def get_population_density(self, country_code: str) -> Optional[Dict]:
        try:
            url = f"{self.base_url}/country/{country_code}/indicator/EN.POP.DNST"
            response = requests.get(url, params={
                'format': 'json',
                'date': 'MRV:1',
                'per_page': 1
            }, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1] and len(data[1]) > 0:
                    item = data[1][0]
                    if item.get('value'):
                        print(f"✅ WB Density: {item['value']:.1f} ({item['date']})")
                        return {
                            'density': item['value'],
                            'year': item['date'],
                            'country': item['country']['value']
                        }
            
            print(f"⚠️ WB: No density data for {country_code}")
        except Exception as e:
            print(f"❌ WB density error: {e}")
        
        return None
    
    def search_country(self, location_name: str) -> Optional[str]:
        city_to_country = {
            'tokyo': 'JPN', 'osaka': 'JPN', 'kyoto': 'JPN',
            'new york': 'USA', 'los angeles': 'USA', 'chicago': 'USA',
            'london': 'GBR', 'manchester': 'GBR',
            'paris': 'FRA', 'marseille': 'FRA',
            'berlin': 'DEU', 'munich': 'DEU',
            'moscow': 'RUS', 'москва': 'RUS',
            'beijing': 'CHN', 'shanghai': 'CHN',
            'delhi': 'IND', 'mumbai': 'IND',
            'sydney': 'AUS', 'melbourne': 'AUS',
            'toronto': 'CAN', 'vancouver': 'CAN',
            'sao paulo': 'BRA', 'rio': 'BRA'
        }
        
        country_map = {
            'russia': 'RUS', 'russian': 'RUS',
            'usa': 'USA', 'united states': 'USA', 'america': 'USA',
            'brazil': 'BRA', 'бразилия': 'BRA', 'brasil': 'BRA',
            'china': 'CHN', 'китай': 'CHN',
            'india': 'IND', 'индия': 'IND',
            'japan': 'JPN', 'japanese': 'JPN',
            'germany': 'DEU', 'german': 'DEU',
            'uk': 'GBR', 'britain': 'GBR', 'united kingdom': 'GBR',
            'france': 'FRA', 'french': 'FRA',
            'canada': 'CAN', 'canadian': 'CAN',
            'australia': 'AUS', 'australian': 'AUS',
            'mexico': 'MEX', 'mexican': 'MEX',
            'italy': 'ITA', 'italian': 'ITA',
            'spain': 'ESP', 'spanish': 'ESP',
            'south korea': 'KOR', 'korea': 'KOR'
        }
        
        location_lower = location_name.lower()
        
        for city, code in city_to_country.items():
            if city in location_lower:
                print(f"🌍 Mapped {location_name} -> {code}")
                return code
        
        for country, code in country_map.items():
            if country in location_lower:
                print(f"🌍 Mapped {location_name} -> {code}")
                return code
        
        print(f"⚠️ No country code for: {location_name}")
        return None
