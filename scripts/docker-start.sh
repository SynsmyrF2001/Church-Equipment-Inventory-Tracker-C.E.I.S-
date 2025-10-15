#!/bin/bash

# Church Equipment Inventory System - Docker Quick Start
# This script helps you run the application with Docker on your laptop

set -e

echo "🐳 Church Equipment Inventory System - Docker Quick Start"
echo "=========================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop from:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is installed and running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it or use Docker Desktop."
    exit 1
fi

echo "✅ docker-compose is available"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    
    # Generate a secure session secret
    SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))' 2>/dev/null || openssl rand -hex 32)
    
    cat > .env << EOF
# Church Equipment Inventory System - Docker Configuration
# Generated on $(date)

# Security
SESSION_SECRET=${SESSION_SECRET}

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://church_admin:CHANGE_THIS_PASSWORD_IN_PRODUCTION@db:5432/church_inventory
POSTGRES_DB=church_inventory
POSTGRES_USER=church_admin
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD_IN_PRODUCTION

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True

# Application Settings
PORT=5000
MAX_CONTENT_LENGTH=16777216

# Optional: Twilio (leave empty if not using)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
EOF
    echo "✅ Created .env file with secure session secret"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🔨 Building Docker images..."
docker-compose -f docker/docker-compose.yml build

echo ""
echo "🚀 Starting services..."
echo "   - PostgreSQL Database"
echo "   - Flask Web Application"
echo ""

# Start docker-compose
docker-compose -f docker/docker-compose.yml up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker-compose -f docker/docker-compose.yml ps | grep -q "Up"; then
    echo ""
    echo "🎉 Success! Your application is now running!"
    echo ""
    echo "📱 Access the application:"
    echo "   🌐 Web Interface: http://localhost:8080"
    echo "   🗄️  Database: localhost:5433"
    echo ""
    echo "💡 Note: Using port 8080 (port 5000 is used by macOS AirPlay)"
    echo ""
    echo "📊 Useful commands:"
    echo "   View logs:          docker-compose -f docker/docker-compose.yml logs -f"
    echo "   Stop application:   docker-compose -f docker/docker-compose.yml down"
    echo "   Restart:            docker-compose -f docker/docker-compose.yml restart"
    echo "   Check status:       docker-compose -f docker/docker-compose.yml ps"
    echo ""
    echo "📖 For more information, see DOCKER.md"
    echo ""
    
    # Try to open browser (macOS/Linux)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🌐 Opening browser..."
        sleep 2
        open http://localhost:8080 2>/dev/null || true
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:8080 2>/dev/null || true
        fi
    fi
    
else
    echo "❌ Something went wrong. Check the logs with: docker-compose -f docker/docker-compose.yml logs"
    exit 1
fi

