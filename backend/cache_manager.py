import json
import hashlib
import time
from typing import Dict, Optional

class CacheManager:
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl
    
    def _generate_key(self, source: str, location: str, data_type: str) -> str:
        data = f"{source}:{location}:{data_type}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, source: str, location: str, data_type: str) -> Optional[Dict]:
        key = self._generate_key(source, location, data_type)
        
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                print(f"✅ Cache HIT: {source}/{location}/{data_type}")
                return entry['data']
            else:
                del self.cache[key]
        
        return None
    
    def set(self, source: str, location: str, data_type: str, data: Dict):
        key = self._generate_key(source, location, data_type)
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        print(f"💾 Cached: {source}/{location}/{data_type}")
    
    def clear(self):
        self.cache.clear()
        print("🗑️ Cache cleared")
