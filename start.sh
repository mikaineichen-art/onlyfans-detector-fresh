#!/bin/bash

# Get PORT from environment or default to 8080
PORT=${PORT:-8080}

echo "Starting application on port $PORT"
echo "Current working directory: $(pwd)"
echo "Files in current directory: $(ls -la)"

# Test if we can import the app
echo "Testing app import..."
python3 -c "from api_server import app; print('Import successful')" || {
    echo "Import failed, checking what's available..."
    python3 -c "import sys; print('Python path:', sys.path)"
    python3 -c "import os; print('Current directory:', os.getcwd())"
    exit 1
}

echo "Starting gunicorn server..."
# Start the server
exec gunicorn api_server:app --bind 0.0.0.0:$PORT --log-level debug --timeout 120
