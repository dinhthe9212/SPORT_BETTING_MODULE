# HƯỚNG DẪN DEPLOYMENT - CAROUSEL SERVICE

## 🚀 **TỔNG QUAN**

Carousel Service đã được cải tiến để sử dụng Gunicorn WSGI server thay vì Django development server, phù hợp cho môi trường production. Service này quản lý carousel, banner và nội dung quảng cáo với hỗ trợ real-time WebSocket và analytics.

## 📋 **CÁC THAY ĐỔI ĐÃ THỰC HIỆN**

### 1. **Cải tiến Server**
- ✅ Chuyển từ `python manage.py runserver` sang `gunicorn`
- ✅ Cấu hình 4 workers cho hiệu năng tối ưu
- ✅ Timeout 120 giây, keep-alive 2 giây
- ✅ Max requests 1000 với jitter 100

### 2. **Cải tiến Image Tagging**
- ✅ Đã sử dụng `v1.0.0` thay vì `:latest`
- ✅ Consistency với tất cả services trong docker-compose.yml

### 3. **Cải tiến Tài liệu**
- ✅ Cập nhật README.md với 20+ API endpoints chi tiết
- ✅ Thêm Swagger UI documentation
- ✅ Thêm ReDoc documentation

## 🔧 **CẤU HÌNH GUNICORN**

### Production Configuration
```bash
gunicorn carousel_service_project.wsgi:application \
    --bind 0.0.0.0:8006 \
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
docker build -t test-carousel-service:v1.0.0 ./carousel_service/

# Tag cho latest (optional)
docker tag test-carousel-service:v1.0.0 test-carousel-service:latest
```

### 2. Chạy với Docker Compose
```bash
# Chạy tất cả services
docker-compose up -d

# Chỉ chạy carousel service
docker-compose up -d carousel_service

# Xem logs
docker-compose logs -f carousel_service
```

### 3. Health Check
```bash
# Kiểm tra health
curl http://localhost:8006/health/

# Kiểm tra API documentation
curl http://localhost:8006/api/docs/
```

## 📊 **MONITORING & LOGS**

### 1. Logs
```bash
# Xem logs real-time
docker-compose logs -f carousel_service

# Xem logs trong container
docker exec -it sport_betting_carousel_service tail -f /app/logs/carousel_service.log
```

### 2. Metrics
- **Prometheus**: `http://localhost:8006/metrics/`
- **Health Check**: `http://localhost:8006/health/`
- **Comprehensive Health**: `http://localhost:8006/health/comprehensive/`

### 3. API Documentation
- **Swagger UI**: `http://localhost:8006/api/docs/`
- **ReDoc**: `http://localhost:8006/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8006/api/schema/`

## 🔌 **WEBSOCKET & REAL-TIME FEATURES**

### 1. WebSocket Endpoints
- **Main Carousel**: `ws://localhost:8006/ws/carousel/`
- **Stats (Admin)**: `ws://localhost:8006/ws/carousel/stats/`

### 2. Real-time Features
- Carousel auto-refresh notifications
- Purchase confirmations
- Analytics updates
- Performance metrics

### 3. WebSocket Testing
```javascript
// Test WebSocket connection
const ws = new WebSocket('ws://localhost:8006/ws/carousel/');
ws.onopen = function(event) {
    console.log('Connected to carousel WebSocket');
};
ws.onmessage = function(event) {
    console.log('Received:', JSON.parse(event.data));
};
```

## 📈 **ANALYTICS & PERFORMANCE**

### 1. Analytics Endpoints
- **Trending Items**: `GET /analytics/trending/`
- **Dashboard**: `GET /analytics/dashboard/`
- **User Behavior**: `GET /analytics/user-behavior/`
- **Conversion**: `GET /analytics/conversion/`

### 2. Performance Monitoring
- Real-time metrics via WebSocket
- Database query optimization
- Redis caching for analytics
- CDN integration for static assets

### 3. Cache Management
```bash
# Refresh analytics cache
curl -X POST http://localhost:8006/analytics/refresh-cache/

# Check cache status
curl http://localhost:8006/analytics/public-summary/
```

## 🔒 **SECURITY CONSIDERATIONS**

### 1. Environment Variables
Đảm bảo các biến môi trường quan trọng được set:
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
CAROUSEL_API_KEY=your-carousel-api-key
INTERNAL_API_KEY=your-internal-api-key
```

### 2. Rate Limiting
- Đã cấu hình rate limiting trong settings
- Có thể điều chỉnh qua environment variables
- WebSocket connections cũng được rate limited

### 3. API Authentication
- API Key authentication cho service-to-service communication
- JWT authentication cho user endpoints
- CORS configuration cho cross-origin requests

## 🚨 **TROUBLESHOOTING**

### 1. Service không start
```bash
# Kiểm tra logs
docker-compose logs carousel_service

# Kiểm tra database connection
docker exec -it sport_betting_carousel_service python manage.py check --database default

# Kiểm tra Redis connection
docker exec -it sport_betting_carousel_service python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

### 2. WebSocket Issues
```bash
# Kiểm tra Redis channel layer
docker exec -it sport_betting_carousel_service python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()
>>> channel_layer.test_channels()
```

### 3. Performance Issues
```bash
# Kiểm tra số workers
docker exec -it sport_betting_carousel_service ps aux | grep gunicorn

# Kiểm tra memory usage
docker stats sport_betting_carousel_service

# Kiểm tra database queries
docker exec -it sport_betting_carousel_service python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)
```

### 4. Database Migration
```bash
# Chạy migrations
docker exec -it sport_betting_carousel_service python manage.py migrate

# Tạo superuser
docker exec -it sport_betting_carousel_service python manage.py createsuperuser
```

## 📈 **SCALING**

### 1. Horizontal Scaling
```yaml
# docker-compose.yml
carousel_service:
  deploy:
    replicas: 3
```

### 2. Load Balancer
Sử dụng Nginx hoặc HAProxy để load balance giữa các instances.

### 3. Database Optimization
- Connection pooling
- Read replicas
- Query optimization
- Index optimization

### 4. Redis Scaling
- Redis Cluster cho high availability
- Redis Sentinel cho failover
- Memory optimization

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
docker exec -it sport_betting_carousel_service python manage.py migrate carousel 0001
```

## 📝 **CHANGELOG**

### v1.0.0 (Current)
- ✅ Chuyển sang Gunicorn WSGI server
- ✅ Cập nhật image tagging strategy
- ✅ Thêm Swagger API documentation
- ✅ Cải thiện README.md với 20+ endpoints
- ✅ Cấu hình production-ready settings
- ✅ WebSocket real-time support
- ✅ Analytics dashboard integration

### Next Steps
- [ ] Thêm health check endpoints chi tiết
- [ ] Cải thiện logging structure
- [ ] Thêm monitoring alerts
- [ ] Tối ưu database queries
- [ ] Thêm caching strategy
- [ ] CDN integration
- [ ] A/B testing framework

## 📞 **SUPPORT**

- **Documentation**: [README.md](./README.md)
- **API Docs**: http://localhost:8006/api/docs/
- **WebSocket**: ws://localhost:8006/ws/carousel/
- **Issues**: GitHub Issues
- **Team**: Development Team
