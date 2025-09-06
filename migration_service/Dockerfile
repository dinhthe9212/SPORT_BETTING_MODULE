# Migration Service Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
        gcc \
        python3-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared module
COPY shared /app/shared

# Copy all service directories for migration
COPY betting_service /app/betting_service
COPY carousel_service /app/carousel_service
COPY individual_bookmaker_service /app/individual_bookmaker_service
COPY risk_management_service /app/risk_management_service
COPY saga_orchestrator /app/saga_orchestrator
COPY sports_data_service /app/sports_data_service

# Copy migration script
COPY scripts/migrate_all.py /app/migrate_all.py

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Default command
CMD ["python", "migrate_all.py"]
