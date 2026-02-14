from data_sources.geocoding import GeocodingService
from data_sources.open_meteo import OpenMeteoDataSource
from data_sources.rest_countries import RestCountriesDataSource
from data_sources.usgs import USGSDataSource

class UnifiedDataService:
    def __init__(self):
        print("🚀 Initializing data sources...")
        self.sources = {
            'geocoding': GeocodingService(),
            'open_meteo': OpenMeteoDataSource(),
            'rest_countries': RestCountriesDataSource(),
            'usgs': USGSDataSource(),
        }
        print(f"✅ Loaded {len(self.sources)} data sources")

    def fetch_data(self, source, location, data_type):
        print(f"📡 Fetching from {source}: {location} ({data_type})")

        try:
            if source in self.sources:
                result = self.sources[source].fetch(location)
                return result
            else:
                return {
                    'metadata': {
                        'error': True,
                        'summary': f'❌ Unknown data source: {source}'
                    }
                }

        except Exception as e:
            print(f"❌ Unified service error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'metadata': {
                    'error': True,
                    'summary': f'❌ Data fetch failed: {str(e)}'
                }
            }
