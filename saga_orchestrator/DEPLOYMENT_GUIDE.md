# 🚀 **SAGA ORCHESTRATOR - DEPLOYMENT GUIDE**

## 📋 **Tổng Quan**

Saga Orchestrator đã được cấu hình **PRODUCTION READY** với Gunicorn WSGI server, API documentation, và monitoring đầy đủ cho distributed transaction coordination.

## 🏗️ **Cấu Hình Production**

### **1. Docker Image Build**
```bash
# Build image với version tag
docker build -t saga-orchestrator:v1.0.0 -f saga_orchestrator/Dockerfile .

# Hoặc build từ docker-compose
docker-compose build saga_orchestrator
```

### **2. Docker Compose Deployment**
```bash
# Chạy service với Gunicorn (Production Ready)
docker-compose up saga_orchestrator

# Chạy trong background
docker-compose up -d saga_orchestrator
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
DB_NAME=saga_db
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
SAGA_API_KEY=your-saga-api-key
INTERNAL_API_KEY=your-internal-api-key
```

### **Optional Variables**
```bash
# Kafka (if using)
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Saga Configuration
SAGA_TIMEOUT=300
SAGA_RETRY_ATTEMPTS=3
SAGA_RETRY_DELAY=5

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
```

## 📊 **API Documentation**

### **Swagger UI**
- **URL**: `http://localhost:8008/api/docs/`
- **Description**: Interactive API documentation với testing capabilities

### **ReDoc**
- **URL**: `http://localhost:8008/api/redoc/`
- **Description**: Clean, responsive API documentation

### **OpenAPI Schema**
- **URL**: `http://localhost:8008/api/schema/`
- **Description**: Raw OpenAPI 3.0 schema

## 🔍 **Health Check & Monitoring**

### **Health Check Endpoints**
```bash
# Basic health check
curl http://localhost:8008/health/

# Detailed health check
curl http://localhost:8008/health/detailed/

# Service status
curl http://localhost:8008/api/sagas/status/
```

### **Logging**
- **Log File**: `logs/saga_orchestrator.log`
- **Format**: JSON structured logging
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Service Not Starting**
```bash
# Check logs
docker-compose logs saga_orchestrator

# Check container status
docker-compose ps saga_orchestrator
```

#### **2. Database Connection Issues**
```bash
# Verify database is running
docker-compose ps postgres

# Check database connectivity
docker-compose exec saga_orchestrator python manage.py dbshell
```

#### **3. Redis Connection Issues**
```bash
# Verify Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

#### **4. Saga Execution Issues**
```bash
# Check saga status
curl http://localhost:8008/api/sagas/status/

# View saga logs
docker-compose logs saga_orchestrator | grep "SAGA"
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

#### **Saga Configuration**
```python
# Adjust saga timeouts based on complexity
SAGA_TIMEOUT = 600  # 10 minutes for complex sagas
SAGA_RETRY_ATTEMPTS = 5  # More retries for critical operations
SAGA_RETRY_DELAY = 10  # Longer delay between retries
```

## 📈 **Monitoring & Metrics**

### **Key Metrics to Monitor**
- **Saga Success Rate**: Percentage of successful saga completions
- **Saga Execution Time**: Average time to complete sagas
- **Compensation Rate**: Percentage of sagas requiring compensation
- **Response Time**: API response times
- **Error Rate**: 4xx/5xx error rates
- **Memory Usage**: Container memory consumption
- **CPU Usage**: Container CPU utilization
- **Database Connections**: Active database connections
- **Redis Connections**: Active Redis connections

### **Alerting Thresholds**
- **Saga Success Rate**: < 95%
- **Saga Execution Time**: > 5 minutes
- **Compensation Rate**: > 10%
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
- [ ] Saga definitions loaded

### **Deployment**
- [ ] Docker image built with version tag
- [ ] Health checks passing
- [ ] API documentation accessible
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Saga orchestration working

### **Post-Deployment**
- [ ] Service responding to requests
- [ ] Database connections stable
- [ ] Redis connections stable
- [ ] Saga execution working
- [ ] Error rates within acceptable limits
- [ ] Performance metrics normal

## 📞 **Support & Maintenance**

### **Regular Maintenance**
- **Log Rotation**: Configure log rotation
- **Database Cleanup**: Regular cleanup of old saga data
- **Security Updates**: Keep dependencies updated
- **Performance Monitoring**: Regular performance reviews
- **Saga Monitoring**: Monitor saga execution patterns

### **Emergency Procedures**
- **Service Restart**: `docker-compose restart saga_orchestrator`
- **Rollback**: `docker-compose down && docker-compose up -d`
- **Database Recovery**: Follow database backup procedures
- **Saga Recovery**: Follow saga compensation procedures
- **Incident Response**: Follow incident response procedures

---

**🎯 Saga Orchestrator is now PRODUCTION READY with Gunicorn, comprehensive API documentation, and full monitoring capabilities for distributed transaction coordination!**
