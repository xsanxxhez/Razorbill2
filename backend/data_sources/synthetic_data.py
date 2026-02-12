import random

class SyntheticDataGenerator:
    def __init__(self):
        self.country_estimates = {
            'Brazil': {'population': 215313498, 'density': 25.4, 'area': 8515767},
            'China': {'population': 1439323776, 'density': 153, 'area': 9388211},
            'India': {'population': 1380004385, 'density': 464, 'area': 2973190},
            'USA': {'population': 331002651, 'density': 36, 'area': 9147420},
            'Russia': {'population': 145934462, 'density': 8.8, 'area': 16376870},
            'Japan': {'population': 126476461, 'density': 347, 'area': 364555},
            'Germany': {'population': 83783942, 'density': 240, 'area': 348560},
            'UK': {'population': 67886011, 'density': 281, 'area': 241930},
            'France': {'population': 65273511, 'density': 119, 'area': 547557},
            'Italy': {'population': 60461826, 'density': 206, 'area': 294140},
            'Spain': {'population': 46754778, 'density': 94, 'area': 498800},
            'Canada': {'population': 37742154, 'density': 4.2, 'area': 9093510},
            'Australia': {'population': 25499884, 'density': 3.3, 'area': 7682300},
            'Mexico': {'population': 128932753, 'density': 66, 'area': 1943950},
            'South Korea': {'population': 51269185, 'density': 527, 'area': 97230}
        }
    
    def get_country_data(self, location_name: str) -> dict:
        for country, data in self.country_estimates.items():
            if country.lower() in location_name.lower():
                variance = random.uniform(0.98, 1.02)
                return {
                    'country': country,
                    'population': int(data['population'] * variance),
                    'density': data['density'] * variance,
                    'area': data['area'],
                    'year': '2024',
                    'source': 'Estimated Data'
                }
        
        return {
            'country': location_name,
            'population': 50000000,
            'density': 100,
            'area': 500000,
            'year': '2024',
            'source': 'Estimated Data'
        }
