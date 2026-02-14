import requests
import time

class GeocodingService:
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.last_request = 0

    def fetch(self, location):
        # Rate limit: 1 request per second
        elapsed = time.time() - self.last_request
        if elapsed < 1:
            time.sleep(1 - elapsed)
        self.last_request = time.time()

        print(f"🌍 Geocoding: {location}")

        try:
            response = requests.get(
                self.nominatim_url,
                params={
                    'q': location,
                    'format': 'geojson',
                    'limit': 1,
                    'addressdetails': 1
                },
                headers={'User-Agent': 'Razorbill2/1.0'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if data.get('features'):
                    feature = data['features'][0]
                    coords = feature['geometry']['coordinates']
                    name = feature['properties'].get('display_name', location)

                    # Create a point with radius for better visibility
                    return {
                        'type': 'FeatureCollection',
                        'features': [{
                            'type': 'Feature',
                            'geometry': {
                                'type': 'Point',
                                'coordinates': coords
                            },
                            'properties': {
                                'name': name,
                                'type': feature['properties'].get('type', 'location')
                            }
                        }],
                        'metadata': {
                            'source': 'OpenStreetMap Nominatim',
                            'layer_type': 'location',
                            'feature_count': 1,
                            'summary': f"📍 {name}",
                            'center': {'latitude': coords[1], 'longitude': coords[0]}
                        }
                    }

                return {'metadata': {'error': True, 'summary': f'❌ Location "{location}" not found'}}

            return {'metadata': {'error': True, 'summary': f'❌ Geocoding failed: HTTP {response.status_code}'}}

        except Exception as e:
            print(f"❌ Geocoding error: {e}")
            return {'metadata': {'error': True, 'summary': f'❌ Error: {str(e)}'}}
