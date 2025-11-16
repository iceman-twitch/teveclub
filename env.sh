#!/bin/bash
# Setup script for Teveclub Django application
# This script sets up the Python virtual environment and installs dependencies

set -e  # Exit on error

echo "==================================="
echo "Teveclub Django Setup Script"
echo "==================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found. Installing core dependencies..."
    pip install Django==4.2.7 beautifulsoup4==4.12.2 lxml==5.3.0 requests==2.31.0
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p static
mkdir -p staticfiles

# Set permissions
echo "Setting permissions..."
chmod +x manage.py
chmod +x env.sh
chmod +x run_django.sh

echo ""
echo "==================================="
echo "Setup completed successfully!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Configure your environment variables (copy .env.example to .env)"
echo "3. Run migrations: python manage.py migrate"
echo "4. Collect static files: python manage.py collectstatic --noinput"
echo "5. Run the development server: python manage.py runserver"
echo ""
echo "For production deployment, see AWS_SETUP.md"
echo "==================================="
