import requests
from datetime import datetime, timedelta

class USGSDataSource:
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def fetch(self, location):
        try:
            print(f"🌋 Fetching earthquakes near: {location}")

            # Geocode location to get bbox
            lat, lon = self._geocode(location)

            if lat is None:
                return {'metadata': {'error': True, 'summary': f'❌ Location not found: {location}'}}

            # Get earthquakes in last 30 days within 500km radius
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)

            response = requests.get(
                self.base_url,
                params={
                    'format': 'geojson',
                    'starttime': start_time.isoformat(),
                    'endtime': end_time.isoformat(),
                    'latitude': lat,
                    'longitude': lon,
                    'maxradiuskm': 500,
                    'minmagnitude': 2.5,
                    'orderby': 'magnitude'
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()

                features = data.get('features', [])
                count = len(features)

                if count == 0:
                    return {'metadata': {'error': True, 'summary': f'✅ No significant earthquakes (M2.5+) near {location} in last 30 days'}}

                # Get strongest earthquake
                strongest = max(features, key=lambda f: f['properties']['mag'])
                max_mag = strongest['properties']['mag']

                return {
                    'type': 'FeatureCollection',
                    'features': features[:50],  # Limit to 50 most significant
                    'metadata': {
                        'source': 'USGS',
                        'layer_type': 'earthquakes',
                        'feature_count': min(count, 50),
                        'summary': f"🌋 {count} earthquakes near {location} (last 30 days). Strongest: M{max_mag:.1f}",
                        'center': {'latitude': lat, 'longitude': lon}
                    }
                }

            return {'metadata': {'error': True, 'summary': f'❌ USGS API error: {response.status_code}'}}

        except Exception as e:
            print(f"❌ Earthquake fetch error: {e}")
            return {'metadata': {'error': True, 'summary': f'❌ Error: {str(e)}'}}

    def _geocode(self, location):
        import time
        time.sleep(1)

        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={'q': location, 'format': 'json', 'limit': 1},
                headers={'User-Agent': 'Razorbill2/1.0'},
                timeout=10
            )

            if response.status_code == 200 and response.json():
                data = response.json()[0]
                return float(data['lat']), float(data['lon'])

            return None, None
        except:
            return None, None
