#!/bin/bash

echo "🚀 Starting OnlyFans Detector..."

# Install Playwright browsers if not already installed
echo "📦 Installing Playwright browsers..."
python -m playwright install chromium

# Install system dependencies if needed
echo "🔧 Installing system dependencies..."
python -m playwright install-deps

# Start the application
echo "🌐 Starting Flask application..."
exec gunicorn --bind 0.0.0.0:$PORT api_server:app
