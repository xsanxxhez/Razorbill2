import os
import json
import re
import requests

class AIAssistant:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY', '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')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3.2-3b-instruct:free"
        
    def parse_user_request(self, message):
        print(f"🔍 Parsing: {message}")
        
        system_prompt = """Extract location and layer type from user query. Respond with JSON ONLY.

Available layers: parks, gardens, forests, water, rivers, lakes, buildings, roads, streets, railway, airports, restaurants, cafes, shops, schools, hospitals, sports, playgrounds, farmland, parking

Format: {"type": "data_layer", "location": "city", "layer_type": "parks"}

Examples:
"Show parks in Paris" -> {"type": "data_layer", "location": "Paris", "layer_type": "parks"}
"Покажи реки в Казани" -> {"type": "data_layer", "location": "Казань", "layer_type": "rivers"}
"Buildings in Tokyo" -> {"type": "data_layer", "location": "Tokyo", "layer_type": "buildings"}
"""
        
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.1
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                json_match = re.search(r'\{[^{}]*\}', content)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    print(f"✅ AI parsed: {parsed}")
                    return parsed
                    
        except Exception as e:
            print(f"⚠️  AI error: {e}")
        
        return self._advanced_parse(message)
    
    def _advanced_parse(self, message):
        message_lower = message.lower()
        
        layer_keywords = {
            'parks': ['парк', 'park'],
            'gardens': ['сад', 'garden'],
            'forests': ['лес', 'forest'],
            'water': ['вод', 'water'],
            'rivers': ['реч', 'реки', 'river'],
            'lakes': ['озер', 'lake'],
            'buildings': ['здан', 'building', 'дом'],
            'roads': ['дорог', 'road', 'трасс'],
            'streets': ['улиц', 'street'],
            'railway': ['железн', 'railway', 'поезд', 'train'],
            'airports': ['аэропорт', 'airport'],
            'restaurants': ['ресторан', 'restaurant'],
            'cafes': ['кафе', 'cafe'],
            'shops': ['магазин', 'shop'],
            'schools': ['школ', 'school'],
            'hospitals': ['больниц', 'hospital'],
            'sports': ['спорт', 'sport'],
        }
        
        layer_type = 'buildings'
        for layer, keywords in layer_keywords.items():
            if any(kw in message_lower for kw in keywords):
                layer_type = layer
                break
        
        cities = {
            'москв': 'Москва', 'moscow': 'Moscow',
            'петербург': 'Санкт-Петербург', 'питер': 'Санкт-Петербург',
            'казан': 'Казань', 'kazan': 'Kazan',
            'сочи': 'Сочи', 'париж': 'Paris', 'лондон': 'London',
            'токио': 'Tokyo', 'нью-йорк': 'New York', 'берлин': 'Berlin'
        }
        
        location = 'Москва'
        for key, city in cities.items():
            if key in message_lower:
                location = city
                break
        
        result = {
            'type': 'data_layer',
            'location': location,
            'layer_type': layer_type
        }
        print(f"📤 Fallback result: {result}")
        return result
