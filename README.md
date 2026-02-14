

# Razorbill — Geospatial AI Analysis Platform (Demo)

A raw, early-stage demo of a geospatial AI analysis platform for **quantitative analysts and quant traders** — built to visualize multi-source data layers, run research-grade analysis pipelines, and turn unstructured inputs into actionable geospatial objects.

<img width="1710" height="1107" alt="image" src="https://github.com/user-attachments/assets/62b7b1ef-47d8-4604-bc0b-89e4a83e1610" />
<img width="1710" height="1107" alt="image" src="https://github.com/user-attachments/assets/e088a5d3-cd18-41d1-8bbc-b5f365f82ad1" />
<img width="1710" height="1107" alt="image" src="https://github.com/user-attachments/assets/f7fec9f8-5fbc-4f9b-8748-0ab6f92acf62" />



---

## Pitch

Razorbill explores a simple idea: markets, people, climate, and infrastructure are spatial systems — and many “edges” appear when you look at data geographically.

The platform combines a 3D globe (“Razorball”) with an NLP-driven AI engine that can interpret requests and translate disparate inputs into geospatial layers. The long-term vision is a research environment where analysts can ingest vast datasets, test hypotheses, and refine probabilistic signals to maximize expected ROI.

---

## Demo highlights

- **3D geospatial visualization (“Razorball”)**  
  Render and explore any supported layer as real geospatial primitives (points/lines/polygons) on an interactive globe.

- **Data layer exploration**  
  Overlay and inspect multiple thematic layers and drill into entities with contextual metadata.

- **Pipeline-first analysis concept**  
  Designed around connected pipelines: ingest → normalize → analyze → visualize, enabling large-scale research flows and statistical edge discovery.

- **Web3 privacy-preserving data aggregation (planned)**  
  A future module aims to serve as an independent data aggregator sourced directly from individual contributors, designed to preserve contributor anonymity when providing sensitive data without legal consequences.

---

## Disclaimer

- **Prototype quality:** Razorbill is a raw demo/proof-of-concept and is not production-ready.
- **No financial advice:** This project is for research and engineering exploration only and does not constitute investment advice.
- **Project status:** The project is currently **frozen** due to maintenance and funding constraints that are not accessible to the co-founders at this time.

---

## Architecture Overview

### Data Flow

1. **User Query Processing**
   - User submits natural language query (e.g., "Show me weather in London")

2. **AI Agent Analysis** (`ai_agent.py`)
   - Extracts location ("London"), data type ("weather"), and optimal data source ("OpenWeather API")
   - Returns decision object: `{source: 'openweather', location: 'London', data_type: 'weather'}`

3. **Unified Data Service** (`unified_data_service.py`)
   - Calls the appropriate data source module (e.g., `data_sources/openweather.py`)
   - Module executes real HTTP request to external API (OpenWeather, NASA, USGS, WorldBank, etc.)
   - Receives JSON response with current data

4. **GeoJSON Conversion**
   - Each data source converts API response to standardized GeoJSON format
   - GeoJSON includes coordinates (latitude/longitude) and properties (temperature, magnitude, population, etc.)

5. **Frontend Visualization** (`CesiumViewer.jsx`)
   - Receives GeoJSON data
   - Renders 3D shapes on Cesium globe (polygons, points, polylines)
   - Applies visual encoding based on data values (temperature mapped to color gradients, population to extrusion height)

6. **Cache Manager** (`cache_manager.py`)
   - Stores API responses to minimize redundant requests
   - Time-to-live (TTL) of 1800 seconds (30 minutes)

### Integrated Data Sources

- **OpenWeather** - Real-time weather data
- **NASA** - Satellite imagery and Earth observation data
- **USGS** - Real-time earthquake monitoring
- **WorldBank** - Economic and demographic statistics
- **Air Quality APIs** - Environmental monitoring data
- **H3 Grid** - Uber's hexagonal spatial indexing system
- **Natural Earth** - Geographic boundary data
- **Rest Countries** - Country metadata and information
- **Satellite Tracking** - Orbital positioning data
- **Subdivision Data** - Administrative divisions
- **Synthetic Data Generator** - Testing and demonstration data

## Technology Stack

**Backend**
- Python 3.x
- Flask (REST API)
- Multiple API integrations
- Caching layer

**Frontend**
- React 18
- Vite (build tool)
- Cesium (3D globe visualization)
- Deck.gl (GPU-accelerated layers)
- MapLibre (vector tile rendering)
- Leaflet (2D mapping)

## Key Features

- Real-time data fetching from 11+ external APIs
- Natural language query interface
- Multi-source data aggregation through unified service layer
- Four different visualization engines for various use cases
- Intelligent caching system for performance optimization
- Standardized GeoJSON output format
- 3D visualization with dynamic styling based on data values


## Team of RAZORBILL
<img width="200" height="200" alt="image" src="https://github.com/user-attachments/assets/b196b9ff-f52d-4f20-9aa7-12361b9cdd3b" />
## Co-founders:
- Alexander Ageenko
- Eugene Hancharou

