from flask import Flask, request, jsonify
from datetime import datetime
import logging
import json

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def log_request(endpoint_name):
    """Helper function to log request details and payload"""
    request_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'endpoint': endpoint_name,
        'method': request.method,
        'url': request.url,
        'headers': dict(request.headers),
        'args': request.args.to_dict(),
        'json': request.get_json(silent=True),
        'form': request.form.to_dict(),
        'remote_addr': request.remote_addr
    }

    logger.info(f"Request captured at {endpoint_name}:")
    logger.info(json.dumps(request_data, indent=2))

    return request_data


@app.route('/api/webhook', methods=['POST', 'GET'])
def webhook():
    """Endpoint 1: Generic webhook that accepts any data"""
    request_data = log_request('/api/webhook')

    response = {
        'status': 'success',
        'message': 'Webhook received',
        'captured_data': request_data
    }

    return jsonify(response), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint 2: Chat endpoint simulating a conversational interface"""
    request_data = log_request('/api/chat')

    payload = request.get_json(silent=True) or {}
    message = payload.get('message', '')
    user_id = payload.get('user_id', 'anonymous')

    response = {
        'status': 'success',
        'user_id': user_id,
        'received_message': message,
        'response': f'Echo: {message}',
        'timestamp': datetime.utcnow().isoformat(),
        'captured_data': request_data
    }

    return jsonify(response), 200


@app.route('/api/data', methods=['POST', 'PUT'])
def data():
    """Endpoint 3: Data processing endpoint"""
    request_data = log_request('/api/data')

    payload = request.get_json(silent=True) or {}

    response = {
        'status': 'success',
        'message': 'Data processed successfully',
        'processed_items': len(payload) if isinstance(payload, (dict, list)) else 0,
        'captured_data': request_data
    }

    return jsonify(response), 200


@app.route('/api/events/<event_type>', methods=['POST'])
def events(event_type):
    """Endpoint 4: Event tracking endpoint with dynamic event types"""
    request_data = log_request(f'/api/events/{event_type}')

    payload = request.get_json(silent=True) or {}

    response = {
        'status': 'success',
        'event_type': event_type,
        'message': f'Event "{event_type}" logged successfully',
        'event_data': payload,
        'captured_data': request_data
    }

    return jsonify(response), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation"""
    return jsonify({
        'message': 'Flask Request Capture API',
        'endpoints': {
            '/api/webhook': {
                'methods': ['GET', 'POST'],
                'description': 'Generic webhook that accepts any data'
            },
            '/api/chat': {
                'methods': ['POST'],
                'description': 'Chat endpoint for conversational interfaces',
                'payload_example': {
                    'message': 'Hello',
                    'user_id': 'user123'
                }
            },
            '/api/data': {
                'methods': ['POST', 'PUT'],
                'description': 'Data processing endpoint'
            },
            '/api/events/<event_type>': {
                'methods': ['POST'],
                'description': 'Event tracking with dynamic event types',
                'example': '/api/events/user_signup'
            },
            '/health': {
                'methods': ['GET'],
                'description': 'Health check endpoint'
            }
        }
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
