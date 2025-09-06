# Hướng Dẫn Database Migration Strategy

## Tổng Quan

Tài liệu này mô tả chiến lược migration database được triển khai để giải quyết vấn đề xung đột khi scale các service trong Docker Compose.

## Vấn Đề Đã Giải Quyết

### Vấn đề ban đầu:
- Tất cả services chạy `python manage.py migrate` trong command khởi động
- Khi scale service (ví dụ: `docker-compose up --scale betting_service=3`), cả 3 container cùng lúc chạy migration
- Gây ra xung đột database và lỗi migration

### Giải pháp triển khai:
1. **Migration Service riêng biệt** - Chạy migration trước tất cả services
2. **Entrypoint Script với Redis Lock** - Đảm bảo chỉ một instance chạy migration
3. **Dependency Management** - Services chờ migration hoàn thành trước khi khởi động

## Kiến Trúc Migration

### 1. Migration Service
```
migration_service/
├── Dockerfile
└── scripts/migrate_all.py
```

**Chức năng:**
- Chạy migration cho tất cả services một cách tuần tự
- Sử dụng Redis lock để tránh xung đột
- Log chi tiết quá trình migration
- Tự động timeout và retry

**Cách hoạt động:**
1. Chờ database và Redis sẵn sàng
2. Lấy migration lock từ Redis
3. Chạy migration cho từng service theo thứ tự
4. Giải phóng lock khi hoàn thành
5. Exit với status code phù hợp

### 2. Entrypoint Script
```
scripts/entrypoint.sh
```

**Chức năng:**
- Thay thế command migration trong mỗi service
- Sử dụng Redis lock để đảm bảo thread-safe
- Chờ migration hoàn thành nếu không phải instance chạy migration
- Khởi động service chính sau khi migration xong

**Cách hoạt động:**
1. Kiểm tra kết nối Redis và Database
2. Thử lấy migration lock
3. Nếu thành công: chạy migration và khởi động service
4. Nếu thất bại: chờ migration hoàn thành rồi khởi động service

## Cấu Hình Docker Compose

### Development Environment
```yaml
# Migration Service chạy trước
migration_service:
  build:
    context: .
    dockerfile: migration_service/Dockerfile
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
  restart: "no"  # Chỉ chạy một lần

# Services chờ migration hoàn thành
betting_service:
  depends_on:
    migration_service:
      condition: service_completed_successfully
  entrypoint: ["/app/entrypoint.sh"]
  command: ["python", "manage.py", "runserver", "0.0.0.0:8002"]
```

### Production Environment
```yaml
# Tương tự development nhưng sử dụng Gunicorn
betting_service:
  entrypoint: ["/app/entrypoint.sh"]
  command: ["gunicorn", "--bind", "0.0.0.0:8002", "betting_service_project.wsgi:application"]
```

## Các Lệnh Sử Dụng

### 1. Khởi động bình thường
```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.production.yml up
```

### 2. Scale services (an toàn)
```bash
# Scale betting service lên 3 instances
docker-compose up --scale betting_service=3

# Scale tất cả services
docker-compose up --scale betting_service=3 --scale carousel_service=2
```

### 3. Chạy migration riêng lẻ
```bash
# Chỉ chạy migration service
docker-compose up migration_service

# Chạy migration cho một service cụ thể
docker-compose exec betting_service python manage.py migrate
```

### 4. Debug migration
```bash
# Xem logs migration
docker-compose logs migration_service

# Xem logs của service cụ thể
docker-compose logs betting_service

# Kiểm tra Redis lock
docker-compose exec redis redis-cli GET migration_betting_service_lock
```

## Monitoring và Troubleshooting

### 1. Kiểm tra trạng thái migration
```bash
# Xem logs migration service
docker-compose logs migration_service

# Kiểm tra Redis locks
docker-compose exec redis redis-cli KEYS "*migration*"
```

### 2. Xử lý lỗi migration
```bash
# Xóa migration lock nếu bị stuck
docker-compose exec redis redis-cli DEL migration_betting_service_lock

# Restart migration service
docker-compose restart migration_service

# Force restart tất cả services
docker-compose down && docker-compose up
```

### 3. Logs quan trọng
- **Migration Service**: `/app/logs/migration.log`
- **Entrypoint Script**: Console output với màu sắc
- **Service Logs**: Standard Docker logs

## Best Practices

### 1. Migration Development
- Luôn test migration trên development environment trước
- Sử dụng `--no-input` flag để tránh interactive prompts
- Backup database trước khi chạy migration quan trọng

### 2. Production Deployment
- Chạy migration service trước khi deploy services mới
- Monitor logs trong quá trình migration
- Có kế hoạch rollback nếu migration thất bại

### 3. Scaling
- Migration service chỉ chạy một lần khi khởi động
- Services có thể scale tự do sau khi migration hoàn thành
- Entrypoint script đảm bảo thread-safe cho mỗi instance

## Environment Variables

### Migration Service
```bash
# Database connection
DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# Redis connection  
REDIS_HOST, REDIS_PORT, REDIS_DB

# Service database names
BETTING_DB_NAME, CAROUSEL_DB_NAME, etc.
```

### Entrypoint Script
```bash
# Service identification
SERVICE_NAME=betting_service

# Database connection
DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# Redis connection
REDIS_HOST, REDIS_PORT, REDIS_DB
```

## Troubleshooting Common Issues

### 1. Migration Service không chạy
**Triệu chứng:** Services không khởi động được
**Giải pháp:**
```bash
# Kiểm tra logs
docker-compose logs migration_service

# Restart migration service
docker-compose restart migration_service
```

### 2. Redis connection failed
**Triệu chứng:** "Không thể kết nối Redis"
**Giải pháp:**
```bash
# Kiểm tra Redis container
docker-compose ps redis

# Restart Redis
docker-compose restart redis
```

### 3. Migration lock bị stuck
**Triệu chứng:** Services chờ mãi không khởi động
**Giải pháp:**
```bash
# Xóa lock
docker-compose exec redis redis-cli DEL migration_betting_service_lock

# Hoặc restart Redis
docker-compose restart redis
```

### 4. Database connection failed
**Triệu chứng:** "Database không sẵn sàng"
**Giải pháp:**
```bash
# Kiểm tra PostgreSQL
docker-compose ps postgres

# Kiểm tra logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

## Kết Luận

Chiến lược migration này đảm bảo:
- ✅ Không có xung đột khi scale services
- ✅ Migration chạy an toàn và có thể monitor
- ✅ Services khởi động đúng thứ tự
- ✅ Dễ dàng debug và troubleshoot
- ✅ Tương thích với cả development và production

Với giải pháp này, bạn có thể scale services một cách an toàn mà không lo lắng về vấn đề migration xung đột.
