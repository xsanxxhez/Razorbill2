import requests
from math import cos, radians

class OpenMeteoDataSource:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def fetch(self, location):
        try:
            print(f"🌤️ Fetching weather for: {location}")

            # Geocode location first
            geocode_response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={'name': location, 'count': 1},
                timeout=10
            )

            if geocode_response.status_code != 200:
                return {'metadata': {'error': True, 'summary': 'Location not found'}}

            geo_data = geocode_response.json()
            if not geo_data.get('results'):
                return {'metadata': {'error': True, 'summary': f'❌ Location "{location}" not found'}}

            place = geo_data['results'][0]
            lat, lon = place['latitude'], place['longitude']

            # Fetch weather
            weather_response = requests.get(
                self.base_url,
                params={
                    'latitude': lat,
                    'longitude': lon,
                    'current_weather': 'true',
                    'timezone': 'auto'
                },
                timeout=10
            )

            if weather_response.status_code == 200:
                weather_data = weather_response.json()
                current = weather_data.get('current_weather', {})

                temp = current.get('temperature', 0)
                wind_speed = current.get('windspeed', 0)

                # Create GRID of rectangles around the location
                features = self._create_weather_grid(lat, lon, temp, wind_speed)

                return {
                    'type': 'FeatureCollection',
                    'features': features,
                    'metadata': {
                        'source': 'Open-Meteo',
                        'layer_type': 'weather',
                        'feature_count': len(features),
                        'summary': f"🌡️ {place['name']}: {temp}°C, Wind: {wind_speed} km/h",
                        'center': {'latitude': lat, 'longitude': lon}
                    }
                }

            return {'metadata': {'error': True, 'summary': 'Weather data unavailable'}}

        except Exception as e:
            print(f"❌ Weather fetch error: {e}")
            return {'metadata': {'error': True, 'summary': f'❌ Error: {str(e)}'}}

    def _create_weather_grid(self, center_lat, center_lon, temp, wind_speed):
        """Create a grid of hexagons or rectangles showing weather"""
        features = []

        # Grid parameters
        grid_size = 5  # 5x5 grid
        cell_size = 0.5  # degrees

        for i in range(-grid_size//2, grid_size//2 + 1):
            for j in range(-grid_size//2, grid_size//2 + 1):
                lat = center_lat + i * cell_size
                lon = center_lon + j * cell_size

                # Add temperature variation for visual effect
                temp_variation = (i * 0.5) + (j * 0.3)
                cell_temp = temp + temp_variation

                # Create rectangle polygon
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [[
                            [lon - cell_size/2, lat - cell_size/2],
                            [lon + cell_size/2, lat - cell_size/2],
                            [lon + cell_size/2, lat + cell_size/2],
                            [lon - cell_size/2, lat + cell_size/2],
                            [lon - cell_size/2, lat - cell_size/2]
                        ]]
                    },
                    'properties': {
                        'temperature': round(cell_temp, 1),
                        'wind_speed': wind_speed,
                        'type': 'weather_cell'
                    }
                })

        return features
