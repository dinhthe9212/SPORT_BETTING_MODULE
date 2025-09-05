# 🚀 **HƯỚNG DẪN SỬ DỤNG PERFORMANCE OPTIMIZATION SERVICE**

## **📋 TỔNG QUAN**

Performance Optimization Service là service tối ưu hóa hiệu suất hệ thống quản lý rủi ro, giúp hệ thống chạy mượt mà và ổn định.

## **🎯 CÁC TÍNH NĂNG CHÍNH**

### **1. Database Optimization**
- Tối ưu hóa database indexes
- Phân tích và tối ưu hóa slow queries
- Quản lý database connections
- Cleanup old data

### **2. Caching Strategy**
- Cache risk configurations
- Cache user risk profiles
- Cache market risk data
- Cache frequently accessed data

### **3. Real-time Processing Optimization**
- Implement async processing
- Implement batch processing
- Tối ưu hóa memory usage
- Tối ưu hóa CPU usage

## **🔧 CÁCH SỬ DỤNG**

### **API Endpoints**

#### **1. Tối ưu hóa Database**
```bash
GET /api/risk-management/performance-optimization/optimize_database/
```

**Response:**
```json
{
    "status": "success",
    "message": "Database optimization completed",
    "result": {
        "indexes": {"indexes_created": 3, "status": "success"},
        "slow_queries": {"slow_queries_found": 2, "optimizations_applied": 1, "status": "success"},
        "connections": {"connections_closed": 1, "status": "success"},
        "cleanup": {"old_volatility_logs": 150, "old_patterns": 75, "status": "success"},
        "execution_time": 0.85,
        "status": "success"
    }
}
```

#### **2. Implement Caching Strategy**
```bash
GET /api/risk-management/performance-optimization/implement_caching/
```

**Response:**
```json
{
    "status": "success",
    "message": "Caching strategy implemented",
    "result": {
        "risk_configs": {"sport_configs_cached": 25, "bet_type_configs_cached": 150, "status": "success"},
        "user_profiles": {"user_profiles_cached": 500, "status": "success"},
        "market_data": {"market_risk_data_cached": 45, "status": "success"},
        "frequent_data": {"frequent_data_cached": 3, "status": "success"},
        "execution_time": 0.32,
        "status": "success"
    }
}
```

#### **3. Tối ưu hóa Real-time Processing**
```bash
GET /api/risk-management/performance-optimization/optimize_real_time/
```

**Response:**
```json
{
    "status": "success",
    "message": "Real-time processing optimization completed",
    "result": {
        "async": {"async_processing": "configured", "status": "success"},
        "batch": {"batch_processing": "configured", "status": "success"},
        "memory": {"garbage_collected": 1250, "cache_cleared": false, "memory_usage_percent": 62.8, "status": "success"},
        "cpu": {"cpu_usage_percent": 45.2, "batch_size": 50, "optimization": "maintained_batch_size", "status": "success"},
        "execution_time": 0.18,
        "status": "success"
    }
}
```

#### **4. Lấy Performance Metrics**
```bash
GET /api/risk-management/performance-optimization/get_metrics/
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "system": {
            "cpu_percent": 45.2,
            "memory_percent": 62.8,
            "memory_available_gb": 8.5,
            "disk_percent": 38.5,
            "disk_free_gb": 125.8
        },
        "database": {
            "active_connections": 15,
            "total_query_time": 2.45,
            "average_query_time": 0.163
        },
        "cache": {
            "hit_rate": 89.3,
            "hits": 1250,
            "misses": 150
        },
        "timestamp": 1703123456.789
    }
}
```

#### **5. Chạy Toàn bộ Optimization**
```bash
GET /api/risk-management/performance-optimization/run_full_optimization/
```

**Response:**
```json
{
    "status": "success",
    "message": "Full optimization completed",
    "result": {
        "database": {...},
        "caching": {...},
        "real_time": {...},
        "performance_metrics": {...},
        "total_execution_time": 1.85,
        "timestamp": 1703123456.789
    }
}
```

## **⚙️ CẤU HÌNH**

### **Environment Variables**
```bash
# Cache TTL (giây)
RISK_CACHE_TTL=300

# Performance thresholds
PERFORMANCE_CPU_THRESHOLD=80
PERFORMANCE_MEMORY_THRESHOLD=80
PERFORMANCE_DISK_THRESHOLD=90
```

### **Settings Configuration**
```python
# settings.py
RISK_CACHE_TTL = 300  # 5 phút
PERFORMANCE_MONITORING_ENABLED = True
AUTO_OPTIMIZATION_ENABLED = True
```

## **📊 MONITORING VÀ ALERTS**

### **Performance Thresholds**
- **CPU Usage**: > 80% → Cảnh báo
- **Memory Usage**: > 80% → Cảnh báo  
- **Disk Usage**: > 90% → Cảnh báo
- **Cache Hit Rate**: < 80% → Cảnh báo

### **Auto-optimization Triggers**
- Memory usage > 80% → Garbage collection + cache cleanup
- CPU usage > 80% → Giảm batch size
- Slow queries > 100ms → Query optimization
- Cache miss rate > 20% → Cache warming

## **🔍 TROUBLESHOOTING**

### **Common Issues**

#### **1. Database Optimization Failed**
```bash
# Kiểm tra database connection
python manage.py dbshell

# Kiểm tra slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

#### **2. Caching Issues**
```bash
# Kiểm tra cache status
python manage.py shell
from django.core.cache import cache
cache.get('test_key')
```

#### **3. Memory Issues**
```bash
# Kiểm tra memory usage
ps aux | grep python
free -h
```

### **Debug Mode**
```python
# Bật debug logging
LOGGING = {
    'loggers': {
        'risk_manager.performance': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## **📈 BEST PRACTICES**

### **1. Regular Optimization**
- Chạy database optimization hàng ngày
- Monitor performance metrics liên tục
- Cleanup old data hàng tuần

### **2. Caching Strategy**
- Cache data thường xuyên truy cập
- Sử dụng appropriate TTL
- Monitor cache hit rate

### **3. Resource Management**
- Monitor CPU, memory, disk usage
- Set appropriate thresholds
- Implement auto-scaling nếu cần

## **🚨 EMERGENCY PROCEDURES**

### **Critical Performance Issues**
1. **Immediate Actions:**
   - Clear all caches
   - Restart critical services
   - Activate emergency mode

2. **Investigation:**
   - Check system logs
   - Analyze performance metrics
   - Identify bottlenecks

3. **Recovery:**
   - Apply optimizations
   - Scale resources
   - Monitor recovery

## **📞 SUPPORT**

### **Contact Information**
- **Technical Support**: tech-support@company.com
- **Emergency Hotline**: +84-xxx-xxx-xxx
- **Documentation**: [Internal Wiki Link]

### **Escalation Matrix**
1. **Level 1**: System Administrator
2. **Level 2**: DevOps Engineer  
3. **Level 3**: System Architect
4. **Level 4**: CTO

---

**📝 Lưu ý**: Service này được thiết kế để tự động tối ưu hóa hệ thống. Trong trường hợp khẩn cấp, có thể can thiệp thủ công thông qua các API endpoints.
