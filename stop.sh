#!/bin/bash
# Stop Teveclub Django application

PID_FILE="logs/gunicorn.pid"

echo "==================================="
echo "Stopping Teveclub Django"
echo "==================================="

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Application is not running (no PID file found)"
    exit 0
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p $PID > /dev/null 2>&1; then
    echo "Process $PID is not running"
    echo "Removing stale PID file..."
    rm -f "$PID_FILE"
    exit 0
fi

# Stop the process
echo "Stopping process $PID..."
kill -TERM $PID

# Wait for process to stop (max 10 seconds)
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✓ Process stopped successfully"
        rm -f "$PID_FILE"
        echo "==================================="
        exit 0
    fi
    sleep 1
done

# If still running, force kill
echo "Process did not stop gracefully, forcing..."
kill -9 $PID

sleep 1

if ! ps -p $PID > /dev/null 2>&1; then
    echo "✓ Process forcefully stopped"
    rm -f "$PID_FILE"
else
    echo "✗ Failed to stop process $PID"
    exit 1
fi

echo "==================================="
