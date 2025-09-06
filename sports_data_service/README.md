# Sports Data Service

Module Dữ Liệu Thể Thao (Sports Data Service) - Microservice độc lập cung cấp dữ liệu thể thao cho toàn bộ hệ thống.

## 🚀 **TÍNH NĂNG CHÍNH**

### **Core Features (100% Complete)**
- ✅ **Multi-Provider Data Ingestion**: Tích hợp với API-Sports.io, The-Odds-API, OpenLigaDB, TheSportsDB
- ✅ **Data Normalization & Cleansing**: Chuẩn hóa và làm sạch dữ liệu từ nhiều nguồn
- ✅ **Data Validation & Reconciliation**: Tự động so sánh và đảm bảo tính chính xác
- ✅ **Error & Latency Handling**: Xử lý lỗi và độ trễ một cách thông minh
- ✅ **Asynchronous Processing/Queueing**: Xử lý bất đồng bộ với queue system
- ✅ **Scheduled Data Synchronization**: Đồng bộ dữ liệu theo lịch trình với cron jobs

### **Advanced Features (100% Complete)**
- ✅ **Circuit Breaker Pattern**: Bảo vệ hệ thống khỏi lỗi external API
- ✅ **Advanced Alerting System**: Hệ thống cảnh báo thông minh với cooldown và rate limiting
- ✅ **Conflict Resolution System**: Tự động phát hiện và giải quyết xung đột dữ liệu
- ✅ **Admin Panel Integration**: API endpoints cho quản trị viên

### **New Security & Infrastructure Features (100% Complete)**
- ✅ **JWT Token Refresh**: Hệ thống xác thực JWT với token refresh tự động
- ✅ **IP Whitelisting**: Kiểm soát truy cập dựa trên IP whitelist
- ✅ **Health Check Endpoints**: Kiểm tra sức khỏe hệ thống toàn diện
- ✅ **Database Connection Pooling**: Quản lý connection pool hiệu quả
- ✅ **Data Validation**: Hệ thống validation dữ liệu toàn diện
- ✅ **API Versioning**: Hỗ trợ nhiều phiên bản API (v1, v2)

## 🛠️ **CÀI ĐẶT NHANH**

### **1. Cài đặt Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Cấu hình Environment Variables**
```bash
# Database
DB_NAME=sports_data_db
DB_USER=sports_user
DB_PASSWORD=sports_password
DB_HOST=localhost
DB_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRY=15
JWT_REFRESH_TOKEN_EXPIRY=7

# API Keys
API_SPORTS_KEY=your_api_sports_key
THE_ODDS_API_KEY=your_the_odds_api_key
OPENLIGADB_KEY=your_openligadb_key
THESPORTSDB_KEY=your_thesportsdb_key

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Alerting Configuration
ALERT_EMAIL_HOST=smtp.gmail.com
ALERT_EMAIL_PORT=587
ALERT_EMAIL_USER=your_email@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
ALERT_SLACK_WEBHOOK_URL=your_slack_webhook_url
```

### **3. Cài đặt Cron Jobs**

#### **Linux/macOS:**
```bash
chmod +x scripts/install_cron.sh
./scripts/install_cron.sh
```

#### **Windows:**
```bash
scripts/install_cron_windows.bat
```

### **4. Chạy Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **5. Khởi chạy Service**
```bash
python manage.py runserver
```

## 🔐 **BẢO MẬT VÀ XÁC THỰC**

### **JWT Token System**
- **Access Token**: Hết hạn sau 15 phút
- **Refresh Token**: Hết hạn sau 7 ngày
- **Auto-refresh**: Tự động làm mới token
- **Token Revocation**: Thu hồi token khi cần thiết

### **IP Whitelisting**
- Hỗ trợ IP đơn lẻ, CIDR notation, wildcard
- Cache whitelist để tối ưu performance
- Tự động cập nhật whitelist

## 🏥 **HEALTH CHECKS**

### **Available Endpoints**
- `GET /api/health/basic/` - Kiểm tra cơ bản
- `GET /api/health/detailed/` - Kiểm tra chi tiết
- `GET /api/health/providers/` - Kiểm tra external providers
- `GET /api/health/ready/` - Kiểm tra readiness

### **Health Check Features**
- Database connection status
- Cache performance
- External API health
- System resources (CPU, Memory, Disk)
- Performance metrics

## 🗄️ **DATABASE CONNECTION POOLING**

### **Configuration**
- **Min Connections**: 5
- **Max Connections**: 20
- **Connection Lifetime**: 10 phút
- **Health Check Interval**: 60 giây
- **Retry Attempts**: 3

### **Features**
- Automatic connection health monitoring
- Connection pool statistics
- Graceful failure handling
- Performance optimization

## ✅ **DATA VALIDATION**

### **Validation Types**
- **Match Data**: Team names, scores, status, time
- **Odds Data**: Odds values, provider, type
- **Team Data**: Names, sport, country, league
- **League Data**: Names, sport, country, season

### **Quality Checks**
- **Completeness**: Kiểm tra trường bắt buộc
- **Consistency**: Kiểm tra tính nhất quán
- **Freshness**: Kiểm tra độ mới của dữ liệu

## 🔄 **API VERSIONING**

### **Supported Versions**
- **v1**: Basic features (stable)
- **v2**: Advanced features + backward compatibility

