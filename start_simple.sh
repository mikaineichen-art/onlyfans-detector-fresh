#!/bin/bash

echo "🚀 Starting OnlyFans Detector (Simple Mode)..."

# Set default PORT if not provided by Railway
if [ -z "$PORT" ]; then
    export PORT=5000
    echo "⚠️  PORT not set, using default: $PORT"
else
    echo "✅ Using Railway PORT: $PORT"
fi

# Start the application with minimal configuration
echo "🌐 Starting Flask application on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --timeout 60 --workers 1 api_server:app
