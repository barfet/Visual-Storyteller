#!/bin/bash

# Ensure scripts are executable
chmod +x scripts/run_docker_test.sh

# Start the Docker container
./scripts/run_docker_test.sh

# Check if container started successfully
if [ $? -ne 0 ]; then
    echo "Failed to start Docker container"
    exit 1
fi

# Run the E2E tests
echo "Running E2E tests..."
python tests/run_tests.py --stage e2e

# Store test result
TEST_RESULT=$?

# Stop and remove the container
echo "Cleaning up..."
docker stop visual-storyteller-test
docker rm visual-storyteller-test

# Exit with test result
exit $TEST_RESULT 