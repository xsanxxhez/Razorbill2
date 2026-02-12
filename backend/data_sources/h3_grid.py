import h3
from typing import List, Tuple, Dict

class H3GridGenerator:
    def __init__(self):
        self.resolution = 4
        
    def generate_grid(self, bounds: Tuple[float, float, float, float], resolution: int = None) -> List[str]:
        if resolution is None:
            resolution = self.resolution
        
        min_lat, max_lat, min_lon, max_lon = bounds
        
        hexagons = set()
        
        lat_step = (max_lat - min_lat) / 20
        lon_step = (max_lon - min_lon) / 20
        
        for lat in [min_lat + i * lat_step for i in range(21)]:
            for lon in [min_lon + i * lon_step for i in range(21)]:
                try:
                    hex_id = h3.latlng_to_cell(lat, lon, resolution)
                    hexagons.add(hex_id)
                except:
                    continue
        
        return list(hexagons)
    
    def hex_to_geojson(self, hex_id: str, properties: Dict = None) -> Dict:
        boundary = h3.cell_to_boundary(hex_id)
        
        coords = [[lon, lat] for lat, lon in boundary]
        coords.append(coords[0])
        
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [coords]
            },
            'properties': properties or {}
        }
    
    def interpolate_value(self, center_value: float, distance_factor: float) -> float:
        variance = (0.5 - distance_factor) * center_value * 0.3
        return center_value + variance
