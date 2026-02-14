import requests
import json
import re
from typing import Dict, Tuple

class DataSourceAgent:
    def __init__(self):
        self.api_key = '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'
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.conversation_history = []

    def analyze_query(self, user_query: str) -> Dict:
        print(f"🤖 AI analyzing: {user_query}")

        system_prompt = """You are Razorbill AI, a helpful geospatial data assistant with dual capabilities:

MODE 1: DATA VISUALIZATION ROUTING
When users request geospatial data (weather, earthquakes, locations, populations, etc.), respond with JSON ONLY.

Available data sources:
1. "open_meteo" - Real-time weather (temperature, wind, conditions)
2. "geocoding" - Find any location on Earth  
3. "rest_countries" - Country information, borders, flags, population
4. "usgs" - Real-time earthquake data worldwide
5. "openstreetmap" - Roads, buildings, parks, water bodies
6. "worldbank" - Population, GDP, demographics
7. "air_quality" - Air pollution (PM2.5, PM10)
8. "nasa" - Satellite imagery, climate data
9. "natural_earth" - Geographic boundaries, cities
10. "h3_grid" - Hexagonal spatial indexing

For data requests, respond ONLY with JSON (no markdown):
{
  "mode": "data",
  "source": "source_name",
  "location": "extracted_location_name", 
  "data_type": "specific_data_type",
  "message": "friendly response to user"
}

MODE 2: CONVERSATION
When users ask general questions, greet you, thank you, or chat, respond naturally as a helpful assistant.

For conversations, respond with JSON:
{
  "mode": "chat",
  "message": "your natural conversational response"
}

Examples:

Query: "weather in Belarus"
{"mode": "data", "source": "open_meteo", "location": "Belarus", "data_type": "weather", "message": "Let me fetch the current weather in Belarus for you! 🌤️"}

Query: "show me New York"  
{"mode": "data", "source": "geocoding", "location": "New York", "data_type": "location", "message": "Flying you to New York now! 🗽"}

Query: "earthquakes in Japan"
{"mode": "data", "source": "usgs", "location": "Japan", "data_type": "earthquakes", "message": "Checking recent seismic activity in Japan... 🌋"}

Query: "population in Brazil"
{"mode": "data", "source": "rest_countries", "location": "Brazil", "data_type": "country", "message": "Looking up Brazil's population data! 🇧🇷"}

Query: "hello"
{"mode": "chat", "message": "Hello! 👋 I'm Razorbill AI, your geospatial assistant. I can show you weather, earthquakes, locations, country data, and more! Just ask me about any place on Earth. What would you like to explore?"}

Query: "what can you do?"
{"mode": "chat", "message": "I can visualize geospatial data on a 3D globe! Try asking me:\n• Weather anywhere (e.g., 'weather in Tokyo')\n• Find locations ('show me Paris')\n• Earthquake data ('earthquakes in California')\n• Country info ('tell me about Italy')\n• And much more! What interests you?"}

Query: "thank you"
{"mode": "chat", "message": "You're welcome! Happy to help you explore our planet! 🌍✨"}

Query: "how does weather prediction work?"
{"mode": "chat", "message": "Weather prediction uses complex atmospheric models that analyze current conditions (temperature, pressure, humidity, wind) and simulate how they'll evolve using physics equations. Modern forecasts combine satellite data, ground sensors, and supercomputer simulations. The accuracy decreases beyond 7-10 days due to chaos theory. Want to see current weather somewhere?"}

IMPORTANT: Always respond with valid JSON only. Extract exact locations from queries."""

        try:
            # Add message to history
            self.conversation_history.append({"role": "user", "content": user_query})

            # Keep last 10 messages for context
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            messages = [{"role": "system", "content": system_prompt}] + self.conversation_history

            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://razorbill2.app",
                    "X-Title": "Razorbill2"
                },
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": messages,
                    "temperature": 0.5,
                    "max_tokens": 500
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()

                # Add assistant response to history
                self.conversation_history.append({"role": "assistant", "content": content})

                # Extract JSON
                content = re.sub(r'```json\s*', '', content)
                content = re.sub(r'```\s*', '', content)

                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))

                    if parsed.get('mode') == 'chat':
                        # Pure conversation, no data fetch
                        print(f"💬 Chat mode: {parsed['message'][:50]}...")
                        return {
                            'mode': 'chat',
                            'message': parsed['message']
                        }

                    elif parsed.get('mode') == 'data':
                        # Data routing
                        print(f"📊 Data mode: {parsed['source']} → {parsed['location']}")
                        return {
                            'mode': 'data',
                            'source': parsed['source'],
                            'location': parsed['location'],
                            'data_type': parsed['data_type'],
                            'message': parsed.get('message', 'Fetching data...')
                        }

                    # Legacy format (no mode specified)
                    if 'source' in parsed:
                        print(f"📊 Legacy format: {parsed['source']} → {parsed.get('location', 'unknown')}")
                        return {
                            'mode': 'data',
                            'source': parsed['source'],
                            'location': parsed.get('location', 'World'),
                            'data_type': parsed.get('data_type', 'unknown'),
                            'message': parsed.get('message', 'Fetching data...')
                        }

                else:
                    print(f"⚠️ Could not extract JSON from: {content}")

            else:
                print(f"❌ OpenRouter API error: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"❌ AI Agent error: {str(e)}")
            import traceback
            traceback.print_exc()

        # Fallback
        return self._intelligent_fallback(user_query)

    def _intelligent_fallback(self, query: str) -> Dict:
        """Smart fallback when AI fails"""
        print(f"⚠️ Using fallback logic")

        q = query.lower()

        # Check if it's a conversational query
        greetings = ['hello', 'hi', 'hey', 'greetings', 'привет', 'здравствуй']
        thanks = ['thank', 'thanks', 'спасибо']
        questions = ['what can you do', 'help', 'how', 'why', 'explain']

        if any(word in q for word in greetings):
            return {
                'mode': 'chat',
                'message': "Hello! 👋 I'm Razorbill AI. I can show you geospatial data on a 3D globe - weather, earthquakes, locations, and more! What would you like to explore?"
            }

        if any(word in q for word in thanks):
            return {
                'mode': 'chat',
                'message': "You're welcome! 😊 Feel free to ask about any location on Earth!"
            }

        if any(word in q for word in questions):
            return {
                'mode': 'chat',
                'message': "I can visualize geospatial data! Try:\n• 'weather in Tokyo'\n• 'show me Paris'\n• 'earthquakes in Japan'\n• 'tell me about Brazil'\n\nWhat interests you?"
            }

        # Otherwise assume it's a data request
        import re
        location_patterns = [
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'in\s+(\w+)',
            r'of\s+(\w+)',
            r'at\s+(\w+)',
        ]

        location = None
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location = match.group(1).strip().title()
                break

        if not location:
            words = query.split()
            for word in words:
                if word and word[0].isupper() and len(word) > 2:
                    location = word
                    break

        if not location:
            location = "World"

        # Route based on keywords
        if any(kw in q for kw in ['weather', 'temperature', 'climate']):
            return {'mode': 'data', 'source': 'open_meteo', 'location': location, 'data_type': 'weather', 'message': f'Fetching weather for {location}...'}

        elif any(kw in q for kw in ['earthquake', 'seismic']):
            return {'mode': 'data', 'source': 'usgs', 'location': location, 'data_type': 'earthquakes', 'message': f'Checking earthquakes near {location}...'}

        elif any(kw in q for kw in ['country', 'nation', 'population', 'people']):
            return {'mode': 'data', 'source': 'rest_countries', 'location': location, 'data_type': 'country', 'message': f'Looking up {location}...'}

        else:
            return {'mode': 'data', 'source': 'geocoding', 'location': location, 'data_type': 'location', 'message': f'Finding {location}...'}
