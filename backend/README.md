# Flask Request Capture API

A Docker containerized Flask application with 4 sample endpoints designed to capture and log all incoming requests and payloads. Includes LangGraph and LangChain for AI/LLM capabilities.

## Features

- 4 different endpoint types for various use cases
- Comprehensive request logging (headers, payload, timestamp, etc.)
- Docker containerized with all dependencies
- LangGraph and LangChain integration ready
- Health check endpoint
- API documentation at root endpoint

## Prerequisites

- Docker
- Docker Compose (optional, but recommended)

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Stop the container
docker-compose down
```

### Using Docker directly

```bash
# Build the image
docker build -t flask-request-capture .

# Run the container
docker run -p 5000:5000 flask-request-capture

# Run in detached mode
docker run -d -p 5000:5000 --name flask-app flask-request-capture
```

## Available Endpoints

The API will be available at `http://localhost:5000`

### 1. Generic Webhook - `/api/webhook`
**Methods:** GET, POST

Accepts any data and logs all request information.

```bash
curl -X POST http://localhost:5000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "data": "sample"}'
```

### 2. Chat Endpoint - `/api/chat`
**Methods:** POST

Simulates a conversational interface with message echoing.

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "user123"}'
```

### 3. Data Processing - `/api/data`
**Methods:** POST, PUT

Processes and logs data payloads.

```bash
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -d '{"items": [1, 2, 3], "metadata": {"source": "test"}}'
```

### 4. Event Tracking - `/api/events/<event_type>`
**Methods:** POST

Dynamic endpoint for tracking different event types.

```bash
curl -X POST http://localhost:5000/api/events/user_signup \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user456", "email": "user@example.com"}'
```

### Health Check - `/health`
**Methods:** GET

```bash
curl http://localhost:5000/health
```

### API Documentation - `/`
**Methods:** GET

```bash
curl http://localhost:5000/
```

## Viewing Logs

All requests are logged with full details including headers, payloads, timestamps, and more.

```bash
# View logs (Docker Compose)
docker-compose logs -f

# View logs (Docker)
docker logs -f flask-app
```

## Development

The docker-compose setup includes volume mounting, so changes to `app.py` will be reflected immediately (with Flask debug mode).

## Project Structure

```
backend/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── .dockerignore         # Docker ignore patterns
└── README.md            # This file
```

## Production Deployment

For production, uncomment the gunicorn command in the Dockerfile:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

## Dependencies

- Flask 3.0.0
- LangGraph 0.2.45
- LangChain 0.3.7
- Gunicorn 21.2.0
- And more (see requirements.txt)
