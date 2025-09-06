# 🚀 **PRODUCTION DEPLOYMENT GUIDE**

## 📋 **Tổng Quan**

Hướng dẫn triển khai hệ thống Sport Betting Module lên môi trường production với cấu hình tối ưu, bảo mật và monitoring đầy đủ.

## 🏗️ **Kiến Trúc Production**

### **Microservices Architecture**
- **Betting Service**: Quản lý cá cược P2P và odds
- **Carousel Service**: Quản lý nội dung carousel và banner
- **Individual Bookmaker Service**: Công cụ cho nhà cái cá nhân
- **Risk Management Service**: Quản lý rủi ro và giám sát
- **Saga Orchestrator**: Điều phối giao dịch phân tán
- **Sports Data Service**: Dữ liệu thể thao và đồng bộ

### **Infrastructure Components**
- **PostgreSQL**: Database chính
- **Redis**: Cache và message broker
- **Kafka**: Event streaming
- **Nginx**: Reverse proxy và load balancer
- **Celery**: Background tasks và cron jobs

## 🔧 **Cấu Hình Environment**

### **1. Environment Variables**
Tạo file `.env.production`:

```bash
# Database Configuration
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-super-secure-password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Service Database Names
BETTING_DB_NAME=betting_db
CAROUSEL_DB_NAME=carousel_db
INDIVIDUAL_BOOKMAKER_DB_NAME=individual_bookmaker_db
RISK_MANAGEMENT_DB_NAME=risk_management_db
SAGA_DB_NAME=saga_db
SPORTS_DATA_DB_NAME=sports_data_db

# Redis Database Numbers
REDIS_DB_BETTING=1
REDIS_DB_CAROUSEL=2
REDIS_DB_INDIVIDUAL_BOOKMAKER=3
REDIS_DB_RISK_MANAGEMENT=4
REDIS_DB_SAGA=5
REDIS_DB_SPORTS_DATA=6

# Kafka Configuration
KAFKA_BROKER_ID=1
KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1

# Security
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=False

# API Keys
BETTING_API_KEY=your-betting-api-key
CAROUSEL_API_KEY=your-carousel-api-key
INDIVIDUAL_BOOKMAKER_API_KEY=your-individual-bookmaker-api-key
RISK_MANAGEMENT_API_KEY=your-risk-management-api-key
SAGA_API_KEY=your-saga-api-key
SPORTS_API_KEY=your-sports-api-key
INTERNAL_API_KEY=your-internal-api-key

# External API Keys
API_SPORTS_KEY=your-api-sports-key
THE_ODDS_API_KEY=your-the-odds-api-key
OPENLIGADB_KEY=your-openligadb-key
THESPORTSDB_KEY=your-thesportsdb-key

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=1000
RATE_LIMIT_WINDOW=60

# Monitoring
LOG_LEVEL=INFO
```

## 🚀 **Deployment Process**

### **1. Build Production Images**
```bash
# Build all services với version tag
./build-production-images.sh v1.0.0

# Hoặc build với registry
./build-production-images.sh v1.0.0 your-registry.com/
```

### **2. Deploy với Docker Compose**
```bash
# Deploy production stack
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### **3. Verify Deployment**
```bash
# Check all services are healthy
curl http://localhost:8002/health/  # Betting Service
curl http://localhost:8003/health/  # Risk Management Service
curl http://localhost:8005/health/  # Sports Data Service
curl http://localhost:8006/health/  # Carousel Service
curl http://localhost:8007/health/  # Individual Bookmaker Service
curl http://localhost:8008/health/  # Saga Orchestrator
```

## 📊 **API Documentation**

### **Swagger UI Endpoints**
- **Betting Service**: `http://localhost:8002/api/docs/`
- **Risk Management Service**: `http://localhost:8003/api/docs/`
- **Sports Data Service**: `http://localhost:8005/api/docs/`
- **Carousel Service**: `http://localhost:8006/api/docs/`
- **Individual Bookmaker Service**: `http://localhost:8007/api/docs/`
- **Saga Orchestrator**: `http://localhost:8008/api/docs/`

### **ReDoc Endpoints**
- **Betting Service**: `http://localhost:8002/api/redoc/`
- **Risk Management Service**: `http://localhost:8003/api/redoc/`
- **Sports Data Service**: `http://localhost:8005/api/redoc/`
- **Carousel Service**: `http://localhost:8006/api/redoc/`
- **Individual Bookmaker Service**: `http://localhost:8007/api/redoc/`
- **Saga Orchestrator**: `http://localhost:8008/api/redoc/`

