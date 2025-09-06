#!/bin/bash

# Build Production Images Script
# Tạo các Docker images production-ready cho tất cả services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VERSION=${1:-"v1.0.0"}
REGISTRY=${2:-""}  # Optional registry prefix

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Build function
build_service() {
    local service_name=$1
    local dockerfile_path=$2
    local image_name=$3
    
    log "Building $service_name..."
    
    if [ -f "$dockerfile_path" ]; then
        docker build -t "$image_name:$VERSION" -f "$dockerfile_path" .
        if [ $? -eq 0 ]; then
            log "✅ Successfully built $image_name:$VERSION"
        else
            log_error "❌ Failed to build $image_name:$VERSION"
            return 1
        fi
    else
        log_error "❌ Dockerfile not found: $dockerfile_path"
        return 1
    fi
}

# Main execution
main() {
    log "=== BUILDING PRODUCTION IMAGES ==="
    log "Version: $VERSION"
    log "Registry: ${REGISTRY:-'local'}"
    log ""
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Build all services
    log_info "Building all microservices..."
    
    # Betting Service
    build_service "Betting Service" "betting_service/Dockerfile" "${REGISTRY}test-betting-service"
    
    # Carousel Service
    build_service "Carousel Service" "carousel_service/Dockerfile" "${REGISTRY}test-carousel-service"
    
    # Individual Bookmaker Service
    build_service "Individual Bookmaker Service" "individual_bookmaker_service/Dockerfile" "${REGISTRY}individual-bookmaker-service"
    
    # Risk Management Service
    build_service "Risk Management Service" "risk_management_service/Dockerfile" "${REGISTRY}test-risk-management-service"
    
    # Saga Orchestrator
    build_service "Saga Orchestrator" "saga_orchestrator/Dockerfile" "${REGISTRY}saga-orchestrator"
    
    # Sports Data Service
    build_service "Sports Data Service" "sports_data_service/Dockerfile" "${REGISTRY}sports-data-service"
    
    log ""
    log "=== BUILD COMPLETED ==="
    log "All production images have been built successfully!"
    log ""
    log "To run with production configuration:"
    log "  docker-compose -f docker-compose.production.yml up -d"
    log ""
    log "To push images to registry:"
    log "  docker push ${REGISTRY}test-betting-service:$VERSION"
    log "  docker push ${REGISTRY}test-carousel-service:$VERSION"
    log "  docker push ${REGISTRY}individual-bookmaker-service:$VERSION"
    log "  docker push ${REGISTRY}test-risk-management-service:$VERSION"
    log "  docker push ${REGISTRY}saga-orchestrator:$VERSION"
    log "  docker push ${REGISTRY}sports-data-service:$VERSION"
}

# Show usage
show_usage() {
    echo "Usage: $0 [VERSION] [REGISTRY]"
    echo ""
    echo "Arguments:"
    echo "  VERSION    Version tag for images (default: v1.0.0)"
    echo "  REGISTRY   Registry prefix (optional, e.g., 'myregistry.com/')"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Build with v1.0.0"
    echo "  $0 v1.2.3                           # Build with v1.2.3"
    echo "  $0 v1.2.3 myregistry.com/           # Build and tag for registry"
}

# Check arguments
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_usage
    exit 0
fi

# Run main function
main "$@"
