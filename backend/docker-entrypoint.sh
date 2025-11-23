#!/bin/bash
set -e

echo "Starting application..."

# Run database migrations
echo "Running database migrations..."
python init_db.py

# Start the application
echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
