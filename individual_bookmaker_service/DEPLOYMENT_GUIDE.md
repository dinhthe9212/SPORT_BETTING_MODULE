# HƯỚNG DẪN DEPLOYMENT - INDIVIDUAL BOOKMAKER SERVICE

## 🚀 **TỔNG QUAN**

Individual Bookmaker Service đã được cải tiến để sử dụng Gunicorn WSGI server thay vì Django development server, phù hợp cho môi trường production. Service này cung cấp dashboard và công cụ quản lý rủi ro cho các nhà cái cá nhân với hệ thống giáo dục độc đáo.

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
gunicorn individual_bookmaker_service.wsgi:application \
    --bind 0.0.0.0:8007 \
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
docker build -t individual-bookmaker-service:v1.0.0 ./individual_bookmaker_service/

# Tag cho latest (optional)
docker tag individual-bookmaker-service:v1.0.0 individual-bookmaker-service:latest
```

### 2. Chạy với Docker Compose
```bash
# Chạy tất cả services
docker-compose up -d

# Chỉ chạy individual bookmaker service
docker-compose up -d individual_bookmaker_service

# Xem logs
docker-compose logs -f individual_bookmaker_service
```

### 3. Health Check
```bash
# Kiểm tra health
curl http://localhost:8007/health/

# Kiểm tra API documentation
curl http://localhost:8007/api/docs/
```

## 📊 **MONITORING & LOGS**

### 1. Logs
```bash
# Xem logs real-time
docker-compose logs -f individual_bookmaker_service

# Xem logs trong container
docker exec -it sport_betting_individual_bookmaker_service tail -f /app/logs/individual_bookmaker_service.log
```

### 2. Metrics
- **Health Check**: `http://localhost:8007/health/`
- **API Health**: `http://localhost:8007/api/health/`

### 3. API Documentation
- **Swagger UI**: `http://localhost:8007/api/docs/`
- **ReDoc**: `http://localhost:8007/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8007/api/schema/`

## 🎓 **TÍNH NĂNG GIÁO DỤC ĐỘC ĐÁO**

### 1. Education System
- **Tutorials**: Hệ thống tutorial giáo dục rủi ro
- **Progress Tracking**: Theo dõi tiến độ học tập
- **Certificates**: Chứng chỉ hoàn thành khóa học
- **Difficulty Levels**: Các cấp độ khó khác nhau

### 2. Risk Management
- **Real-time Alerts**: Cảnh báo rủi ro thời gian thực
- **Risk Assessment**: Đánh giá mức độ rủi ro
- **Best Practices**: Hướng dẫn thực hành tốt nhất
- **Performance Analytics**: Phân tích hiệu suất chi tiết

### 3. Dashboard Features
- **Overview Dashboard**: Tổng quan tài khoản và rủi ro
- **Performance Metrics**: Thống kê hiệu suất theo thời gian
- **Visual Reports**: Biểu đồ và báo cáo trực quan
- **Real-time Updates**: Thông tin cập nhật theo thời gian thực

## 🔒 **SECURITY CONSIDERATIONS**

### 1. Environment Variables
Đảm bảo các biến môi trường quan trọng được set:
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
INDIVIDUAL_BOOKMAKER_API_KEY=your-api-key
INTERNAL_API_KEY=your-internal-api-key
```

### 2. Authentication & Authorization
- JWT token-based authentication
- Role-based access control
- API key authentication cho service-to-service communication
- Rate limiting cho tất cả endpoints

### 3. Data Protection
- Input validation cho tất cả API endpoints
- SQL injection protection với Django ORM
- XSS protection với Django built-in features
- Audit logging cho tất cả hoạt động

## 🚨 **TROUBLESHOOTING**

### 1. Service không start
```bash
# Kiểm tra logs
docker-compose logs individual_bookmaker_service

# Kiểm tra database connection
docker exec -it sport_betting_individual_bookmaker_service python manage.py check --database default

