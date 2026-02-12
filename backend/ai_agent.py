import requests
import json
import re
from typing import Dict

class DataSourceAgent:
    def __init__(self):
        self.api_key = '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'
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def analyze_query(self, user_query: str) -> Dict:
        print(f"🤖 Analyzing: {user_query}")
        
        system_prompt = """Geospatial data router. Respond with JSON ONLY.

Sources:
- openstreetmap: roads, parks, buildings, water
- worldbank: population, density
- weather: current weather
- nasa: temperature, climate
- earthquakes: seismic activity
- pollution: air quality (PM2.5)
- satellite: imagery
- borders: boundaries

Format:
{"source": "source_name", "location": "place", "data_type": "type", "reasoning": "why"}

Examples:
"earthquakes in Japan" -> {"source": "earthquakes", "location": "Japan", "data_type": "seismic", "reasoning": "USGS data"}
"air quality in Beijing" -> {"source": "pollution", "location": "Beijing", "data_type": "pm25", "reasoning": "pollution monitoring"}
"satellite image of Paris" -> {"source": "satellite", "location": "Paris", "data_type": "imagery", "reasoning": "aerial view"}
"""
        
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query}
                    ],
                    "temperature": 0.1
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    print(f"✅ GPT-4: {parsed['source']} -> {parsed['data_type']}")
                    return parsed
                    
        except Exception as e:
            print(f"⚠️ GPT-4 error: {e}")
        
        return self._fallback(user_query)
    
    def _fallback(self, query: str) -> Dict:
        q = query.lower()
        
        if any(kw in q for kw in ['earthquake', 'землетряс', 'seismic']):
            return {'source': 'earthquakes', 'location': 'Japan', 'data_type': 'seismic', 'reasoning': 'fallback'}
        elif any(kw in q for kw in ['pollution', 'air quality', 'загрязн', 'pm2.5']):
            return {'source': 'pollution', 'location': 'Beijing', 'data_type': 'pm25', 'reasoning': 'fallback'}
        elif any(kw in q for kw in ['satellite', 'спутник', 'imagery', 'снимок']):
            return {'source': 'satellite', 'location': 'Paris', 'data_type': 'imagery', 'reasoning': 'fallback'}
        elif any(kw in q for kw in ['weather', 'погод']):
            return {'source': 'weather', 'location': 'London', 'data_type': 'current', 'reasoning': 'fallback'}
        else:
            return {'source': 'openstreetmap', 'location': 'Moscow', 'data_type': 'buildings', 'reasoning': 'fallback'}
