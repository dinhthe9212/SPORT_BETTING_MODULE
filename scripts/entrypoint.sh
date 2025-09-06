#!/bin/bash
# Entrypoint script với cơ chế lock để tránh xung đột migration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME=${SERVICE_NAME:-"unknown"}
REDIS_HOST=${REDIS_HOST:-"redis"}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_DB=${REDIS_DB:-0}
MIGRATION_LOCK_KEY="migration_${SERVICE_NAME}_lock"
MIGRATION_LOCK_TIMEOUT=300
MAX_WAIT_TIME=600
WAIT_INTERVAL=5

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

# Check if Redis is available
check_redis() {
    log "Kiểm tra kết nối Redis..."
    for i in {1..30}; do
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" ping > /dev/null 2>&1; then
            log "Redis đã sẵn sàng"
            return 0
        fi
        log "Chờ Redis sẵn sàng... ($i/30)"
        sleep 2
    done
    log_error "Redis không sẵn sàng sau 60 giây"
    return 1
}

# Check if database is ready
check_database() {
    log "Kiểm tra kết nối database..."
    for i in {1..30}; do
        if pg_isready -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" > /dev/null 2>&1; then
            log "Database đã sẵn sàng"
            return 0
        fi
        log "Chờ database sẵn sàng... ($i/30)"
        sleep 2
    done
    log_error "Database không sẵn sàng sau 60 giây"
    return 1
}

# Acquire migration lock
acquire_migration_lock() {
    local lock_value="migration_${SERVICE_NAME}_$(date +%s)"
    
    # Try to acquire lock
    local result=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" \
        SET "$MIGRATION_LOCK_KEY" "$lock_value" NX EX "$MIGRATION_LOCK_TIMEOUT" 2>/dev/null)
    
    if [ "$result" = "OK" ]; then
        log "Đã lấy được migration lock cho $SERVICE_NAME"
        echo "$lock_value" > /tmp/migration_lock_value
        return 0
    else
        log_warning "Migration lock đã được sử dụng bởi instance khác"
        return 1
    fi
}

# Release migration lock
release_migration_lock() {
    if [ -f /tmp/migration_lock_value ]; then
        local lock_value=$(cat /tmp/migration_lock_value)
        local current_value=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" \
            GET "$MIGRATION_LOCK_KEY" 2>/dev/null)
        
        # Only release if we own the lock
        if [ "$current_value" = "$lock_value" ]; then
            redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" \
                DEL "$MIGRATION_LOCK_KEY" > /dev/null 2>&1
            log "Đã giải phóng migration lock cho $SERVICE_NAME"
        fi
        rm -f /tmp/migration_lock_value
    fi
}

# Wait for migration to complete
wait_for_migration() {
    log "Chờ migration hoàn thành..."
    local wait_time=0
    
    while [ $wait_time -lt $MAX_WAIT_TIME ]; do
        local lock_exists=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" \
            EXISTS "$MIGRATION_LOCK_KEY" 2>/dev/null)
        
        if [ "$lock_exists" = "0" ]; then
            log "Migration đã hoàn thành"
            return 0
        fi
        
        log "Vẫn chờ migration... (${wait_time}s/${MAX_WAIT_TIME}s)"
        sleep $WAIT_INTERVAL
        wait_time=$((wait_time + WAIT_INTERVAL))
    done
    
    log_error "Timeout chờ migration sau $MAX_WAIT_TIME giây"
    return 1
}

# Run migration
run_migration() {
    log "Bắt đầu chạy migration cho $SERVICE_NAME..."
    
    if python manage.py migrate --no-input; then
        log "Migration thành công cho $SERVICE_NAME"
        return 0
    else
        log_error "Migration thất bại cho $SERVICE_NAME"
        return 1
    fi
}

# Main execution
main() {
    log "=== BẮT ĐẦU ENTRYPOINT CHO $SERVICE_NAME ==="
    
    # Check dependencies
    if ! check_redis; then
        log_error "Không thể kết nối Redis"
        exit 1
    fi
    
    if ! check_database; then
        log_error "Không thể kết nối Database"
        exit 1
    fi
    
    # Try to acquire migration lock
    if acquire_migration_lock; then
        # We got the lock, run migration
        if run_migration; then
            log "Migration hoàn thành thành công"
        else
            log_error "Migration thất bại"
            exit 1
        fi
        # Release lock
        release_migration_lock
    else
        # Wait for migration to complete
        if wait_for_migration; then
            log "Migration đã được thực hiện bởi instance khác"
        else
            log_error "Timeout chờ migration"
            exit 1
        fi
    fi
    
    # Start the main application
    log "Khởi động $SERVICE_NAME..."
    exec "$@"
}

# Cleanup on exit
cleanup() {
    log "Dọn dẹp và thoát..."
    release_migration_lock
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Run main function
main "$@"