### **Version Detection**
- URL path: `/api/v1/`, `/api/v2/`
- Header: `X-API-Version`
- Query parameter: `?version=v1`

### **Version Management**
- Deprecation warnings
- Migration guides
- Compatibility checking
- Feature matrix

## 📊 **ADMIN ENDPOINTS**

### **Dashboard & Monitoring**
- `GET /api/admin/dashboard/` - Tổng quan hệ thống
- `GET /api/admin/circuit-breaker-status/` - Trạng thái circuit breakers
- `GET /api/admin/provider-performance/` - Hiệu suất providers

### **Data Management**
- `GET /api/admin/reference-odds/` - Dữ liệu tỷ lệ cược tham khảo
- `GET /api/admin/market-analysis/` - Phân tích thị trường
- `POST /api/admin/force-sync/` - Đồng bộ dữ liệu thủ công

### **Conflict Resolution**
- `GET /api/admin/active-conflicts/` - Xung đột dữ liệu đang hoạt động
- `POST /api/admin/resolve-conflict/` - Giải quyết xung đột thủ công

### **Alert Management**
- `GET /api/admin/alert-history/` - Lịch sử cảnh báo

## 🔧 **CẤU HÌNH NÂNG CAO**

### **Circuit Breaker Settings**
```python
CIRCUIT_BREAKER_SETTINGS = {
    'failure_threshold': 3,
    'recovery_timeout': 120,
    'expected_exception': Exception
}
```

### **Alerting Rules**
```python
ALERT_RULES = {
    'data_sync_failure': {
        'cooldown': 300,  # 5 phút
        'max_alerts_per_hour': 3
    },
    'provider_down': {
        'cooldown': 600,  # 10 phút
        'max_alerts_per_hour': 2
    }
}
```

### **Cache Strategy**
```python
CACHE_SETTINGS = {
    'live_scores_ttl': 60,      # 1 phút
    'fixtures_ttl': 3600,       # 1 giờ
    'odds_data_ttl': 300,       # 5 phút
    'provider_metrics_ttl': 1800  # 30 phút
}
```

## 📁 **CẤU TRÚC DỰ ÁN**

```
sports_data_service/
├── sports_data/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── admin_views.py
│   ├── health_checks.py
│   ├── api_versioning.py
│   ├── urls.py
│   ├── auth/
│   │   └── jwt_utils.py
│   ├── middleware/
│   │   └── ip_whitelist.py
│   ├── database/
│   │   └── connection_manager.py
│   ├── validation/
│   │   └── validators.py
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── api_sports_provider.py
│   │   ├── the_odds_api_provider.py
│   │   ├── openligadb_provider.py
│   │   ├── thesportsdb_provider.py
│   │   ├── multi_sports_provider.py
│   │   └── circuit_breaker.py
│   ├── alerting/
│   │   └── alert_manager.py
│   ├── conflict_resolution/
│   │   └── conflict_manager.py
│   └── management/
│       └── commands/
│           ├── sync_sports_data.py
│           └── sync_odds_data.py
├── scripts/
│   ├── install_cron.sh
│   └── install_cron_windows.bat
├── sports_data_service/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
├── README.md
└── 100_PERCENT_COMPLETION_REPORT.md
```

## 🚀 **SỬ DỤNG**

### **1. Health Check**
```bash
curl http://localhost:8000/api/health/basic/
```

### **2. API Version Info**
```bash
curl http://localhost:8000/api/versions/
```

### **3. Admin Dashboard**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/admin/dashboard/
```

### **4. Versioned API**
```bash
# V1 API
curl http://localhost:8000/api/v1/health/basic/

# V2 API
curl http://localhost:8000/api/v2/health/detailed/
```

## 📈 **MONITORING & ALERTS**

### **System Metrics**
- Database connection pool status
- External API response times
- Cache hit rates
- System resource usage

### **Alert Channels**
- Email notifications
- Slack webhooks
- Custom webhook endpoints
- SMS framework (configurable)

### **Alert Types**
- Data synchronization failures
- Provider API downtime
- System resource warnings
- Data quality issues

## 🔍 **TROUBLESHOOTING**

### **Common Issues**
1. **Database Connection Errors**: Kiểm tra connection pool settings
2. **Circuit Breaker Open**: Reset circuit breaker hoặc kiểm tra provider
3. **IP Whitelist Blocked**: Thêm IP vào whitelist
4. **JWT Token Expired**: Sử dụng refresh token

### **Debug Commands**
```bash
# Kiểm tra circuit breaker status
python manage.py shell
>>> from sports_data.providers.circuit_breaker import circuit_breaker_manager
>>> circuit_breaker_manager.get_status()

# Kiểm tra connection pool
>>> from sports_data.database.connection_manager import db_connection_manager
>>> db_connection_manager.get_pool_status()
```

## 📚 **TÀI LIỆU THAM KHẢO**

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [JWT Authentication](https://jwt.io/)
- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)

## 🤝 **ĐÓNG GÓP**

1. Fork dự án
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📄 **LICENSE**

Dự án này được phân phối dưới MIT License. Xem file `LICENSE` để biết thêm chi tiết.

---

**Sports Data Service** - Module dữ liệu thể thao hoàn chỉnh với 100% tính năng được triển khai! 🎯⚽🏀
