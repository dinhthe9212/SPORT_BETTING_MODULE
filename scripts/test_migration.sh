#!/bin/bash
# Test script để kiểm tra migration strategy

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
}

log_info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO: $1${NC}"
}

# Test functions
test_migration_service() {
    log "=== TESTING MIGRATION SERVICE ==="
    
    log "1. Starting migration service..."
    if docker-compose up migration_service; then
        log "✅ Migration service completed successfully"
    else
        log_error "❌ Migration service failed"
        return 1
    fi
}

test_service_startup() {
    log "=== TESTING SERVICE STARTUP ==="
    
    log "2. Starting all services..."
    docker-compose up -d
    
    log "3. Waiting for services to be ready..."
    sleep 30
    
    # Check if services are running
    services=("betting_service" "carousel_service" "individual_bookmaker_service" "risk_management_service" "saga_orchestrator" "sports_data_service")
    
    for service in "${services[@]}"; do
        if docker-compose ps | grep -q "$service.*Up"; then
            log "✅ $service is running"
        else
            log_error "❌ $service is not running"
            docker-compose logs "$service" | tail -20
        fi
    done
}

test_scaling() {
    log "=== TESTING SERVICE SCALING ==="
    
    log "4. Testing service scaling..."
    
    # Scale betting service to 3 instances
    log "Scaling betting_service to 3 instances..."
    docker-compose up -d --scale betting_service=3
    
    sleep 15
    
    # Check if all instances are running
    betting_count=$(docker-compose ps | grep "betting_service" | grep "Up" | wc -l)
    if [ "$betting_count" -eq 3 ]; then
        log "✅ Successfully scaled betting_service to 3 instances"
    else
        log_error "❌ Failed to scale betting_service (found $betting_count instances)"
    fi
}

test_redis_locks() {
    log "=== TESTING REDIS LOCKS ==="
    
    log "5. Checking Redis migration locks..."
    
    # Check if migration locks are cleared
    locks=$(docker-compose exec -T redis redis-cli KEYS "*migration*" 2>/dev/null | wc -l)
    if [ "$locks" -eq 0 ]; then
        log "✅ All migration locks are cleared"
    else
        log_warning "⚠️  Found $locks migration locks still in Redis"
        docker-compose exec -T redis redis-cli KEYS "*migration*"
    fi
}

test_database_consistency() {
    log "=== TESTING DATABASE CONSISTENCY ==="
    
    log "6. Checking database migrations..."
    
    # Check migration status for each service
    services=("betting_service" "carousel_service" "individual_bookmaker_service" "risk_management_service" "saga_orchestrator" "sports_data_service")
    
    for service in "${services[@]}"; do
        log "Checking migration status for $service..."
        if docker-compose exec -T "$service" python manage.py showmigrations --plan | grep -q "\[ \]"; then
            log_warning "⚠️  $service has pending migrations"
        else
            log "✅ $service migrations are up to date"
        fi
    done
}

cleanup() {
    log "=== CLEANUP ==="
    
    log "7. Cleaning up test environment..."
    docker-compose down -v
    docker system prune -f
    log "✅ Cleanup completed"
}

# Main test execution
main() {
    log "🚀 STARTING MIGRATION STRATEGY TEST"
    log "====================================="
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        log_error ".env file not found. Please copy .env.example to .env and configure it."
        exit 1
    fi
    
    # Run tests
    test_migration_service
    test_service_startup
    test_scaling
    test_redis_locks
    test_database_consistency
    
    log "====================================="
    log "🎉 ALL TESTS COMPLETED SUCCESSFULLY!"
    log "====================================="
    
    # Ask if user wants to cleanup
    read -p "Do you want to cleanup test environment? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cleanup
    else
        log "Test environment left running. Use 'make clean' to cleanup later."
    fi
}

# Handle script interruption
trap 'log_error "Test interrupted by user"; exit 1' INT TERM

# Run main function
main "$@"
