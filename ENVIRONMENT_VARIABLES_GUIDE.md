# 🔧 Hướng dẫn Quản lý Biến Môi trường (Environment Variables)

## 📋 Tổng quan

Tài liệu này hướng dẫn cách quản lý biến môi trường trong dự án SPORT_BETTING_MODULE một cách an toàn và hiệu quả.

## 🎯 Mục tiêu

- **Bảo mật**: Không hard-code thông tin nhạy cảm trong code
- **Linh hoạt**: Dễ dàng thay đổi cấu hình cho các môi trường khác nhau
- **Nhất quán**: Sử dụng cùng một bộ biến môi trường cho toàn bộ hệ thống
- **Dễ bảo trì**: Quản lý tập trung tất cả cấu hình

## 📁 Cấu trúc File

```
SPORT_BETTING_MODULE/
├── .env                    # File biến môi trường chính (KHÔNG commit)
├── .env.example           # Template cho biến môi trường
├── docker-compose.yml     # Sử dụng biến môi trường từ .env
└── [service]/
    └── .env.example       # Template riêng cho từng service
```

## 🚀 Cài đặt

### 1. Tạo file .env

```bash
# Copy từ template
cp .env.example .env

# Chỉnh sửa các giá trị theo môi trường của bạn
nano .env
```

### 2. Cập nhật các giá trị quan trọng

**⚠️ QUAN TRỌNG**: Thay đổi các giá trị mặc định sau:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password_here

# Security
SECRET_KEY=your-super-secret-key-change-in-production-2024
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-2024

# API Keys
API_SPORTS_KEY=your_actual_api_sports_key
THE_ODDS_API_KEY=your_actual_the_odds_api_key
OPENLIGADB_KEY=your_actual_openligadb_key
THESPORTSDB_KEY=your_actual_thesportsdb_key
```

## 🔐 Phân loại Biến Môi trường

### 1. **Biến Nhạy cảm (Sensitive)**
```bash
# Database credentials
POSTGRES_PASSWORD=postgres123

# API Keys
API_SPORTS_KEY=your_api_key
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Email credentials
ALERT_EMAIL_PASSWORD=your_app_password
```

### 2. **Biến Cấu hình (Configuration)**
```bash
# Database settings
POSTGRES_DB=sport_betting_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis settings
REDIS_HOST=redis
REDIS_PORT=6379

# Service URLs
BETTING_SERVICE_URL=http://betting_service:8002
```

### 3. **Biến Tính năng (Feature Flags)**
```bash
# Feature toggles
DEBUG=True
AUTO_ORDER_ENABLED=True
CASHOUT_ENABLED=True
CLOUDFLARE_ENABLED=False
```

## 🏗️ Cấu trúc Biến Môi trường

### Database Configuration
```bash
# Main PostgreSQL Database
POSTGRES_DB=sport_betting_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Service-specific Database Names
BETTING_DB_NAME=betting_db
CAROUSEL_DB_NAME=carousel_db
INDIVIDUAL_BOOKMAKER_DB_NAME=individual_bookmaker_db
RISK_MANAGEMENT_DB_NAME=risk_management_db
SAGA_DB_NAME=saga_db
SPORTS_DATA_DB_NAME=sports_data_db
```

### Redis Configuration
```bash
# Redis Main Settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Service-specific Redis Databases
REDIS_DB_BETTING=2
REDIS_DB_CAROUSEL=6
REDIS_DB_INDIVIDUAL_BOOKMAKER=7
REDIS_DB_RISK_MANAGEMENT=3
REDIS_DB_SAGA=8
REDIS_DB_SPORTS_DATA=5
```

### Service URLs
```bash
# Internal Service URLs (Docker network)
# Core Services
AUTH_SERVICE_URL=http://auth_service:8001
BETTING_SERVICE_URL=http://betting_service:8002
RISK_SERVICE_URL=http://risk_management_service:8003
WALLET_SERVICE_URL=http://wallet_service:8004
SPORTS_SERVICE_URL=http://sports_data_service:8005
CAROUSEL_SERVICE_URL=http://carousel_service:8006
INDIVIDUAL_BOOKMAKER_SERVICE_URL=http://individual_bookmaker_service:8007
SAGA_SERVICE_URL=http://saga_orchestrator:8008

