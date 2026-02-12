import requests
import json
from typing import Dict, List
from data_sources.worldbank import WorldBankAPI

class GeospatialAPI:
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.worldbank = WorldBankAPI()
        
    def geocode(self, location_name: str) -> Dict:
        print(f"🌍 Geocoding: {location_name}")
        
        try:
            response = requests.get(
                f"{self.nominatim_url}/search",
                params={
                    'q': location_name,
                    'format': 'json',
                    'limit': 1,
                    'accept-language': 'en,ru'
                },
                headers={'User-Agent': 'Razorbill2/1.0'},
                timeout=10
            )
            
            if response.status_code == 200 and response.json():
                result = response.json()[0]
                coords = {
                    'lat': float(result['lat']),
                    'lon': float(result['lon']),
                    'bbox': result.get('boundingbox'),
                    'display_name': result.get('display_name')
                }
                print(f"✅ Geocoded to: {coords['display_name']}")
                return coords
        except Exception as e:
            print(f"❌ Geocoding error: {e}")
        
        print(f"⚠️  Using default coordinates")
        return {'lat': 55.7558, 'lon': 37.6173, 'bbox': None, 'display_name': 'Moscow'}
    
    def fetch_data_layer(self, location: str, layer_type: str, filters: Dict = None) -> Dict:
        print(f"📍 Fetching {layer_type} for {location}")
        
        if layer_type in ['population', 'density']:
            return self._fetch_population_layer(location, layer_type)
        
        coords = self.geocode(location)
        osm_data = self._fetch_osm_data(coords, layer_type)
        
        return {
            'type': 'FeatureCollection',
            'metadata': {
                'location': location,
                'display_name': coords.get('display_name', location),
                'layer_type': layer_type,
                'center': [coords['lon'], coords['lat']],
                'feature_count': len(osm_data),
                'source': 'OpenStreetMap'
            },
            'features': osm_data
        }
    
    def _fetch_population_layer(self, location: str, layer_type: str) -> Dict:
        print(f"📊 Fetching population data for {location}")
        
        country_code = self.worldbank.search_country(location)
        if not country_code:
            return {
                'type': 'FeatureCollection',
                'metadata': {
                    'location': location,
                    'layer_type': layer_type,
                    'error': 'Country not found',
                    'feature_count': 0
                },
                'features': []
            }
        
        if layer_type == 'population':
            data = self.worldbank.get_population_data(country_code)
        else:
            data = self.worldbank.get_population_density(country_code)
        
        if not data:
            return {
                'type': 'FeatureCollection',
                'metadata': {
                    'location': location,
                    'layer_type': layer_type,
                    'error': 'Data not available',
                    'feature_count': 0
                },
                'features': []
            }
        
        coords = self.geocode(location)
        
        if layer_type == 'population':
            value = data['population']
            unit = 'people'
            formatted_value = f"{value:,.0f}"
        else:
            value = data['density']
            unit = 'people/km²'
            formatted_value = f"{value:,.1f}"
        
        print(f"✅ Population data: {formatted_value} {unit} ({data['year']})")
        
        bbox = coords.get('bbox')
        if bbox:
            min_lat, max_lat = float(bbox[0]), float(bbox[1])
            min_lon, max_lon = float(bbox[2]), float(bbox[3])
            
            polygon_coords = [[
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, max_lat],
                [min_lon, max_lat],
                [min_lon, min_lat]
            ]]
        else:
            offset = 5
            polygon_coords = [[
                [coords['lon'] - offset, coords['lat'] - offset],
                [coords['lon'] + offset, coords['lat'] - offset],
                [coords['lon'] + offset, coords['lat'] + offset],
                [coords['lon'] - offset, coords['lat'] + offset],
                [coords['lon'] - offset, coords['lat'] - offset]
            ]]
        
        features = [{
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': polygon_coords
            },
            'properties': {
                'name': data['country'],
                'value': value,
                'formatted_value': formatted_value,
                'unit': unit,
                'year': data['year'],
                'source': 'World Bank',
                'type': layer_type
            }
        }]
        
        return {
            'type': 'FeatureCollection',
            'metadata': {
                'location': location,
                'display_name': data['country'],
                'layer_type': layer_type,
                'center': [coords['lon'], coords['lat']],
                'feature_count': 1,
                'source': 'World Bank',
                'data_info': f"{formatted_value} {unit} ({data['year']})"
            },
            'features': features
        }
    
    def _fetch_osm_data(self, coords: Dict, layer_type: str) -> List:
        queries = {
            'parks': '[leisure=park]',
            'gardens': '[leisure=garden]',
            'forests': '[landuse=forest]',
            'water': '[natural=water]',
            'rivers': '[waterway=river]',
            'lakes': '[natural=water][water=lake]',
            'buildings': '[building]',
            'roads': '[highway~"motorway|trunk|primary|secondary"]',
            'streets': '[highway~"residential|service"]',
            'railway': '[railway=rail]',
            'airports': '[aeroway=aerodrome]',
            'restaurants': '[amenity=restaurant]',
            'cafes': '[amenity=cafe]',
            'shops': '[shop]',
            'schools': '[amenity=school]',
            'hospitals': '[amenity=hospital]',
            'sports': '[leisure=sports_centre]',
        }
        
        osm_filter = queries.get(layer_type, '[building]')
        radius = 5000
        
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node{osm_filter}(around:{radius},{coords['lat']},{coords['lon']});
          way{osm_filter}(around:{radius},{coords['lat']},{coords['lon']});
          relation{osm_filter}(around:{radius},{coords['lat']},{coords['lon']});
        );
        out geom;
        """
        
        try:
            print(f"🔄 Querying Overpass API...")
            response = requests.post(
                self.overpass_url,
                data=overpass_query,
                timeout=30
            )
            
            if response.status_code == 200:
                osm_result = response.json()
                features = self._convert_osm_to_geojson(osm_result['elements'])
                print(f"✅ Found {len(features)} features")
                return features
        except Exception as e:
            print(f"❌ OSM fetch error: {e}")
        
        return []
    
    def _convert_osm_to_geojson(self, elements: List) -> List:
        features = []
        
        for element in elements[:300]:
            try:
                if element['type'] == 'node':
                    features.append({
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [element['lon'], element['lat']]
                        },
                        'properties': element.get('tags', {})
                    })
                
                elif element['type'] == 'way' and 'geometry' in element:
                    coords = [[node['lon'], node['lat']] for node in element['geometry']]
                    
                    if len(coords) < 2:
                        continue
                    
                    is_closed = len(coords) >= 3 and coords[0] == coords[-1]
                    
                    features.append({
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Polygon' if is_closed else 'LineString',
                            'coordinates': [coords] if is_closed else coords
                        },
                        'properties': element.get('tags', {})
                    })
            except Exception as e:
                continue
        
        return features
    
    def get_available_layers(self) -> List[Dict]:
        return [
            {'id': 'population', 'name': 'Population', 'category': 'Demographics', 'source': 'World Bank'},
            {'id': 'density', 'name': 'Population Density', 'category': 'Demographics', 'source': 'World Bank'},
            {'id': 'parks', 'name': 'Parks', 'category': 'Nature', 'source': 'OpenStreetMap'},
            {'id': 'forests', 'name': 'Forests', 'category': 'Nature', 'source': 'OpenStreetMap'},
            {'id': 'water', 'name': 'Water', 'category': 'Nature', 'source': 'OpenStreetMap'},
            {'id': 'buildings', 'name': 'Buildings', 'category': 'Infrastructure', 'source': 'OpenStreetMap'},
            {'id': 'roads', 'name': 'Roads', 'category': 'Infrastructure', 'source': 'OpenStreetMap'},
        ]
