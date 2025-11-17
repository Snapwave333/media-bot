# Backend Dockerfile
FROM python:3.11-slim

# Install system dependencies for librosa and MoviePy
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/outputs /app/temp

# Run the application
CMD ["python", "run.py"]
