# Multi-stage build for Saga Orchestrator
# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
        python3-dev \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY saga_orchestrator/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV DJANGO_SETTINGS_MODULE=saga_orchestrator_project.settings
ENV PATH="/root/.local/bin:$PATH"

# Set work directory
WORKDIR /app

# Install only runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy shared module first
COPY shared /app/shared

# Copy only necessary application files
COPY saga_orchestrator/saga_orchestrator_project/ /app/saga_orchestrator_project/
COPY saga_orchestrator/saga_orchestrator/ /app/saga_orchestrator/
COPY saga_orchestrator/sagas/ /app/sagas/
COPY saga_orchestrator/manage.py /app/
COPY saga_orchestrator/requirements.txt /app/

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8008

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8008/health/ || exit 1

# Run the application
CMD python manage.py migrate && python manage.py loaddata sagas/fixtures/initial_saga_definitions.json && gunicorn saga_orchestrator_project.wsgi:application --bind 0.0.0.0:8008 --workers 4 --worker-class sync --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100

