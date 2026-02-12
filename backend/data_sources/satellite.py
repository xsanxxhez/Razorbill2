import requests
from typing import Dict, Optional

class SatelliteAPI:
    def __init__(self):
        self.base_url = "https://services.sentinel-hub.com/ogc/wms"
        
    def get_satellite_tile_url(self, bbox: tuple, width: int = 512, height: int = 512) -> str:
        min_lat, max_lat, min_lon, max_lon = bbox
        
        tile_url = (
            f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/"
            f"{{z}}/{{y}}/{{x}}"
        )
        
        return {
            'type': 'satellite',
            'tile_url': tile_url,
            'bbox': bbox,
            'description': 'High-resolution satellite imagery'
        }
