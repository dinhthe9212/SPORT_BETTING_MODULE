#!/usr/bin/env python3
"""
Migration Service - Chạy migration cho tất cả services một cách an toàn
Sử dụng Redis lock để đảm bảo chỉ một instance chạy migration tại một thời điểm
"""

import os
import sys
import time
import logging
import subprocess
import redis
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
MIGRATION_LOCK_KEY = 'migration_lock'
MIGRATION_LOCK_TIMEOUT = 300  # 5 minutes

# Service configurations
SERVICES = [
    {
        'name': 'betting_service',
        'path': '/app/betting_service',
        'db_name': os.getenv('BETTING_DB_NAME', 'betting_db')
    },
    {
        'name': 'carousel_service', 
        'path': '/app/carousel_service',
        'db_name': os.getenv('CAROUSEL_DB_NAME', 'carousel_db')
    },
    {
        'name': 'individual_bookmaker_service',
        'path': '/app/individual_bookmaker_service', 
        'db_name': os.getenv('INDIVIDUAL_BOOKMAKER_DB_NAME', 'individual_bookmaker_db')
    },
    {
        'name': 'risk_management_service',
        'path': '/app/risk_management_service',
        'db_name': os.getenv('RISK_MANAGEMENT_DB_NAME', 'risk_management_db')
    },
    {
        'name': 'saga_orchestrator',
        'path': '/app/saga_orchestrator',
        'db_name': os.getenv('SAGA_DB_NAME', 'saga_db')
    },
    {
        'name': 'sports_data_service',
        'path': '/app/sports_data_service',
        'db_name': os.getenv('SPORTS_DATA_DB_NAME', 'sports_data_db')
    }
]

def get_redis_connection():
    """Tạo kết nối Redis"""
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        r.ping()
        return r
    except Exception as e:
        logger.error(f"Không thể kết nối Redis: {e}")
        return None

def acquire_migration_lock(redis_conn):
    """Lấy lock để chạy migration"""
    try:
        # Thử set lock với timeout
        result = redis_conn.set(
            MIGRATION_LOCK_KEY, 
            f"migration_{int(time.time())}", 
            nx=True,  # Chỉ set nếu key chưa tồn tại
            ex=MIGRATION_LOCK_TIMEOUT  # Tự động expire sau 5 phút
        )
        return result
    except Exception as e:
        logger.error(f"Lỗi khi lấy migration lock: {e}")
        return False

def release_migration_lock(redis_conn):
    """Giải phóng migration lock"""
    try:
        redis_conn.delete(MIGRATION_LOCK_KEY)
        logger.info("Đã giải phóng migration lock")
    except Exception as e:
        logger.error(f"Lỗi khi giải phóng migration lock: {e}")

def wait_for_database():
    """Chờ database sẵn sàng"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Test PostgreSQL connection
            result = subprocess.run([
                'pg_isready', 
                '-h', os.getenv('DB_HOST', 'postgres'),
                '-p', os.getenv('DB_PORT', '5432'),
                '-U', os.getenv('DB_USER', 'postgres')
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Database đã sẵn sàng")
                return True
                
        except Exception as e:
            logger.warning(f"Database chưa sẵn sàng: {e}")
            
        retry_count += 1
        time.sleep(2)
        
    logger.error("Database không sẵn sàng sau 60 giây")
    return False

def run_migration_for_service(service):
    """Chạy migration cho một service"""
    service_name = service['name']
    service_path = service['path']
    
    logger.info(f"Bắt đầu migration cho {service_name}")
    
    try:
        # Chuyển đến thư mục service
        os.chdir(service_path)
        
        # Chạy migration
        result = subprocess.run([
            'python', 'manage.py', 'migrate', '--no-input'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info(f"Migration thành công cho {service_name}")
            return True
        else:
            logger.error(f"Migration thất bại cho {service_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Migration timeout cho {service_name}")
        return False
    except Exception as e:
        logger.error(f"Lỗi khi migration {service_name}: {e}")
        return False
    finally:
        # Quay lại thư mục gốc
        os.chdir('/app')

def main():
    """Hàm chính"""
    logger.info("=== BẮT ĐẦU MIGRATION SERVICE ===")
    
    # Chờ database sẵn sàng
    if not wait_for_database():
        logger.error("Database không sẵn sàng, thoát")
        sys.exit(1)
    
    # Kết nối Redis
    redis_conn = get_redis_connection()
    if not redis_conn:
        logger.error("Không thể kết nối Redis, thoát")
        sys.exit(1)
    
    # Thử lấy migration lock
    if not acquire_migration_lock(redis_conn):
        logger.info("Migration đang được chạy bởi instance khác, chờ đợi...")
        
        # Chờ lock được giải phóng
        while True:
            time.sleep(5)
            if acquire_migration_lock(redis_conn):
                break
            logger.info("Vẫn chờ migration lock...")
    
    logger.info("Đã lấy được migration lock, bắt đầu migration")
    
    try:
        # Chạy migration cho từng service
        success_count = 0
        total_services = len(SERVICES)
        
        for service in SERVICES:
            if run_migration_for_service(service):
                success_count += 1
            else:
                logger.error(f"Migration thất bại cho {service['name']}")
        
        logger.info(f"Hoàn thành migration: {success_count}/{total_services} services thành công")
        
        if success_count == total_services:
            logger.info("=== MIGRATION HOÀN THÀNH THÀNH CÔNG ===")
            sys.exit(0)
        else:
            logger.error("=== MIGRATION HOÀN THÀNH VỚI LỖI ===")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {e}")
        sys.exit(1)
    finally:
        # Giải phóng lock
        release_migration_lock(redis_conn)

if __name__ == '__main__':
    main()
