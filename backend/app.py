from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from ai_agent import DataSourceAgent
from unified_data_service import UnifiedDataService
from cache_manager import CacheManager

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

agent = DataSourceAgent()
data_service = UnifiedDataService()
cache = CacheManager(ttl=1800)

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    user_message = data.get('message', '')
    
    decision = agent.analyze_query(user_message)
    
    cached_data = cache.get(
        decision['source'],
        decision['location'],
        decision['data_type']
    )
    
    if cached_data:
        layer_data = cached_data
    else:
        layer_data = data_service.fetch_data(
            source=decision['source'],
            location=decision['location'],
            data_type=decision['data_type']
        )
        
        if 'error' not in layer_data.get('metadata', {}):
            cache.set(
                decision['source'],
                decision['location'],
                decision['data_type'],
                layer_data
            )
    
    if 'error' in layer_data.get('metadata', {}):
        return jsonify({
            'success': False,
            'message': layer_data['metadata']['summary'],
            'layer_data': None
        })
    
    summary = layer_data['metadata'].get('summary', '')
    
    return jsonify({
        'success': True,
        'message': summary,
        'layer_data': layer_data,
        'view_position': layer_data['metadata'].get('center')
    })

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    cache.clear()
    return jsonify({'success': True, 'message': 'Cache cleared'})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')
