from typing import Dict, List
from data_sources.worldbank import WorldBankAPI
from data_sources.rest_countries import RestCountriesAPI
from data_sources.synthetic_data import SyntheticDataGenerator
from data_sources.nasa import NASAAPI
from data_sources.openweather import OpenWeatherAPI
from data_sources.natural_earth import NaturalEarthAPI
from data_sources.subdivision import SubdivisionAPI
from data_sources.h3_grid import H3GridGenerator
from data_sources.usgs import USGSAPI
from data_sources.satellite import SatelliteAPI
import requests
import random

class UnifiedDataService:
    def __init__(self):
        self.worldbank = WorldBankAPI()
        self.rest_countries = RestCountriesAPI()
        self.synthetic = SyntheticDataGenerator()
        self.nasa = NASAAPI()
        self.weather = OpenWeatherAPI()
        self.natural_earth = NaturalEarthAPI()
        self.subdivision = SubdivisionAPI()
        self.h3_grid = H3GridGenerator()
        self.usgs = USGSAPI()
        self.satellite = SatelliteAPI()
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        
    def fetch_data(self, source: str, location: str, data_type: str) -> Dict:
        print(f"🔄 Fetching from {source}: {data_type} for {location}")
        
        handlers = {
            'worldbank': self._fetch_demographic,
            'weather': self._fetch_weather,
            'earthquakes': self._fetch_earthquakes,
            'satellite': self._fetch_satellite,
            'openstreetmap': self._fetch_osm
        }
        
        handler = handlers.get(source, self._fetch_osm)
        return handler(location, data_type)
    
    def _fetch_demographic(self, location: str, data_type: str) -> Dict:
        print(f"📊 Fetching demographic data for {location}")
        
        country_code = self.worldbank.search_country(location)
        demographic_data = None
        
        if country_code:
            print(f"🔍 Trying World Bank for {country_code}...")
            if data_type == 'population':
                demographic_data = self.worldbank.get_population_data(country_code)
            else:
                demographic_data = self.worldbank.get_population_density(country_code)
        
        if not demographic_data:
            print(f"🔍 World Bank failed, trying REST Countries...")
            demographic_data = self.rest_countries.get_country_data(location)
        
        if not demographic_data:
            print(f"⚠️ Using synthetic data for {location}")
            demographic_data = self.synthetic.get_country_data(location)
        
        value_key = 'population' if data_type == 'population' else 'density'
        value = demographic_data[value_key]
        unit = 'people' if data_type == 'population' else 'people/km²'
        formatted = f"{value:,.0f}" if data_type == 'population' else f"{value:,.1f}"
        
        coords = self._geocode(location)
        subdivisions = self.subdivision.get_subdivisions(location)
        
        if subdivisions and len(subdivisions['features']) > 3:
            print(f"✅ Using {len(subdivisions['features'])} subdivisions")
            return self._create_subdivision_layer(
                demographic_data, subdivisions, data_type, 
                value_key, unit, coords, location
            )
        else:
            print(f"✅ Using H3 grid")
            return self._create_h3_layer(
                demographic_data, location, data_type,
                value_key, unit, coords
            )
    
    def _create_subdivision_layer(self, data: Dict, subdivisions: Dict, 
                                 data_type: str, value_key: str, unit: str, 
                                 coords: Dict, location: str) -> Dict:
        value = data[value_key]
        formatted = f"{value:,.0f}" if data_type == 'population' else f"{value:,.1f}"
        
        features = []
        for feature in subdivisions['features']:
            region_value = value * (0.7 + random.random() * 0.6) / len(subdivisions['features'])
            region_formatted = f"{region_value:,.0f}" if data_type == 'population' else f"{region_value:,.1f}"
            
            feature['properties'].update({
                'value': region_value,
                'formatted': region_formatted,
                'unit': unit,
                'year': data['year'],
                'region': feature['properties'].get('name', 'Unknown')
            })
            features.append(feature)
        
        summary = f"""📊 {data_type.upper()}: {data['country']}

📍 Regions: {len(features)}
👥 Total: {formatted} {unit}
📅 Year: {data['year']}
🔄 Source: {data.get('source', 'World Bank')}

Regional breakdown available."""
        
        return {
            'type': 'FeatureCollection',
            'metadata': {
                'location': location,
                'display_name': data['country'],
                'layer_type': data_type,
                'center': [coords['lon'], coords['lat']],
                'feature_count': len(features),
                'source': data.get('source', 'Multiple'),
                'summary': summary
            },
            'features': features
        }
    
    def _create_h3_layer(self, data: Dict, location: str, data_type: str,
                        value_key: str, unit: str, coords: Dict) -> Dict:
        value = data[value_key]
        formatted = f"{value:,.0f}" if data_type == 'population' else f"{value:,.1f}"
        
        bbox = coords.get('bbox')
        if bbox:
            bounds = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        else:
            bounds = (coords['lat'] - 5, coords['lat'] + 5, coords['lon'] - 5, coords['lon'] + 5)
        
        hexagons = self.h3_grid.generate_grid(bounds, resolution=4)
        
        features = []
        for hex_id in hexagons[:200]:
            hex_value = self.h3_grid.interpolate_value(value / len(hexagons), random.random())
            hex_formatted = f"{hex_value:,.0f}" if data_type == 'population' else f"{hex_value:,.1f}"
            
            features.append(self.h3_grid.hex_to_geojson(hex_id, {
                'value': hex_value,
                'formatted': hex_formatted,
                'unit': unit,
                'year': data['year']
            }))
        
        summary = f"""📊 {data_type.upper()}: {data['country']}

🔷 H3 Grid: {len(features)} cells
👥 Total: {formatted} {unit}
📅 Year: {data['year']}
🔄 Source: {data.get('source', 'World Bank')}

Interpolated hexagonal distribution."""
        
        return {
            'type': 'FeatureCollection',
            'metadata': {
                'location': location,
                'display_name': data['country'],
                'layer_type': data_type,
                'center': [coords['lon'], coords['lat']],
                'feature_count': len(features),
                'source': data.get('source', 'Multiple'),
                'summary': summary
            },
            'features': features
        }
    
    def _fetch_weather(self, location: str, data_type: str) -> Dict:
        coords = self._geocode(location)
        weather_data = self.weather.get_weather_data(coords['lat'], coords['lon'])
        
        if not weather_data:
            return self._error_response("Weather data not available")
        
        bbox = coords.get('bbox')
        bounds = (
            float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
        ) if bbox else (coords['lat'] - 1, coords['lat'] + 1, coords['lon'] - 1, coords['lon'] + 1)
        
        hexagons = self.h3_grid.generate_grid(bounds, resolution=5)
        features = []
        
        for hex_id in hexagons[:100]:
            hex_temp = weather_data['temperature'] + (random.random() - 0.5) * 5
            features.append(self.h3_grid.hex_to_geojson(hex_id, {
                'temperature': round(hex_temp, 1),
                'wind_speed': weather_data['wind_speed'],
                'precipitation': weather_data['precipitation']
            }))
        
        summary = f"""📊 Weather: {location}

🌡️ {weather_data['temperature']}°C
💨 {weather_data['wind_speed']} km/h
🌧️ {weather_data['precipitation']} mm"""
        
        return {
            'type': 'FeatureCollection',
            'metadata': {
                'location': location,
                'layer_type': 'weather',
                'center': [coords['lon'], coords['lat']],
                'feature_count': len(features),
                'source': 'Open-Meteo',
                'summary': summary
            },
            'features': features
        }
    
    def _fetch_earthquakes(self, location: str, data_type: str) -> Dict:
        coords = self._geocode(location)
        earthquake_data = self.usgs.get_earthquakes(coords['lat'], coords['lon'], radius_km=2000, days=30)
        
        if not earthquake_data or not earthquake_data.get('features'):
            return self._error_response("No earthquake data for this region")
        
        features = earthquake_data['features']
        summary = f"""📊 Earthquakes: {location}

🌍 {len(features)} events
📅 Last 30 days
🔍 M 2.5+"""
        
        return {
            'type': 'FeatureCollection',
            'metadata': {
                'location': location,
                'layer_type': 'earthquakes',
                'center': [coords['lon'], coords['lat']],
                'feature_count': len(features),
                'source': 'USGS',
                'summary': summary
            },
            'features': features
        }
    
    def _fetch_satellite(self, location: str, data_type: str) -> Dict:
        coords = self._geocode(location)
        summary = f"📊 Satellite: {location}\n\n🛰️ High-resolution imagery"
        
        return {
            'type': 'FeatureCollection',
            'metadata': {
                'location': location,
                'layer_type': 'satellite',
                'center': [coords['lon'], coords['lat']],
                'feature_count': 1,
                'source': 'ArcGIS',
                'summary': summary
            },
            'features': []
        }
    
    def _fetch_osm(self, location: str, data_type: str) -> Dict:
        coords = self._geocode(location)
        
        type_queries = {
            'parks': '[leisure=park]',
            'roads': '[highway~"motorway|trunk|primary|secondary"]',
            'buildings': '[building]',
            'water': '[natural=water]',
            'forests': '[landuse=forest]'
        }
        
        osm_filter = type_queries.get(data_type, '[building]')
        
        query = f"""
        [out:json][timeout:25];
        (
          way{osm_filter}(around:10000,{coords['lat']},{coords['lon']});
        );
        out geom;
        """
        
        try:
            response = requests.post(self.overpass_url, data=query, timeout=30)
            if response.status_code == 200:
                elements = response.json()['elements']
                features = self._osm_to_geojson(elements)
                
                return {
                    'type': 'FeatureCollection',
                    'metadata': {
                        'location': location,
                        'layer_type': data_type,
                        'center': [coords['lon'], coords['lat']],
                        'feature_count': len(features),
                        'source': 'OSM',
                        'summary': f"📊 {data_type.upper()}: {len(features)} features"
                    },
                    'features': features
                }
        except:
            pass
        
        return self._error_response("OSM fetch failed")
    
    def _geocode(self, location: str) -> Dict:
        try:
            response = requests.get(
                f"{self.nominatim_url}/search",
                params={'q': location, 'format': 'json', 'limit': 1},
                headers={'User-Agent': 'Razorbill2/1.0'},
                timeout=10
            )
            
            if response.status_code == 200 and response.json():
                result = response.json()[0]
                return {
                    'lat': float(result['lat']),
                    'lon': float(result['lon']),
                    'bbox': result.get('boundingbox'),
                    'display_name': result.get('display_name')
                }
        except:
            pass
        
        return {'lat': 55.7558, 'lon': 37.6173, 'bbox': None, 'display_name': location}
    
    def _osm_to_geojson(self, elements: List) -> List:
        features = []
        for el in elements[:1000]:
            try:
                if el['type'] == 'way' and 'geometry' in el:
                    coords = [[n['lon'], n['lat']] for n in el['geometry']]
                    if len(coords) >= 2:
                        is_closed = len(coords) >= 3 and coords[0] == coords[-1]
                        features.append({
                            'type': 'Feature',
                            'geometry': {
                                'type': 'Polygon' if is_closed else 'LineString',
                                'coordinates': [coords] if is_closed else coords
                            },
                            'properties': el.get('tags', {})
                        })
            except:
                continue
        return features
    
    def _error_response(self, message: str) -> Dict:
        return {
            'type': 'FeatureCollection',
            'metadata': {
                'error': message,
                'feature_count': 0,
                'summary': f"❌ {message}"
            },
            'features': []
        }
