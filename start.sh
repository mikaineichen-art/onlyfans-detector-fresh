#!/bin/bash

# Get PORT from environment or default to 8080
PORT=${PORT:-8080}

echo "Starting application on port $PORT"
echo "Current working directory: $(pwd)"
echo "Files in current directory: $(ls -la)"

# Test if we can import the simple test app
echo "Testing simple app import..."
python3 -c "from test_app import app; print('Simple app import successful')" || {
    echo "Simple app import failed, checking what's available..."
    python3 -c "import sys; print('Python path:', sys.path)"
    python3 -c "import os; print('Current directory:', os.getcwd())"
    echo "Trying to start simple test app instead..."
    exec gunicorn test_app:app --bind 0.0.0.0:$PORT --log-level debug --timeout 120
}

echo "Testing complex app import..."
python3 -c "from api_server import app; print('Complex app import successful')" || {
    echo "Complex app import failed, starting simple test app instead..."
    exec gunicorn test_app:app --bind 0.0.0.0:$PORT --log-level debug --timeout 120
}

echo "Starting complex app with gunicorn..."
# Start the server
exec gunicorn api_server:app --bind 0.0.0.0:$PORT --log-level debug --timeout 120
