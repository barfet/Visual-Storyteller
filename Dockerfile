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

# Pre-download and cache the BLIP model
RUN python -c "from transformers import BlipProcessor, BlipForConditionalGeneration; \
    processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base'); \
    model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')"

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/sample_images data/audio \
    && chmod -R 777 data

# Set environment variables
ENV PYTHONPATH=/app
ENV UPLOAD_DIR=/app/data/sample_images
ENV AUDIO_DIR=/app/data/audio
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 