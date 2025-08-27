#!/bin/bash

# Get PORT from environment or default to 8080
PORT=${PORT:-8080}

echo "Starting application on port $PORT"

# Start the server
exec gunicorn api_server:app --bind 0.0.0.0:$PORT --log-level info
