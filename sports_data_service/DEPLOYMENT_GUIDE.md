# 🚀 **SPORTS DATA SERVICE - DEPLOYMENT GUIDE**

## 📋 **Tổng Quan**

Sports Data Service đã được cấu hình **PRODUCTION READY** với Gunicorn WSGI server, Celery Beat cho cron jobs, API documentation, và monitoring đầy đủ.

## 🏗️ **Cấu Hình Production**

### **1. Docker Image Build**
```bash
# Build image với version tag
docker build -t sports-data-service:v1.0.0 -f sports_data_service/Dockerfile .

# Hoặc build từ docker-compose
docker-compose build sports_data_service
```

### **2. Docker Compose Deployment**
```bash
# Chạy service với Gunicorn (Production Ready)
docker-compose up sports_data_service

# Chạy trong background
docker-compose up -d sports_data_service
```

### **3. Gunicorn Configuration**
Service sử dụng Gunicorn với cấu hình tối ưu cho production:
- **Workers**: 4 workers
- **Worker Class**: sync
- **Timeout**: 120 seconds
- **Keep-alive**: 2 seconds
- **Max Requests**: 1000 per worker
- **Max Requests Jitter**: 100

## 🔧 **Environment Variables**

### **Required Variables**
```bash
# Database
DB_NAME=sports_data_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Security
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=False

# API Keys
SPORTS_API_KEY=your-sports-api-key
INTERNAL_API_KEY=your-internal-api-key

# External API Keys
API_SPORTS_KEY=your-api-sports-key
THE_ODDS_API_KEY=your-the-odds-api-key
OPENLIGADB_KEY=your-openligadb-key
THESPORTSDB_KEY=your-thesportsdb-key
```

### **Optional Variables**
```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRY=15
JWT_REFRESH_TOKEN_EXPIRY=7

# Alerting
ALERT_EMAIL_HOST=smtp.gmail.com
ALERT_EMAIL_PORT=587
ALERT_EMAIL_USER=your-email@example.com
ALERT_EMAIL_PASSWORD=your-email-password
ALERT_SLACK_WEBHOOK_URL=your-slack-webhook-url

# Cache Settings
CACHE_LIVE_SCORES_TTL=60
CACHE_FIXTURES_TTL=3600
CACHE_ODDS_DATA_TTL=300
CACHE_PROVIDER_METRICS_TTL=1800

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
```

## 📊 **API Documentation**

### **Swagger UI**
- **URL**: `http://localhost:8005/api/docs/`
- **Description**: Interactive API documentation với testing capabilities

### **ReDoc**
- **URL**: `http://localhost:8005/api/redoc/`
- **Description**: Clean, responsive API documentation

### **OpenAPI Schema**
- **URL**: `http://localhost:8005/api/schema/`
- **Description**: Raw OpenAPI 3.0 schema

## ⏰ **Cron Jobs Management với Celery Beat**

### **Thay thế Scripts Cron**
Thay vì sử dụng `install_cron.sh` và `install_cron_windows.bat`, service hiện sử dụng **Celery Beat** để quản lý scheduled tasks:

```bash
# Chạy Celery Beat (thay thế cho cron jobs)
celery -A sports_data_service_project beat --loglevel=info

# Chạy Celery Worker
celery -A sports_data_service_project worker --loglevel=info

# Chạy cả Beat và Worker
celery -A sports_data_service_project worker --beat --loglevel=info
```

### **Scheduled Tasks**
- **Data Synchronization**: Đồng bộ dữ liệu từ external APIs
- **Data Validation**: Kiểm tra và validate dữ liệu
- **Cache Refresh**: Làm mới cache data
- **Health Checks**: Kiểm tra sức khỏe external APIs
- **Cleanup Tasks**: Dọn dẹp dữ liệu cũ

### **Docker Compose với Celery**
```yaml
# Thêm vào docker-compose.yml
sports_data_celery:
  image: sports-data-service:v1.0.0
  container_name: sport_betting_sports_data_celery
  command: ["celery", "-A", "sports_data_service_project", "worker", "--beat", "--loglevel=info"]
  depends_on:
    - postgres
    - redis
  environment:
    - DB_NAME=sports_data_db
    - DB_USER=postgres
    - DB_PASSWORD=postgres123
    - DB_HOST=postgres
    - REDIS_HOST=redis
  volumes:
    - ./shared:/app/shared
    - ./sports_data_service:/app
```

## 🔍 **Health Check & Monitoring**

### **Health Check Endpoints**
```bash
# Basic health check
curl http://localhost:8005/health/

# Detailed health check
curl http://localhost:8005/health/detailed/

# Service status
curl http://localhost:8005/api/sports_data/status/
```