# Kiểm tra Redis connection
docker exec -it sport_betting_individual_bookmaker_service python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

### 2. Performance Issues
```bash
# Kiểm tra số workers
docker exec -it sport_betting_individual_bookmaker_service ps aux | grep gunicorn

# Kiểm tra memory usage
docker stats sport_betting_individual_bookmaker_service

# Kiểm tra database queries
docker exec -it sport_betting_individual_bookmaker_service python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)
```

### 3. Education System Issues
```bash
# Kiểm tra tutorial data
docker exec -it sport_betting_individual_bookmaker_service python manage.py shell
>>> from individual_bookmaker.models import RiskEducationTutorial
>>> RiskEducationTutorial.objects.count()

# Kiểm tra user progress
>>> from individual_bookmaker.models import IndividualBookmaker
>>> IndividualBookmaker.objects.filter(education_enabled=True).count()
```

### 4. Database Migration
```bash
# Chạy migrations
docker exec -it sport_betting_individual_bookmaker_service python manage.py migrate

# Tạo superuser
docker exec -it sport_betting_individual_bookmaker_service python manage.py createsuperuser
```

## 📈 **SCALING**

### 1. Horizontal Scaling
```yaml
# docker-compose.yml
individual_bookmaker_service:
  deploy:
    replicas: 3
```

### 2. Load Balancer
Sử dụng Nginx hoặc HAProxy để load balance giữa các instances.

### 3. Database Optimization
- Connection pooling
- Read replicas
- Query optimization
- Index optimization cho education và performance data

### 4. Redis Scaling
- Redis Cluster cho high availability
- Redis Sentinel cho failover
- Memory optimization cho cache data

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
docker exec -it sport_betting_individual_bookmaker_service python manage.py migrate individual_bookmaker 0001
```

## 📝 **CHANGELOG**

### v1.0.0 (Current)
- ✅ Chuyển sang Gunicorn WSGI server
- ✅ Cập nhật image tagging strategy
- ✅ Thêm Swagger API documentation
- ✅ Cải thiện README.md với 20+ endpoints
- ✅ Cấu hình production-ready settings
- ✅ Education system với tutorials và certificates
- ✅ Risk management với real-time alerts
- ✅ Performance analytics dashboard

### Next Steps
- [ ] Thêm health check endpoints chi tiết
- [ ] Cải thiện logging structure
- [ ] Thêm monitoring alerts
- [ ] Tối ưu database queries
- [ ] Thêm caching strategy cho education data
- [ ] A/B testing framework cho tutorials
- [ ] Machine learning cho risk assessment

## 🎯 **TÍNH NĂNG ĐỘC ĐÁO**

### 1. Education System
- **Tutorial Management**: Quản lý khóa học giáo dục rủi ro
- **Progress Tracking**: Theo dõi tiến độ học tập của từng user
- **Certificate System**: Hệ thống chứng chỉ hoàn thành
- **Difficulty Levels**: Các cấp độ khó từ Beginner đến Expert

### 2. Risk Management
- **Real-time Alerts**: Cảnh báo rủi ro thời gian thực
- **Risk Assessment**: Đánh giá và phân loại mức độ rủi ro
- **Best Practices**: Hướng dẫn thực hành tốt nhất
- **Performance Analytics**: Phân tích hiệu suất chi tiết

### 3. Dashboard & Analytics
- **Overview Dashboard**: Tổng quan tài khoản và rủi ro
- **Performance Metrics**: Thống kê hiệu suất theo thời gian
- **Visual Reports**: Biểu đồ và báo cáo trực quan
- **Real-time Updates**: Thông tin cập nhật theo thời gian thực

## 📞 **SUPPORT**

- **Documentation**: [README.md](./README.md)
- **API Docs**: http://localhost:8007/api/docs/
- **Education System**: Tutorials và certificates
- **Issues**: GitHub Issues
- **Team**: Development Team
