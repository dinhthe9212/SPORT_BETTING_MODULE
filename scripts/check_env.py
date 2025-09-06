#!/usr/bin/env python3
"""
Script kiểm tra biến môi trường cho SPORT_BETTING_MODULE
Sử dụng: python scripts/check_env.py
"""

import os
import sys
from pathlib import Path

# Thêm project root vào Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_env_file(env_path):
    """Load biến môi trường từ file .env"""
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

def check_required_vars():
    """Kiểm tra các biến môi trường bắt buộc"""
    required_vars = [
        'POSTGRES_DB',
        'POSTGRES_USER', 
        'POSTGRES_PASSWORD',
        'POSTGRES_HOST',
        'POSTGRES_PORT',
        'REDIS_HOST',
        'REDIS_PORT',
        'SECRET_KEY',
        'DEBUG',
        'ALLOWED_HOSTS'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

def check_sensitive_vars():
    """Kiểm tra các biến nhạy cảm có được thay đổi từ giá trị mặc định"""
    sensitive_vars = {
        'POSTGRES_PASSWORD': 'postgres123',
        'SECRET_KEY': 'your-super-secret-key-change-in-production-2024',
        'JWT_SECRET_KEY': 'your-super-secret-jwt-key-change-in-production-2024'
    }
    
    unchanged_vars = []
    for var, default_value in sensitive_vars.items():
        current_value = os.getenv(var)
        if current_value == default_value:
            unchanged_vars.append(var)
    
    return unchanged_vars

def check_service_databases():
    """Kiểm tra các database names cho từng service"""
    service_dbs = [
        'BETTING_DB_NAME',
        'CAROUSEL_DB_NAME', 
        'INDIVIDUAL_BOOKMAKER_DB_NAME',
        'RISK_MANAGEMENT_DB_NAME',
        'SAGA_DB_NAME',
        'SPORTS_DATA_DB_NAME'
    ]
    
    missing_dbs = []
    for db_var in service_dbs:
        if not os.getenv(db_var):
            missing_dbs.append(db_var)
    
    return missing_dbs

def check_redis_dbs():
    """Kiểm tra Redis database numbers"""
    redis_dbs = [
        'REDIS_DB_BETTING',
        'REDIS_DB_CAROUSEL',
        'REDIS_DB_INDIVIDUAL_BOOKMAKER', 
        'REDIS_DB_RISK_MANAGEMENT',
        'REDIS_DB_SAGA',
        'REDIS_DB_SPORTS_DATA'
    ]
    
    missing_redis_dbs = []
    for redis_db in redis_dbs:
        if not os.getenv(redis_db):
            missing_redis_dbs.append(redis_db)
    
    return missing_redis_dbs

def check_api_keys():
    """Kiểm tra API keys"""
    api_keys = [
        'API_SPORTS_KEY',
        'THE_ODDS_API_KEY',
        'OPENLIGADB_KEY',
        'THESPORTSDB_KEY'
    ]
    
    missing_keys = []
    for key in api_keys:
        value = os.getenv(key)
        if not value or value.startswith('your_') or value.endswith('_here'):
            missing_keys.append(key)
    
    return missing_keys

def main():
    """Main function"""
    print("🔧 KIỂM TRA BIẾN MÔI TRƯỜNG SPORT_BETTING_MODULE")
    print("=" * 60)
    
    # Load .env file nếu có
    env_file = project_root / '.env'
    if env_file.exists():
        print(f"✅ Tìm thấy file .env: {env_file}")
        env_vars = load_env_file(env_file)
        # Set environment variables
        for key, value in env_vars.items():
            os.environ[key] = value
    else:
        print(f"⚠️  Không tìm thấy file .env: {env_file}")
        print("   Hãy chạy: cp .env.example .env")
        return 1
    
    # Kiểm tra các biến bắt buộc
    print("\n📋 KIỂM TRA BIẾN BẮT BUỘC")
    print("-" * 30)
    missing_required = check_required_vars()
    if missing_required:
        print("❌ Thiếu các biến bắt buộc:")
        for var in missing_required:
            print(f"   - {var}")
    else:
        print("✅ Tất cả biến bắt buộc đã được thiết lập")
    
    # Kiểm tra biến nhạy cảm
    print("\n🔐 KIỂM TRA BIẾN NHẠY CẢM")
    print("-" * 30)
    unchanged_sensitive = check_sensitive_vars()
    if unchanged_sensitive:
        print("⚠️  Các biến nhạy cảm chưa được thay đổi:")
        for var in unchanged_sensitive:
            print(f"   - {var}")
        print("   Hãy thay đổi các giá trị này trước khi deploy production!")
    else:
        print("✅ Tất cả biến nhạy cảm đã được cập nhật")
    
    # Kiểm tra service databases
    print("\n🗄️  KIỂM TRA SERVICE DATABASES")
    print("-" * 30)
    missing_dbs = check_service_databases()
    if missing_dbs:
        print("❌ Thiếu database names cho services:")
        for db in missing_dbs:
            print(f"   - {db}")
    else:
        print("✅ Tất cả service database names đã được thiết lập")
    
    # Kiểm tra Redis databases
    print("\n🔴 KIỂM TRA REDIS DATABASES")
    print("-" * 30)
    missing_redis_dbs = check_redis_dbs()
    if missing_redis_dbs:
        print("❌ Thiếu Redis database numbers:")
        for redis_db in missing_redis_dbs:
            print(f"   - {redis_db}")
    else:
        print("✅ Tất cả Redis database numbers đã được thiết lập")
    
    # Kiểm tra API keys
    print("\n🔑 KIỂM TRA API KEYS")
    print("-" * 30)
    missing_keys = check_api_keys()
    if missing_keys:
        print("⚠️  API keys chưa được cập nhật:")
        for key in missing_keys:
            print(f"   - {key}")
        print("   Hãy cập nhật với keys thực tế từ các nhà cung cấp!")
    else:
        print("✅ Tất cả API keys đã được cập nhật")
    
    # Tổng kết
    print("\n📊 TỔNG KẾT")
    print("=" * 60)
    
    total_issues = len(missing_required) + len(unchanged_sensitive) + len(missing_dbs) + len(missing_redis_dbs) + len(missing_keys)
    
    if total_issues == 0:
        print("🎉 Tất cả biến môi trường đã được cấu hình đúng!")
        print("   Bạn có thể khởi động hệ thống với: docker-compose up -d")
        return 0
    else:
        print(f"⚠️  Tìm thấy {total_issues} vấn đề cần khắc phục")
        print("   Hãy cập nhật file .env và chạy lại script này")
        return 1

if __name__ == "__main__":
    sys.exit(main())
