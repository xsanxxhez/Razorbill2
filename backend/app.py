from flask import Flask, request, jsonify
from dotenv import load_dotenv
from ai_agent import DataSourceAgent
from unified_data_service import UnifiedDataService
from cache_manager import CacheManager

load_dotenv()

app = Flask(__name__)

# Manual CORS handling - add headers to every response
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

agent = DataSourceAgent()
data_service = UnifiedDataService()
cache = CacheManager(ttl=1800)

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200

    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'layer_data': None
            }), 400

        user_message = data.get('message', '')

        if not user_message:
            return jsonify({
                'success': False,
                'message': 'Message is required',
                'layer_data': None
            }), 400

        print(f"✓ Received message: {user_message}")

        decision = agent.analyze_query(user_message)
        print(f"✓ Decision: {decision}")

        # Check if it's chat mode (no data fetch needed)
        if decision.get('mode') == 'chat':
            return jsonify({
                'success': True,
                'message': decision['message'],
                'layer_data': None,
                'view_position': None
            }), 200

        # Data mode - fetch and visualize
        cached_data = cache.get(
            decision['source'],
            decision['location'],
            decision['data_type']
        )

        if cached_data:
            print("✓ Using cached data")
            layer_data = cached_data
        else:
            print("✓ Fetching fresh data")
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
            }), 200

        # Use AI's friendly message + data summary
        ai_message = decision.get('message', '')
        data_summary = layer_data['metadata'].get('summary', '')
        combined_message = f"{ai_message}\n\n{data_summary}"

        print(f"✓ Returning response with data")

        return jsonify({
            'success': True,
            'message': combined_message,
            'layer_data': layer_data,
            'view_position': layer_data['metadata'].get('center')
        }), 200

    except Exception as e:
        print(f"✗ Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'layer_data': None
        }), 500

@app.route('/api/clear-cache', methods=['POST', 'OPTIONS'])
def clear_cache():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200

    try:
        cache.clear()
        return jsonify({'success': True, 'message': 'Cache cleared'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Razorbill2 API'}), 200

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 RAZORBILL2 BACKEND STARTING")
    print("="*60)
    print(f"Server: http://127.0.0.1:5000")
    print(f"Health: http://127.0.0.1:5000/api/health")
    print(f"Chat:   http://127.0.0.1:5000/api/chat")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, host='127.0.0.1')