### **Logging**
- **Log File**: `logs/sports_data_service.log`
- **Format**: JSON structured logging
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Service Not Starting**
```bash
# Check logs
docker-compose logs sports_data_service

# Check container status
docker-compose ps sports_data_service
```

#### **2. Database Connection Issues**
```bash
# Verify database is running
docker-compose ps postgres

# Check database connectivity
docker-compose exec sports_data_service python manage.py dbshell
```

#### **3. Redis Connection Issues**
```bash
# Verify Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

#### **4. External API Issues**
```bash
# Check API provider status
curl http://localhost:8005/api/sports_data/providers/status/

# View provider metrics
curl http://localhost:8005/api/sports_data/providers/metrics/
```

#### **5. Celery Issues**
```bash
# Check Celery status
docker-compose logs sports_data_celery

# Check Celery tasks
docker-compose exec sports_data_service python manage.py shell
>>> from celery import current_app
>>> current_app.control.inspect().active()
```

### **Performance Tuning**

#### **Gunicorn Workers**
```bash
# Adjust workers based on CPU cores
# Formula: (2 x CPU cores) + 1
# For 2 cores: 5 workers
# For 4 cores: 9 workers
```

#### **Database Connection Pool**
```python
# In settings.py
DATABASES = {
    'default': {
        'OPTIONS': {
            'timeout': 20,
            'MAX_CONNS': 20,  # Adjust based on needs
        }
    }
}
```

#### **Cache Configuration**
```python
# Adjust cache TTL based on data freshness requirements
CACHE_SETTINGS = {
    'live_scores_ttl': 30,  # 30 seconds for live scores
    'fixtures_ttl': 1800,   # 30 minutes for fixtures
    'odds_data_ttl': 60,    # 1 minute for odds
}
```

## 📈 **Monitoring & Metrics**

### **Key Metrics to Monitor**
- **Data Sync Success Rate**: Percentage of successful data synchronizations
- **API Response Time**: External API response times
- **Cache Hit Rate**: Cache effectiveness
- **Error Rate**: 4xx/5xx error rates
- **Memory Usage**: Container memory consumption
- **CPU Usage**: Container CPU utilization
- **Database Connections**: Active database connections
- **Redis Connections**: Active Redis connections
- **Celery Task Queue**: Pending and completed tasks

### **Alerting Thresholds**
- **Data Sync Success Rate**: < 95%
- **API Response Time**: > 5 seconds
- **Cache Hit Rate**: < 80%
- **Error Rate**: > 5%
- **Memory Usage**: > 80%
- **CPU Usage**: > 80%

## 🔒 **Security Considerations**

### **Production Security**
1. **Change Default Keys**: Update all default API keys
2. **Enable HTTPS**: Use reverse proxy with SSL
3. **Network Security**: Restrict access to internal networks
4. **Database Security**: Use strong passwords and encryption
5. **Log Security**: Monitor logs for suspicious activities

### **API Security**
- **Rate Limiting**: Configured with 100 requests/minute
- **Authentication**: Internal API key validation
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error messages

## 🚀 **Deployment Checklist**

### **Pre-Deployment**
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Redis connectivity verified
- [ ] API keys updated
- [ ] SSL certificates configured
- [ ] External API keys configured

### **Deployment**
- [ ] Docker image built with version tag
- [ ] Health checks passing
- [ ] API documentation accessible
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Celery Beat configured
- [ ] Data synchronization working

### **Post-Deployment**
- [ ] Service responding to requests
- [ ] Database connections stable
- [ ] Redis connections stable
- [ ] External APIs accessible
- [ ] Celery tasks running
- [ ] Error rates within acceptable limits
- [ ] Performance metrics normal

## 📞 **Support & Maintenance**

### **Regular Maintenance**
- **Log Rotation**: Configure log rotation
- **Database Cleanup**: Regular cleanup of old data
- **Security Updates**: Keep dependencies updated
- **Performance Monitoring**: Regular performance reviews
- **API Monitoring**: Monitor external API health

### **Emergency Procedures**
- **Service Restart**: `docker-compose restart sports_data_service`
- **Rollback**: `docker-compose down && docker-compose up -d`
- **Database Recovery**: Follow database backup procedures
- **API Recovery**: Follow external API recovery procedures
- **Incident Response**: Follow incident response procedures

---

**🎯 Sports Data Service is now PRODUCTION READY with Gunicorn, Celery Beat for cron jobs, comprehensive API documentation, and full monitoring capabilities!**
