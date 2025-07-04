#!/bin/bash
"""
Run the streaming API test with Docker
Usage: ./run_test_docker.sh
"""

echo "Running streaming API fixes test in Docker container..."
echo "=================================================="

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not available"
    exit 1
fi

# Check if the web_1 container is running
if ! docker ps | grep -q "web_1"; then
    echo "Error: web_1 container is not running"
    echo "Please start the application with: docker-compose up"
    exit 1
fi

# Run the test in the container
sudo docker exec web_1 python test_streaming_fixes.py

# Capture the exit code
exit_code=$?

echo "=================================================="
if [ $exit_code -eq 0 ]; then
    echo "✅ All tests passed! The streaming API fixes should work correctly."
else
    echo "❌ Some tests failed. Check the output above for details."
fi

exit $exit_code
