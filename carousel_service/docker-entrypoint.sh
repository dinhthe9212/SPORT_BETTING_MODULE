#!/bin/bash
# Production entrypoint script for Django services
# Cost: $0 (Shell script)

set -e

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! python -c "
import psycopg2
import os
import sys
try:
    conn = psycopg2.connect(
        host=os.environ.get('DATABASE_HOST', 'postgres'),
        port=os.environ.get('DATABASE_PORT', '5432'),
        user=os.environ.get('POSTGRES_USER', 'postgres'),
        password=os.environ.get('POSTGRES_PASSWORD', 'securepassword'),
        dbname=os.environ.get('POSTGRES_DB', 'betting_platform')
    )
    conn.close()
    print('Database is ready!')
except psycopg2.OperationalError:
    print('Database is not ready yet...')
    sys.exit(1)
"; do
    echo "Database is unavailable - sleeping"
    sleep 2
done

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
while ! python -c "
import redis
import os
import sys
try:
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST', 'redis'),
        port=int(os.environ.get('REDIS_PORT', '6379')),
        db=0
    )
    r.ping()
    print('Redis is ready!')
except redis.ConnectionError:
    print('Redis is not ready yet...')
    sys.exit(1)
"; do
    echo "Redis is unavailable - sleeping"
    sleep 2
done

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"

# Load initial data (if any)
if [ -f "fixtures/initial_data.json" ]; then
    echo "Loading initial data..."
    python manage.py loaddata fixtures/initial_data.json
fi

# Warm up cache
echo "Warming up cache..."
python -c "
from carousel.optimizations import CacheOptimizer
try:
    CacheOptimizer.warm_cache_for_popular_items()
    print('Cache warmed up successfully')
except Exception as e:
    print(f'Cache warm-up failed: {e}')
"

# Start the application
echo "Starting Django application..."
if [ "$DEBUG" = "True" ]; then
    echo "Running in development mode"
    exec python manage.py runserver 0.0.0.0:8001
else
    echo "Running in production mode with Gunicorn"
    exec gunicorn \
        --bind 0.0.0.0:8001 \
        --workers 4 \
        --worker-class gevent \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 30 \
        --keep-alive 2 \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        carousel_service_project.wsgi:application
fi