## 🔍 **Monitoring & Health Checks**

### **Health Check Endpoints**
```bash
# Basic health checks
curl http://localhost:8002/health/
curl http://localhost:8003/health/
curl http://localhost:8005/health/
curl http://localhost:8006/health/
curl http://localhost:8007/health/
curl http://localhost:8008/health/

# Detailed health checks
curl http://localhost:8002/health/detailed/
curl http://localhost:8003/health/detailed/
curl http://localhost:8005/health/detailed/
curl http://localhost:8006/health/detailed/
curl http://localhost:8007/health/detailed/
curl http://localhost:8008/health/detailed/
```

### **Key Metrics to Monitor**
- **Response Time**: < 2 seconds
- **Error Rate**: < 5%
- **Memory Usage**: < 80%
- **CPU Usage**: < 80%
- **Database Connections**: < 80% of max
- **Redis Connections**: < 80% of max

## 🔒 **Security Best Practices**

### **1. Network Security**
- Sử dụng internal networks cho communication
- Restrict external access chỉ qua Nginx
- Enable SSL/TLS cho tất cả external traffic

### **2. Database Security**
- Sử dụng strong passwords
- Enable SSL cho database connections
- Regular backup và encryption

### **3. API Security**
- Rate limiting cho tất cả endpoints
- API key authentication
- Input validation và sanitization
- Secure error messages

### **4. Container Security**
- Sử dụng non-root users
- Regular security updates
- Image scanning
- Resource limits

## 📈 **Performance Optimization**

### **1. Gunicorn Configuration**
```bash
# Optimize workers based on CPU cores
# Formula: (2 x CPU cores) + 1
# For 4 cores: 9 workers
# For 8 cores: 17 workers
```

### **2. Database Optimization**
```python
# Connection pooling
DATABASES = {
    'default': {
        'OPTIONS': {
            'timeout': 20,
            'MAX_CONNS': 20,
        }
    }
}
```

### **3. Redis Optimization**
```bash
# Memory optimization
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### **4. Nginx Optimization**
```nginx
# Worker processes
worker_processes auto;

# Connection limits
worker_connections 1024;

# Gzip compression
gzip on;
gzip_types text/plain application/json application/javascript text/css;
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Service Not Starting**
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs [service_name]

# Check container status
docker-compose -f docker-compose.production.yml ps
```

#### **2. Database Connection Issues**
```bash
# Check database connectivity
docker-compose -f docker-compose.production.yml exec postgres psql -U postgres -c "\l"

# Check service database connections
docker-compose -f docker-compose.production.yml exec [service_name] python manage.py dbshell
```

#### **3. Redis Connection Issues**
```bash
# Check Redis connectivity
docker-compose -f docker-compose.production.yml exec redis redis-cli ping

# Check Redis info
docker-compose -f docker-compose.production.yml exec redis redis-cli info
```

#### **4. High Memory Usage**
```bash
# Check memory usage
docker stats

# Check specific service
docker-compose -f docker-compose.production.yml exec [service_name] free -h
```

### **Emergency Procedures**

#### **1. Service Restart**
```bash
# Restart specific service
docker-compose -f docker-compose.production.yml restart [service_name]

# Restart all services
docker-compose -f docker-compose.production.yml restart
```

#### **2. Rollback**
```bash
# Stop current deployment
docker-compose -f docker-compose.production.yml down

# Deploy previous version
docker-compose -f docker-compose.production.yml up -d
```

#### **3. Database Recovery**
```bash
# Backup current database
docker-compose -f docker-compose.production.yml exec postgres pg_dump -U postgres > backup.sql

# Restore from backup
docker-compose -f docker-compose.production.yml exec -T postgres psql -U postgres < backup.sql
```

## 📞 **Maintenance & Support**

### **Regular Maintenance**
- **Log Rotation**: Configure log rotation
- **Database Cleanup**: Regular cleanup of old data
- **Security Updates**: Keep dependencies updated
- **Performance Monitoring**: Regular performance reviews
- **Backup Verification**: Regular backup testing

### **Monitoring Setup**
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards và visualization
- **ELK Stack**: Log aggregation và analysis
- **AlertManager**: Alerting và notifications

---

**🎯 Hệ thống Sport Betting Module đã sẵn sàng cho production với cấu hình tối ưu, bảo mật và monitoring đầy đủ!**
