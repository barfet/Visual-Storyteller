FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set up model cache directory and environment variable
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
RUN mkdir -p /app/.cache/huggingface

# Pre-download and cache the BLIP model, then clean up unnecessary files
RUN python -c "from transformers import BlipProcessor, BlipForConditionalGeneration; \
    processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base'); \
    model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')" \
    && find /app/.cache/huggingface -type f -not -name "*.bin" -not -name "*.json" -delete \
    && rm -rf /root/.cache/huggingface

# Copy the rest of the application
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p data/sample_images data/audio \
    && chmod -R 777 data \
    && chmod -R 777 /app/.cache

# Set environment variables
ENV PYTHONPATH=/app
ENV UPLOAD_DIR=/app/data/sample_images
ENV AUDIO_DIR=/app/data/audio

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 