# HƯỚNG DẪN DEPLOYMENT - BETTING SERVICE

## 🚀 **TỔNG QUAN**

Betting Service đã được cải tiến để sử dụng Gunicorn WSGI server thay vì Django development server, phù hợp cho môi trường production.

## 📋 **CÁC THAY ĐỔI ĐÃ THỰC HIỆN**

### 1. **Cải tiến Server**
- ✅ Chuyển từ `python manage.py runserver` sang `gunicorn`
- ✅ Cấu hình 4 workers cho hiệu năng tối ưu
- ✅ Timeout 120 giây, keep-alive 2 giây
- ✅ Max requests 1000 với jitter 100

### 2. **Cải tiến Image Tagging**
- ✅ Thay đổi từ `:latest` sang `v1.0.0`
- ✅ Áp dụng cho tất cả services trong docker-compose.yml

### 3. **Cải tiến Tài liệu**
- ✅ Cập nhật README.md với 50+ API endpoints chi tiết
- ✅ Thêm Swagger UI documentation
- ✅ Thêm ReDoc documentation

## 🔧 **CẤU HÌNH GUNICORN**

### Production Configuration
```bash
gunicorn betting_service_project.wsgi:application \
    --bind 0.0.0.0:8002 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100
```

### Các tham số giải thích:
- `--workers 4`: Số lượng worker processes (khuyến nghị: 2 * CPU cores + 1)
- `--worker-class sync`: Loại worker (sync phù hợp cho Django)
- `--timeout 120`: Timeout cho mỗi request (giây)
- `--keep-alive 2`: Thời gian giữ kết nối alive (giây)
- `--max-requests 1000`: Số request tối đa trước khi restart worker
- `--max-requests-jitter 100`: Random jitter để tránh restart đồng thời

## 🐳 **DOCKER DEPLOYMENT**

### 1. Build Image với Version Tag
```bash
# Build image với version cụ thể
docker build -t test-betting-service:v1.0.0 ./betting_service/

# Tag cho latest (optional)
docker tag test-betting-service:v1.0.0 test-betting-service:latest
```

### 2. Chạy với Docker Compose
```bash
# Chạy tất cả services
docker-compose up -d

# Chỉ chạy betting service
docker-compose up -d betting_service

# Xem logs
docker-compose logs -f betting_service
```

### 3. Health Check
```bash
# Kiểm tra health
curl http://localhost:8002/health/

# Kiểm tra API documentation
curl http://localhost:8002/api/docs/
```

## 📊 **MONITORING & LOGS**

### 1. Logs
```bash
# Xem logs real-time
docker-compose logs -f betting_service

# Xem logs trong container
docker exec -it sport_betting_betting_service tail -f /app/logs/betting_service.log
```

### 2. Metrics
- **Prometheus**: `http://localhost:8002/metrics/`
- **Health Check**: `http://localhost:8002/health/`

### 3. API Documentation
- **Swagger UI**: `http://localhost:8002/api/docs/`
- **ReDoc**: `http://localhost:8002/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8002/api/schema/`

## 🔒 **SECURITY CONSIDERATIONS**

### 1. Environment Variables
Đảm bảo các biến môi trường quan trọng được set:
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
```

### 2. Database Security
- Sử dụng connection pooling
- Set timeout phù hợp
- Enable SSL nếu cần

### 3. Rate Limiting
- Đã cấu hình rate limiting trong settings
- Có thể điều chỉnh qua environment variables

## 🚨 **TROUBLESHOOTING**

### 1. Service không start
```bash
# Kiểm tra logs
docker-compose logs betting_service

# Kiểm tra database connection
docker exec -it sport_betting_betting_service python manage.py check --database default
```

### 2. Performance Issues
```bash
# Kiểm tra số workers
docker exec -it sport_betting_betting_service ps aux | grep gunicorn

# Kiểm tra memory usage
docker stats sport_betting_betting_service
```

### 3. Database Migration
```bash
# Chạy migrations
docker exec -it sport_betting_betting_service python manage.py migrate

# Tạo superuser
docker exec -it sport_betting_betting_service python manage.py createsuperuser
```

## 📈 **SCALING**

### 1. Horizontal Scaling
```yaml
# docker-compose.yml
betting_service:
  deploy:
    replicas: 3
```

### 2. Load Balancer
Sử dụng Nginx hoặc HAProxy để load balance giữa các instances.

### 3. Database Optimization
- Connection pooling
- Read replicas
- Query optimization

## 🔄 **ROLLBACK STRATEGY**

### 1. Version Rollback
```bash
# Rollback về version cũ
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.rollback.yml up -d
```

### 2. Database Rollback
```bash
# Rollback migrations
docker exec -it sport_betting_betting_service python manage.py migrate betting 0001
```

## 📝 **CHANGELOG**

### v1.0.0 (Current)
- ✅ Chuyển sang Gunicorn WSGI server
- ✅ Cập nhật image tagging strategy
- ✅ Thêm Swagger API documentation
- ✅ Cải thiện README.md với 50+ endpoints
- ✅ Cấu hình production-ready settings

### Next Steps
- [ ] Thêm health check endpoints chi tiết
- [ ] Cải thiện logging structure
- [ ] Thêm monitoring alerts
- [ ] Tối ưu database queries
- [ ] Thêm caching strategy

## 📞 **SUPPORT**

- **Documentation**: [README.md](./README.md)
- **API Docs**: http://localhost:8002/api/docs/
- **Issues**: GitHub Issues
- **Team**: Development Team
