from flask import Flask, request, jsonify
from datetime import datetime
import logging
import json
import base64
import os
from dotenv import load_dotenv
from fal_service import get_fal_service
from db import save_pinterest_credentials, get_pinterest_credentials
from pinterest_service import PinterestService, get_pinterest_status

# Load environment variables
load_dotenv()

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


def process_image(image_data, filename):
    """Process the uploaded image - placeholder for actual processing logic"""
    logger.info(f"Processing image: {filename}")
    logger.info(f"Image size: {len(image_data)} bytes")

    # Here you can add actual image processing logic
    # For now, just return success
    return {
        'status': 'success',
        'message': 'Image processed successfully',
        'image_size': len(image_data),
        'filename': filename
    }


@app.route('/api/upload', methods=['POST'])
def upload_base64():
    """Endpoint 5: Upload and process base64 encoded images with AI editing"""
    request_data = log_request('/api/upload')

    try:
        data = request.get_json()

        if not data or 'image' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No image data provided. Please include "image" field with base64 encoded data.'
            }), 400

        base64_image = data.get('image')
        filename = data.get('filename', f'image_{datetime.utcnow().timestamp()}.jpg')
        prompt = data.get('prompt')  # Get the prompt for AI editing

        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'No prompt provided. Please include "prompt" field for AI image editing.'
            }), 400

        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]

        # Decode base64 image
        try:
            image_data = base64.b64decode(base64_image)
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid base64 image data'
            }), 400

        # Create uploads directory if it doesn't exist
        uploads_dir = 'uploads'
        os.makedirs(uploads_dir, exist_ok=True)

        # Save the original image
        filepath = os.path.join(uploads_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(image_data)

        logger.info(f"Image saved to: {filepath}")

        # Get optional parameters for AI editing
        image_size = data.get('image_size', 'auto')
        output_format = data.get('output_format', 'png')
        enable_prompt_expansion = data.get('enable_prompt_expansion', False)
        seed = data.get('seed')

        # Process the image with AI editing using fal.ai
        try:
            fal_service = get_fal_service()
            ai_result = fal_service.edit_image(
                prompt=prompt,
                image_data=image_data,
                filename=filename,
                image_size=image_size,
                output_format=output_format,
                enable_prompt_expansion=enable_prompt_expansion,
                seed=seed
            )

            # Extract the edited image URL
            edited_images = ai_result.get('images', [])
            edited_image_url = edited_images[0]['url'] if edited_images else None

            response = {
                'status': 'success',
                'message': 'Image uploaded and edited successfully',
                'original_filepath': filepath,
                'edited_image_url': edited_image_url,
                'edited_images': edited_images,
                'seed': ai_result.get('seed'),
                'prompt': prompt,
                'captured_data': request_data
            }

            return jsonify(response), 200

        except Exception as ai_error:
            logger.error(f"AI editing failed: {str(ai_error)}")
            # Still return success for upload, but indicate AI editing failed
            return jsonify({
                'status': 'partial_success',
                'message': 'Image uploaded but AI editing failed',
                'original_filepath': filepath,
                'error': str(ai_error),
                'captured_data': request_data
            }), 200

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


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


@app.route('/api/pinterest/login', methods=['POST'])
def pinterest_login():
    """
    Endpoint 6: Save Pinterest credentials for a user

    Request body:
    {
        "user_id": "unique_user_identifier",
        "pinterest_username": "pinterest_username",
        "pinterest_email": "user@example.com",
        "pinterest_password": "password"
    }
    """
    request_data = log_request('/api/pinterest/login')

    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['user_id', 'pinterest_username', 'pinterest_email', 'pinterest_password']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        user_id = data['user_id']
        pinterest_username = data['pinterest_username']
        pinterest_email = data['pinterest_email']
        pinterest_password = data['pinterest_password']

        # Save credentials to database
        result = save_pinterest_credentials(
            user_id=user_id,
            pinterest_username=pinterest_username,
            pinterest_email=pinterest_email,
            pinterest_password=pinterest_password
        )

        logger.info(f"Pinterest credentials saved for user {user_id}")

        return jsonify({
            'status': 'success',
            'message': 'Pinterest credentials saved successfully',
            'user_id': user_id,
            'pinterest_username': pinterest_username,
            'captured_data': request_data
        }), 200

    except Exception as e:
        logger.error(f"Error saving Pinterest credentials: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/pinterest/status', methods=['GET'])
def pinterest_status():
    """
    Endpoint 7: Check Pinterest connection status for a user

    Query parameters:
    - user_id: Your app's user ID

    Returns:
    - connected: User has valid Pinterest session
    - expired: User has credentials but session expired
    - disconnected: User has no Pinterest credentials
    """
    request_data = log_request('/api/pinterest/status')

    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'user_id query parameter is required'
            }), 400

        # Get Pinterest connection status
        connection_status = get_pinterest_status(user_id)

        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'pinterest_status': connection_status,
            'captured_data': request_data
        }), 200

    except Exception as e:
        logger.error(f"Error checking Pinterest status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/pinterest/boards', methods=['GET'])
def pinterest_boards():
    """
    Endpoint 8: Get all Pinterest mood boards for a user

    Query parameters:
    - user_id: Your app's user ID

    Returns list of boards with:
    - id: Board identifier
    - name: Board name (mood board name)
    - description: Board description
    - pin_count: Number of pins in the board
    - url: Pinterest URL to the board
    - image_thumbnail_url: Thumbnail image
    - privacy: Board privacy setting
    """
    request_data = log_request('/api/pinterest/boards')

    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'user_id query parameter is required'
            }), 400

        # Check if user has Pinterest credentials
        creds = get_pinterest_credentials(user_id)
        if not creds:
            return jsonify({
                'status': 'error',
                'message': 'No Pinterest account linked. Please login first.'
            }), 404

        # Initialize Pinterest service
        pinterest_service = PinterestService(user_id)

        # Get all boards
        boards = pinterest_service.get_boards()

        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'board_count': len(boards),
            'boards': boards,
            'captured_data': request_data
        }), 200

    except Exception as e:
        logger.error(f"Error fetching Pinterest boards: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'hint': 'You may need to re-authenticate with Pinterest. Check /api/pinterest/status'
        }), 500


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
            '/api/upload': {
                'methods': ['POST'],
                'description': 'Upload and AI-edit base64 encoded images using fal.ai',
                'payload_example': {
                    'image': 'base64_encoded_image_data',
                    'prompt': 'add a sunset background',
                    'filename': 'optional_filename.jpg',
                    'image_size': 'auto (optional)',
                    'output_format': 'png (optional)',
                    'enable_prompt_expansion': False,
                    'seed': 12345
                }
            },
            '/api/pinterest/login': {
                'methods': ['POST'],
                'description': 'Save Pinterest credentials for a user',
                'payload_example': {
                    'user_id': 'user123',
                    'pinterest_username': 'pinterest_username',
                    'pinterest_email': 'user@example.com',
                    'pinterest_password': 'password'
                }
            },
            '/api/pinterest/status': {
                'methods': ['GET'],
                'description': 'Check Pinterest connection status (connected/expired/disconnected)',
                'query_parameters': {
                    'user_id': 'Your app user ID'
                },
                'example': '/api/pinterest/status?user_id=user123'
            },
            '/api/pinterest/boards': {
                'methods': ['GET'],
                'description': 'Get all Pinterest mood boards for a user',
                'query_parameters': {
                    'user_id': 'Your app user ID'
                },
                'example': '/api/pinterest/boards?user_id=user123',
                'returns': 'List of boards with id, name, description, pin_count, url, etc.'
            },
            '/health': {
                'methods': ['GET'],
                'description': 'Health check endpoint'
            }
        }
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
