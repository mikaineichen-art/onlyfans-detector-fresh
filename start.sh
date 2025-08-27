#!/bin/bash

echo "🚀 Starting OnlyFans Detector..."

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

# Start the application (this will work with or without Playwright)
echo "🌐 Starting Flask application..."
exec gunicorn --bind 0.0.0.0:$PORT api_server:app
