#!/bin/bash

# Test script for issue 140 - Output field persistence
# This script runs the test inside the Docker container

echo "🐳 Testing Issue 140: Output Field Persistence in Docker"
echo "=========================================================="

# Get the container name/id
CONTAINER_NAME=$(docker ps --format "table {{.Names}}" | grep -E "(age|fb1)" | head -1)

if [ -z "$CONTAINER_NAME" ]; then
    echo "❌ No running Docker container found with 'age' or 'fb1' in the name"
    echo "Please make sure your Docker container is running:"
    echo "  docker-compose up -d"
    exit 1
fi

echo "📦 Found Docker container: $CONTAINER_NAME"
echo "🔧 Copying test script to container..."

# Copy the test script to the container
docker cp test_output_fields_docker.py $CONTAINER_NAME:/app/

if [ $? -ne 0 ]; then
    echo "❌ Failed to copy test script to container"
    exit 1
fi

echo "✅ Test script copied successfully"
echo "🚀 Running test in container..."
echo ""

# Run the test script inside the container
docker exec -it $CONTAINER_NAME python test_output_fields_docker.py

# Capture the exit code
TEST_EXIT_CODE=$?

echo ""
echo "🧹 Cleaning up test script from container..."
docker exec $CONTAINER_NAME rm -f /app/test_output_fields_docker.py

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests passed! Issue 140 is properly implemented."
else
    echo "❌ Tests failed. Please check the implementation."
fi

exit $TEST_EXIT_CODE
