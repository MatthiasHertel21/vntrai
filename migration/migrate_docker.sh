#!/bin/bash
# Docker-based Migration Script
# Alternative zum direkten python3-Aufruf

echo "Starting v036 Data Migration via Docker..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please use: python3 migration/migrate_v036_data.py"
    exit 1
fi

# Build a temporary Python container and run migration
docker run --rm \
    -v "$(pwd)":/workspace \
    -w /workspace \
    python:3.11-slim \
    python3 migration/migrate_v036_data.py

echo "Migration completed via Docker!"
