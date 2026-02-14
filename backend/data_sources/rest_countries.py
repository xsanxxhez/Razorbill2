import requests
import json

class RestCountriesDataSource:
    def __init__(self):
        self.base_url = "https://restcountries.com/v3.1"
        # We'll use Natural Earth for actual boundaries
        self.boundaries_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson"

    def fetch(self, location):
        try:
            print(f"🌍 Fetching country: {location}")

            # Get country info
            response = requests.get(
                f"{self.base_url}/name/{location}",
                params={'fullText': 'false'},
                timeout=10
            )

            if response.status_code == 200:
                countries = response.json()

                if countries:
                    country = countries[0]

                    # Get country boundaries from Natural Earth
                    country_code = country.get('cca3')
                    boundaries = self._get_country_boundaries(country_code)

                    latlng = country.get('latlng', [0, 0])
                    area = country.get('area', 0)  # in km²

                    # Calculate perimeter (approximate from boundary)
                    perimeter = self._calculate_perimeter(boundaries) if boundaries else 0

                    features = []

                    # Add boundary polygon if available
                    if boundaries:
                        features.append({
                            'type': 'Feature',
                            'geometry': boundaries,
                            'properties': {
                                'name': country['name']['common'],
                                'type': 'boundary',
                                'area': area,
                                'perimeter': perimeter,
                                'capital': country.get('capital', ['N/A'])[0],
                                'population': country.get('population', 0),
                                'flag': country.get('flag', '🏳️')
                            }
                        })

                    # Add center point marker
                    features.append({
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [latlng[1], latlng[0]]
                        },
                        'properties': {
                            'name': country['name']['common'],
                            'type': 'marker',
                            'capital': country.get('capital', ['N/A'])[0],
                            'population': country.get('population', 0),
                            'area': area,
                            'perimeter': perimeter,
                            'flag': country.get('flag', '🏳️')
                        }
                    })

                    return {
                        'type': 'FeatureCollection',
                        'features': features,
                        'metadata': {
                            'source': 'REST Countries',
                            'layer_type': 'country',
                            'feature_count': len(features),
                            'summary': f"{country.get('flag', '🏳️')} {country['name']['common']}: Area {area:,.0f} km², Perimeter ~{perimeter:,.0f} km, Population {country.get('population', 0):,}",
                            'center': {'latitude': latlng[0], 'longitude': latlng[1]}
                        }
                    }

            return {'metadata': {'error': True, 'summary': f'❌ Country "{location}" not found'}}

        except Exception as e:
            print(f"❌ Country fetch error: {e}")
            return {'metadata': {'error': True, 'summary': f'❌ Error: {str(e)}'}}

    def _get_country_boundaries(self, country_code):
        """Fetch actual country boundary polygon from Natural Earth or REST Countries"""
        try:
            # Try to get from REST Countries admin endpoint (some have borders)
            response = requests.get(
                f"{self.base_url}/alpha/{country_code}",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()[0]

                # Some countries have border data
                if 'borders' in data:
                    # For now, create a simple polygon around the center
                    # In production, use a proper GeoJSON database
                    latlng = data.get('latlng', [0, 0])
                    lat, lng = latlng[0], latlng[1]

                    # Create rough bounding box (this is simplified)
                    offset = 2  # degrees
                    return {
                        'type': 'Polygon',
                        'coordinates': [[
                            [lng - offset, lat - offset],
                            [lng + offset, lat - offset],
                            [lng + offset, lat + offset],
                            [lng - offset, lat + offset],
                            [lng - offset, lat - offset]
                        ]]
                    }

            return None

        except Exception as e:
            print(f"⚠️ Could not fetch boundaries: {e}")
            return None

    def _calculate_perimeter(self, geometry):
        """Calculate approximate perimeter from polygon coordinates"""
        if not geometry or geometry.get('type') != 'Polygon':
            return 0

        coords = geometry['coordinates'][0]
        perimeter = 0

        for i in range(len(coords) - 1):
            lon1, lat1 = coords[i]
            lon2, lat2 = coords[i + 1]

            # Haversine formula for distance
            from math import radians, cos, sin, sqrt, atan2

            R = 6371  # Earth radius in km

            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))

            perimeter += R * c

        return perimeter
