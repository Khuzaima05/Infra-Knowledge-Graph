#!/bin/bash

echo "🧹 Cleaning up Infra Knowledge Graph..."

# Stop containers
echo "Stopping containers..."
docker-compose down

# Remove volumes
echo "Removing volumes..."
docker-compose down -v

# Clean cloned repos
echo "Cleaning cloned repositories..."
rm -rf backend/cloned_repos/*

echo "✅ Cleanup complete!"
