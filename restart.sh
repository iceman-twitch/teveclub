#!/bin/bash
# Restart Teveclub Django application

echo "==================================="
echo "Restarting Teveclub Django"
echo "==================================="

# Stop the application
./stop.sh

# Wait a moment
sleep 2

# Start the application
./run.sh
