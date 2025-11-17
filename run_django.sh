#!/bin/bash
# Script to run the Teveclub Django application
# Can be used for development or production (with Gunicorn)

set -e  # Exit on error

# Configuration
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/venv"
DJANGO_DIR="$APP_DIR/django"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found. Run env.sh first."
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Change to Django directory
cd "$DJANGO_DIR"

# Run mode: development or production
MODE="${1:-dev}"

if [ "$MODE" = "prod" ]; then
    echo "Starting Teveclub Django in PRODUCTION mode with Gunicorn..."
    
    # Check if Gunicorn is installed
    if ! command -v gunicorn &> /dev/null; then
        echo "Installing Gunicorn..."
        pip install gunicorn
    fi
    
    # Add Django directory to Python path
    export PYTHONPATH="$DJANGO_DIR:$PYTHONPATH"
    
    # Run with Gunicorn
    gunicorn teveclub_project.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --timeout 60 \
        --access-logfile ../logs/access.log \
        --error-logfile ../logs/error.log \
        --log-level info \
        --daemon
    
    echo "Gunicorn started successfully!"
    echo "Access logs: $APP_DIR/logs/access.log"
    echo "Error logs: $APP_DIR/logs/error.log"
    
elif [ "$MODE" = "dev" ]; then
    echo "Starting Teveclub Django in DEVELOPMENT mode..."
    export PYTHONPATH="$DJANGO_DIR:$PYTHONPATH"
    python manage.py runserver 0.0.0.0:8000
    
else
    echo "Usage: $0 [dev|prod]"
    echo "  dev  - Run Django development server (default)"
    echo "  prod - Run with Gunicorn for production"
    exit 1
fi
