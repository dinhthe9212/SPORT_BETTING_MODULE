# 🚀 **RISK MANAGEMENT SERVICE - DEPLOYMENT GUIDE**

## 📋 **Tổng Quan**

Risk Management Service đã được cấu hình **PRODUCTION READY** với Gunicorn WSGI server, API documentation, và monitoring đầy đủ.

## 🏗️ **Cấu Hình Production**

### **1. Docker Image Build**
```bash
# Build image với version tag
docker build -t risk-management-service:v1.0.0 -f risk_management_service/Dockerfile .

# Hoặc build từ docker-compose
docker-compose build risk_management_service
```

### **2. Docker Compose Deployment**
```bash
# Chạy service với Gunicorn (Production Ready)
docker-compose up risk_management_service

# Chạy trong background
docker-compose up -d risk_management_service
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
DB_NAME=risk_management_db
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
RISK_MANAGEMENT_API_KEY=your-risk-management-api-key
INTERNAL_API_KEY=your-internal-api-key
```

### **Optional Variables**
```bash
# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
```

## 📊 **API Documentation**

### **Swagger UI**
- **URL**: `http://localhost:8003/api/docs/`
- **Description**: Interactive API documentation với testing capabilities

### **ReDoc**
- **URL**: `http://localhost:8003/api/redoc/`
- **Description**: Clean, responsive API documentation

### **OpenAPI Schema**
- **URL**: `http://localhost:8003/api/schema/`
- **Description**: Raw OpenAPI 3.0 schema

## 🔍 **Health Check & Monitoring**

### **Health Check Endpoints**
```bash
# Basic health check
curl http://localhost:8003/api/v1/risk/health/

# Detailed health check
curl http://localhost:8003/api/v1/risk/health/detailed/

# Service status
curl http://localhost:8003/api/v1/risk/status/
```

### **Logging**
- **Log File**: `logs/risk_management_service.log`
- **Format**: JSON structured logging
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Service Not Starting**
```bash
# Check logs
docker-compose logs risk_management_service

# Check container status
docker-compose ps risk_management_service
```

#### **2. Database Connection Issues**
```bash
# Verify database is running
docker-compose ps postgres

# Check database connectivity
docker-compose exec risk_management_service python manage.py dbshell
```

#### **3. Redis Connection Issues**
```bash
# Verify Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
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

## 📈 **Monitoring & Metrics**

### **Key Metrics to Monitor**
- **Response Time**: API response times
- **Error Rate**: 4xx/5xx error rates
- **Memory Usage**: Container memory consumption
- **CPU Usage**: Container CPU utilization
- **Database Connections**: Active database connections
- **Redis Connections**: Active Redis connections

### **Alerting Thresholds**
- **Response Time**: > 2 seconds
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

### **Deployment**
- [ ] Docker image built with version tag
- [ ] Health checks passing
- [ ] API documentation accessible
- [ ] Logging configured
- [ ] Monitoring enabled

### **Post-Deployment**
- [ ] Service responding to requests
- [ ] Database connections stable
- [ ] Redis connections stable
- [ ] Error rates within acceptable limits
- [ ] Performance metrics normal

## 📞 **Support & Maintenance**

### **Regular Maintenance**
- **Log Rotation**: Configure log rotation
- **Database Cleanup**: Regular cleanup of old data
- **Security Updates**: Keep dependencies updated
- **Performance Monitoring**: Regular performance reviews

### **Emergency Procedures**
- **Service Restart**: `docker-compose restart risk_management_service`
- **Rollback**: `docker-compose down && docker-compose up -d`
- **Database Recovery**: Follow database backup procedures
- **Incident Response**: Follow incident response procedures

---

**🎯 Risk Management Service is now PRODUCTION READY with Gunicorn, comprehensive API documentation, and full monitoring capabilities!**
