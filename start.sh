#!/bin/bash

echo "🚀 Starting OnlyFans Detector..."

# Set default PORT if not provided by Railway
if [ -z "$PORT" ]; then
    export PORT=5000
    echo "⚠️  PORT not set, using default: $PORT"
else
    echo "✅ Using Railway PORT: $PORT"
fi

# Try to install Playwright browsers (optional - won't crash if it fails)
echo "📦 Attempting to install Playwright browsers..."
if python -m playwright install chromium; then
    echo "✅ Playwright browsers installed successfully"
else
    echo "⚠️  Playwright browser installation failed - continuing without it"
fi

# Try to install system dependencies (optional - won't crash if it fails)
echo "🔧 Attempting to install system dependencies..."
if python -m playwright install-deps; then
    echo "✅ System dependencies installed successfully"
else
    echo "⚠️  System dependency installation failed - continuing without it"
fi

# Start the application with proper Railway configuration
echo "🌐 Starting Flask application on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 --worker-class sync --max-requests 1000 --max-requests-jitter 100 api_server:app
