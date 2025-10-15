#!/bin/bash

# Church Equipment Inventory System - Quick Start Script
# This script helps you get the application running quickly

set -e

echo "🚀 Church Equipment Inventory System - Quick Start"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION detected. Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv package manager..."
    uv sync
else
    echo "Using pip package manager..."
    pip install -r requirements.txt
fi

# Set up environment variables
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOF
SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:///church_inventory.db
FLASK_ENV=development
DEBUG=True
EOF
    echo "✅ Created .env file with secure session secret"
else
    echo "✅ .env file already exists"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from app import app, db; app.app_context().push(); db.create_all()" || {
    echo "❌ Failed to initialize database. Please check your configuration."
    exit 1
}

echo ""
echo "🎉 Setup complete! Starting the application..."
echo "📱 The application will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the application
python3 app.py 