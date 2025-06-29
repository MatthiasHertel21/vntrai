#!/bin/bash

echo "🔄 Upgrading Dependencies for Implementation Modules..."
echo "This will rebuild the Docker container with all required libraries."
echo

# Stop running container
echo "⏹️  Stopping existing containers..."
sudo docker-compose down

# Remove old images to force rebuild
echo "🗑️  Removing old images..."
sudo docker image prune -f

# Rebuild with new requirements
echo "🔨 Building with new requirements..."
sudo docker-compose build --no-cache

# Start the application
echo "🚀 Starting application..."
sudo docker-compose up -d

echo
echo "✅ Upgrade complete!"
echo "📊 Checking container status..."
sudo docker-compose ps

echo
echo "📝 Available Implementation Modules after upgrade:"
echo "  - OpenAI ChatCompletion (requires: openai, aiohttp)"
echo "  - Google Sheets (requires: google-api-python-client, google-auth)"
echo "  - Future modules: Slack, Email, Database, File Processing"
echo
echo "🌐 Application should be available at: http://localhost:5004"
