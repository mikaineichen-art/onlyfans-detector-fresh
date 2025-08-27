#!/bin/bash

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install chromium

# Start the application with proper port handling
echo "Starting application on port ${PORT:-8080}..."
gunicorn api_server:app --bind 0.0.0.0:${PORT:-8080} --timeout 120 --workers 1
