# Use official Playwright image with all browser dependencies preinstalled
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

# Railway provides PORT env var
ENV PORT=8080
EXPOSE 8080

# Start the server
CMD ["gunicorn", "api_server:app", "--bind", "0.0.0.0:${PORT}"]

