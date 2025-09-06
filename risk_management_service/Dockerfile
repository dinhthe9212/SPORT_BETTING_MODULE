FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY risk_management_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module first
COPY shared /app/shared

# Copy project
COPY risk_management_service/ /app/

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8003

# Run the application
CMD ["gunicorn", "risk_management_service_project.wsgi:application", "--bind", "0.0.0.0:8003", "--workers", "4", "--worker-class", "sync", "--timeout", "120", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "100"]