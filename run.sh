#!/bin/bash
# Run Teveclub Django application in background

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/venv"
DJANGO_DIR="$APP_DIR/django"
PID_FILE="$APP_DIR/logs/gunicorn.pid"

echo "==================================="
echo "Starting Teveclub Django"
echo "==================================="

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Error: Application is already running (PID: $PID)"
        echo "Use ./stop.sh to stop it first, or ./restart.sh to restart"
        exit 1
    else
        echo "Removing stale PID file..."
        rm -f "$PID_FILE"
    fi
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found. Run ./env.sh first."
    exit 1
fi

# Create logs directory
mkdir -p "$APP_DIR/logs"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check if Gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing Gunicorn..."
    pip install gunicorn
fi

# Change to Django directory
cd "$DJANGO_DIR"

# Add Django directory to Python path
export PYTHONPATH="$DJANGO_DIR:$PYTHONPATH"

# Start Gunicorn in background
echo "Starting Gunicorn..."
gunicorn teveclub_project.wsgi:application \
    --bind 0.0.0.0:3000 \
    --workers 3 \
    --timeout 60 \
    --access-logfile "$APP_DIR/logs/access.log" \
    --error-logfile "$APP_DIR/logs/error.log" \
    --log-level info \
    --daemon \
    --pid "$PID_FILE"

# Wait a moment for startup
sleep 2

# Check if started successfully
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo ""
        echo "✓ Teveclub Django started successfully!"
        echo "  PID: $PID"
        echo "  URL: http://localhost:3000"
        echo ""
        echo "Logs:"
        echo "  Access: $APP_DIR/logs/access.log"
        echo "  Error:  $APP_DIR/logs/error.log"
        echo ""
        echo "Use ./status.sh to check status"
        echo "Use ./stop.sh to stop the application"
    else
        echo "✗ Failed to start. Check error logs:"
        echo "  $APP_DIR/logs/error.log"
        exit 1
    fi
else
    echo "✗ Failed to start. PID file not created."
    echo "Check error logs: $APP_DIR/logs/error.log"
    exit 1
fi

echo "==================================="
