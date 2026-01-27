FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories for uploads and downloads
RUN mkdir -p /app/uploads /app/downloads

# Expose ports
# 5000 for Flask web server
# 8000 for WebSocket server
EXPOSE 5000 8000

# Default command: run Flask web server
CMD ["python", "web_server.py"]