# Additional Services
PROMOTIONS_SERVICE_URL=http://promotions_service:8009
GROUPS_SERVICE_URL=http://groups_service:8010
PAYMENT_SERVICE_URL=http://payment_service:8011
NOTIFICATION_SERVICE_URL=http://notification_service:8012
```

**🔧 Cách sử dụng Service URLs trong Code:**

Thay vì hard-code URLs, hãy sử dụng cấu hình tập trung:

```python
# ❌ KHÔNG NÊN - Hard-code URLs
betting_url = "http://localhost:8002"

# ✅ NÊN DÙNG - Sử dụng cấu hình tập trung
from shared.base_settings import get_service_url
betting_url = get_service_url('betting')

# Hoặc lấy tất cả URLs
from shared.base_settings import get_all_service_urls
all_urls = get_all_service_urls()
betting_url = all_urls['betting']
```

### Kafka Configuration
```bash
# Kafka Event Streaming Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_BROKER_ID=1
KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181

# Kafka Listeners (Docker Network Configuration)
KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:29092,PLAINTEXT_INTERNAL://kafka:9092
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092,PLAINTEXT_INTERNAL://kafka:9092
KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_INTERNAL:PLAINTEXT
KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT_INTERNAL
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1
```

**🔧 Giải thích cấu hình Kafka:**
- `KAFKA_BOOTSTRAP_SERVERS=kafka:9092`: Các service kết nối đến Kafka qua hostname `kafka` trong Docker network
- `KAFKA_LISTENERS`: Kafka lắng nghe trên 2 cổng:
  - `29092`: Cho kết nối từ bên ngoài Docker (localhost)
  - `9092`: Cho kết nối nội bộ trong Docker network
- `KAFKA_ADVERTISED_LISTENERS`: Kafka quảng bá địa chỉ kết nối:
  - `localhost:29092`: Cho client bên ngoài Docker
  - `kafka:9092`: Cho các service trong Docker network
- `KAFKA_INTER_BROKER_LISTENER_NAME`: Sử dụng listener nội bộ cho giao tiếp giữa các broker

**⚠️ Lưu ý quan trọng:**
- Các service trong Docker network phải kết nối qua `kafka:9092`
- Client bên ngoài Docker kết nối qua `localhost:29092`
- Cấu hình này đảm bảo Kafka hoạt động đúng trong cả môi trường Docker và local

### API Keys
```bash
# Internal API Keys
BETTING_API_KEY=dev-betting-key-123
CAROUSEL_API_KEY=dev-carousel-key-123
INDIVIDUAL_BOOKMAKER_API_KEY=dev-individual-bookmaker-key-123
RISK_MANAGEMENT_API_KEY=dev-risk-management-key-123
SAGA_API_KEY=dev-saga-key-123
SPORTS_API_KEY=dev-sports-key-123
INTERNAL_API_KEY=dev-internal-key-456

# External API Keys
API_SPORTS_KEY=your_api_sports_key_here
THE_ODDS_API_KEY=your_the_odds_api_key_here
OPENLIGADB_KEY=your_openligadb_key_here
THESPORTSDB_KEY=your_thesportsdb_key_here
```

## 🐳 Sử dụng với Docker

### 1. Khởi động với biến môi trường

```bash
# Khởi động tất cả services
docker-compose up -d

# Xem logs để kiểm tra
docker-compose logs -f
```

### 2. Kiểm tra biến môi trường trong container

```bash
# Kiểm tra biến môi trường của service
docker exec sport_betting_betting_service env | grep DB_

# Kiểm tra biến môi trường cụ thể
docker exec sport_betting_betting_service printenv SECRET_KEY
```

### 3. Override biến môi trường

```bash
# Override biến môi trường khi chạy
POSTGRES_PASSWORD=new_password docker-compose up -d

# Hoặc sử dụng file .env khác
docker-compose --env-file .env.production up -d
```

## 🔄 Quản lý Môi trường

### Development Environment
```bash
# .env.development
DEBUG=True
POSTGRES_PASSWORD=dev_password
SECRET_KEY=dev-secret-key
```

### Staging Environment
```bash
# .env.staging
DEBUG=False
POSTGRES_PASSWORD=staging_password
SECRET_KEY=staging-secret-key
```

### Production Environment
```bash
# .env.production
DEBUG=False
POSTGRES_PASSWORD=production_secure_password
SECRET_KEY=production-secret-key
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 🛡️ Bảo mật

### 1. **KHÔNG commit file .env**
```bash
# Thêm vào .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
echo "!.env.example" >> .gitignore
```

### 2. **Sử dụng .env.example**
- Luôn giữ file `.env.example` trong repository
- Cập nhật `.env.example` khi thêm biến môi trường mới
- Không chứa thông tin nhạy cảm trong `.env.example`

