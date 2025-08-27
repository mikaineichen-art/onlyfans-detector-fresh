# Use official Playwright image with all browser dependencies preinstalled
# Railway deployment - Aug 27 2025 - Fixed PORT issue
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements and install first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install chromium

# Copy the rest of the app
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port 8080 - Fixed for Railway
EXPOSE 8080

# Start the server with explicit port handling - No more $PORT issues
CMD gunicorn api_server:app --bind 0.0.0.0:8080
