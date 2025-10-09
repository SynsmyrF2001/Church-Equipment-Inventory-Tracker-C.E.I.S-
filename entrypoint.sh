#!/bin/bash
set -e

echo "🚀 Church Equipment Inventory System - Starting..."

# Wait for database to be ready
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "⏳ Waiting for PostgreSQL to be ready..."
    
    # Extract database connection details
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    # Wait for PostgreSQL to be ready (max 30 seconds)
    timeout=30
    while ! pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -q 2>/dev/null; do
        timeout=$((timeout - 1))
        if [ $timeout -le 0 ]; then
            echo "❌ Timeout waiting for PostgreSQL"
            exit 1
        fi
        echo "⏳ PostgreSQL is unavailable - sleeping (${timeout}s remaining)"
        sleep 1
    done
    
    echo "✅ PostgreSQL is ready!"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 << END
from app import app, db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    with app.app_context():
        # Create all tables
        db.create_all()
        logger.info("✅ Database tables created successfully")
except Exception as e:
    logger.error(f"❌ Database initialization failed: {e}")
    exit(1)
END

if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed"
    exit 1
fi

echo "✅ Database initialized successfully"

# Check if we should run migrations (for future use)
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "🔄 Running database migrations..."
    # flask db upgrade
fi

echo "🎉 Startup complete! Starting application..."
echo "📱 Application will be available at: http://localhost:${PORT:-5000}"

# Execute the main command
exec "$@"