### 3. **Rotate Keys định kỳ**
```bash
# Tạo script rotate keys
#!/bin/bash
# rotate_keys.sh
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
```

### 4. **Sử dụng Secret Management**
```bash
# Với Docker Secrets
echo "my_secret_password" | docker secret create postgres_password -

# Với Kubernetes Secrets
kubectl create secret generic app-secrets \
  --from-literal=postgres-password=my_secret_password \
  --from-literal=secret-key=my_secret_key
```

## 🔧 Troubleshooting

### 1. **Biến môi trường không được load**

```bash
# Kiểm tra file .env có tồn tại
ls -la .env

# Kiểm tra quyền file
chmod 600 .env

# Kiểm tra format file .env
cat .env | grep -v "^#" | grep -v "^$"
```

### 2. **Docker không đọc được biến môi trường**

```bash
# Kiểm tra docker-compose.yml
docker-compose config

# Test với một service
docker-compose up betting_service
```

### 3. **Service không khởi động được**

```bash
# Kiểm tra logs
docker-compose logs betting_service

# Kiểm tra biến môi trường trong container
docker exec sport_betting_betting_service env
```

### 4. **Kafka Connection Issues**

```bash
# Kiểm tra Kafka container có chạy không
docker ps | grep kafka

# Kiểm tra logs Kafka
docker logs sport_betting_kafka

# Test kết nối Kafka từ bên trong Docker network
docker exec sport_betting_saga_orchestrator python -c "
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='kafka:9092')
print('Kafka connection successful')
"

# Test kết nối Kafka từ bên ngoài Docker
python -c "
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='localhost:29092')
print('Kafka external connection successful')
"

# Kiểm tra Kafka topics
docker exec sport_betting_kafka kafka-topics --bootstrap-server kafka:9092 --list
```

**🔍 Các lỗi thường gặp với Kafka:**

1. **Connection refused**: Kiểm tra `KAFKA_ADVERTISED_LISTENERS` có đúng không
2. **Timeout**: Kiểm tra `KAFKA_LISTENERS` có bind đúng port không
3. **Service không kết nối được**: Đảm bảo sử dụng `kafka:9092` trong Docker network

## 📝 Best Practices

### 1. **Naming Convention**
```bash
# Sử dụng UPPER_CASE
DATABASE_URL=postgresql://user:pass@host:port/db

# Prefix theo service
BETTING_DB_NAME=betting_db
CAROUSEL_DB_NAME=carousel_db

# Suffix theo mục đích
REDIS_DB_BETTING=2
REDIS_DB_CAROUSEL=6
```

### 2. **Validation**
```python
# Trong Django settings.py
import os
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_env_variable('SECRET_KEY')
```

### 3. **Default Values**
```python
# Sử dụng default values
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
```

### 4. **Documentation**
```bash
# Luôn cập nhật .env.example khi thêm biến mới
# Thêm comment giải thích
# API_SPORTS_KEY=your_api_sports_key_here  # Get from https://api-sports.io
```

## 🚀 Deployment

### 1. **Production Setup**
```bash
# Tạo file .env.production
cp .env.example .env.production

# Cập nhật giá trị production
nano .env.production

# Deploy với file production
docker-compose --env-file .env.production up -d
```

### 2. **CI/CD Integration**
```yaml
# .github/workflows/deploy.yml
- name: Create .env file
  run: |
    echo "SECRET_KEY=${{ secrets.SECRET_KEY }}" >> .env
    echo "POSTGRES_PASSWORD=${{ secrets.POSTGRES_PASSWORD }}" >> .env
    echo "API_SPORTS_KEY=${{ secrets.API_SPORTS_KEY }}" >> .env
```

### 3. **Health Checks**
```bash
# Kiểm tra tất cả services
make health

# Kiểm tra biến môi trường
make check-env
```

## 📚 Tài liệu Tham khảo

- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [Django Environment Variables](https://docs.djangoproject.com/en/stable/topics/settings/)
- [12-Factor App](https://12factor.net/config)
- [Environment Variables Best Practices](https://blog.doppler.com/environment-variables-best-practices)

## 🆘 Hỗ trợ

Nếu gặp vấn đề với biến môi trường:

1. Kiểm tra file `.env` có tồn tại và đúng format
2. Xem logs của service: `docker-compose logs [service_name]`
3. Kiểm tra biến môi trường trong container: `docker exec [container] env`
4. Tạo issue trên GitHub với thông tin chi tiết

---

**Lưu ý**: Luôn giữ file `.env` an toàn và không commit vào repository!
