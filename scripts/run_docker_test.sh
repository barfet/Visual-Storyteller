#!/bin/bash

# Stop and remove any existing container
docker stop visual-storyteller-test 2>/dev/null || true
docker rm visual-storyteller-test 2>/dev/null || true

# Build the Docker image
echo "Building Docker image..."
docker build -t visual-storyteller-test .

# Run the container
echo "Starting container..."
docker run -d \
    --name visual-storyteller-test \
    -p 8000:8000 \
    -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
    -e UPLOAD_DIR=/app/data/sample_images \
    -e AUDIO_DIR=/app/data/audio \
    visual-storyteller-test

# Wait for the service to be ready
echo "Waiting for service to be ready..."
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo "Service is ready!"
        exit 0
    fi
    echo "Attempt $attempt/$max_attempts: Service not ready yet..."
    sleep 2
    attempt=$((attempt + 1))
done

echo "Service failed to start within timeout"
docker logs visual-storyteller-test
docker stop visual-storyteller-test
exit 1 