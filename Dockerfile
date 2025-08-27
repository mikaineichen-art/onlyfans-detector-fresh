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

# Make the start script executable
RUN chmod +x start.sh

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Railway provides PORT env var
ENV PORT=8080
EXPOSE 8080

# Start the server using the shell script
CMD ["./start.sh"]
