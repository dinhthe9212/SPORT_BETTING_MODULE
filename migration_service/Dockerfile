# Multi-stage build for Migration Service
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

# Copy requirements from all services and install Python dependencies
COPY betting_service/requirements.txt /app/betting_requirements.txt
COPY carousel_service/requirements.production.txt /app/carousel_requirements.txt
COPY individual_bookmaker_service/requirements.txt /app/individual_bookmaker_requirements.txt
COPY risk_management_service/requirements.txt /app/risk_management_requirements.txt
COPY saga_orchestrator/requirements.txt /app/saga_requirements.txt
COPY sports_data_service/requirements.txt /app/sports_data_requirements.txt

# Install all dependencies
RUN pip install --no-cache-dir --user -r betting_requirements.txt \
    && pip install --no-cache-dir --user -r carousel_requirements.txt \
    && pip install --no-cache-dir --user -r individual_bookmaker_requirements.txt \
    && pip install --no-cache-dir --user -r risk_management_requirements.txt \
    && pip install --no-cache-dir --user -r saga_requirements.txt \
    && pip install --no-cache-dir --user -r sports_data_requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
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

# Copy shared module
COPY shared /app/shared

# Copy only necessary service files for migration
COPY betting_service/betting_service_project/ /app/betting_service/betting_service_project/
COPY betting_service/betting/ /app/betting_service/betting/
COPY betting_service/manage.py /app/betting_service/

COPY carousel_service/carousel_service_project/ /app/carousel_service/carousel_service_project/
COPY carousel_service/carousel/ /app/carousel_service/carousel/
COPY carousel_service/manage.py /app/carousel_service/

COPY individual_bookmaker_service/individual_bookmaker_service/ /app/individual_bookmaker_service/individual_bookmaker_service/
COPY individual_bookmaker_service/individual_bookmaker/ /app/individual_bookmaker_service/individual_bookmaker/
COPY individual_bookmaker_service/manage.py /app/individual_bookmaker_service/

COPY risk_management_service/risk_management_service_project/ /app/risk_management_service/risk_management_service_project/
COPY risk_management_service/risk_manager/ /app/risk_management_service/risk_manager/
COPY risk_management_service/manage.py /app/risk_management_service/

COPY saga_orchestrator/saga_orchestrator_project/ /app/saga_orchestrator/saga_orchestrator_project/
COPY saga_orchestrator/saga_orchestrator/ /app/saga_orchestrator/saga_orchestrator/
COPY saga_orchestrator/sagas/ /app/saga_orchestrator/sagas/
COPY saga_orchestrator/manage.py /app/saga_orchestrator/

COPY sports_data_service/sports_data_service_project/ /app/sports_data_service/sports_data_service_project/
COPY sports_data_service/sports_data/ /app/sports_data_service/sports_data/
COPY sports_data_service/manage.py /app/sports_data_service/

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
