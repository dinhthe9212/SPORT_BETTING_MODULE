# 🏆 SPORT_BETTING_MODULE

**Một microproject hoàn chỉnh cho hệ thống cá cược thể thao với kiến trúc microservices**

[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Mục lục

- [Tổng quan](#tổng-quan)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Sử dụng](#sử-dụng)
- [API Documentation](#api-documentation)
- [Tích hợp](#tích-hợp)
- [Deployment](#deployment)
- [Đóng góp](#đóng-góp)

## 🎯 Tổng quan

SPORT_BETTING_MODULE là một hệ thống cá cược thể thao được xây dựng với kiến trúc microservices, bao gồm các module độc lập có thể được tích hợp vào các dự án khác. Hệ thống được thiết kế để xử lý các giao dịch cá cược, quản lý rủi ro, và cung cấp dữ liệu thể thao real-time.

### ✨ Tính năng chính

- 🎲 **Betting Service**: Quản lý cá cược và odds
- 🎠 **Carousel Service**: Hiển thị nội dung động
- 👤 **Individual Bookmaker Service**: Quản lý nhà cái cá nhân
- ⚠️ **Risk Management Service**: Quản lý rủi ro
- 🏃 **Saga Orchestrator**: Điều phối giao dịch phân tán
- 📊 **Sports Data Service**: Cung cấp dữ liệu thể thao

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                    SPORT_BETTING_MODULE                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Betting   │  │  Carousel   │  │ Individual  │        │
│  │  Service    │  │  Service    │  │ Bookmaker   │        │
│  │   :8002     │  │   :8006     │  │  Service    │        │
│  └─────────────┘  └─────────────┘  │   :8007     │        │
│                                     └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Risk     │  │    Saga     │  │   Sports    │        │
│  │ Management  │  │Orchestrator │  │    Data     │        │
│  │  Service    │  │   :8008     │  │  Service    │        │
│  │   :8003     │  └─────────────┘  │   :8005     │        │
│  └─────────────┘                    └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Shared Module                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Base Config │  │   Utils     │  │ Middleware  │        │
│  │   Models    │  │  Constants  │  │   Security  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │    Redis    │  │   Kafka     │        │
│  │  Database   │  │    Cache    │  │   Events    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Cài đặt

### Yêu cầu hệ thống

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- Kafka (optional)

### Cài đặt nhanh với Docker

```bash
# Clone repository
git clone <repository-url>
cd SPORT_BETTING_MODULE

# Copy environment file
cp .env.example .env

# Khởi động tất cả services
make up

# Kiểm tra trạng thái
make health
```

### Cài đặt thủ công

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt dependencies cho từng service
cd betting_service
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

# Khởi động service
python manage.py runserver 8002
```

## 🎮 Sử dụng

### Khởi động hệ thống

```bash
# Khởi động tất cả services
make up

# Xem logs
make logs

# Kiểm tra health
make health
```

### Quản lý database

```bash
# Chạy migrations
make migrate

# Reset database
make db-reset

# Backup database
make backup-db
```

### Testing

```bash
# Chạy tất cả tests
make test

# Test từng service
make test-betting
make test-carousel
make test-individual-bookmaker
make test-risk-management
make test-saga
make test-sports-data
```

## 📚 API Documentation

### Betting Service (Port 8002)

```http
GET    /api/bets/                    # Lấy danh sách cá cược
POST   /api/bets/                    # Tạo cá cược mới
GET    /api/bets/{id}/               # Lấy chi tiết cá cược
PUT    /api/bets/{id}/               # Cập nhật cá cược
DELETE /api/bets/{id}/               # Xóa cá cược
POST   /api/bets/{id}/cashout/       # Cash out cá cược
```

### Carousel Service (Port 8006)

```http
GET    /api/carousel/                # Lấy danh sách carousel
POST   /api/carousel/                # Tạo carousel mới
GET    /api/carousel/{id}/           # Lấy chi tiết carousel
PUT    /api/carousel/{id}/           # Cập nhật carousel
DELETE /api/carousel/{id}/           # Xóa carousel
```

### Individual Bookmaker Service (Port 8007)

```http
GET    /api/bookmakers/              # Lấy danh sách nhà cái
POST   /api/bookmakers/              # Tạo nhà cái mới
GET    /api/bookmakers/{id}/         # Lấy chi tiết nhà cái
PUT    /api/bookmakers/{id}/         # Cập nhật nhà cái
DELETE /api/bookmakers/{id}/         # Xóa nhà cái
```

### Risk Management Service (Port 8003)

```http
GET    /api/risk/                    # Lấy thông tin rủi ro
POST   /api/risk/assess/             # Đánh giá rủi ro
GET    /api/risk/thresholds/         # Lấy ngưỡng rủi ro
PUT    /api/risk/thresholds/         # Cập nhật ngưỡng rủi ro
```

### Saga Orchestrator (Port 8008)

```http
GET    /api/sagas/                   # Lấy danh sách saga
POST   /api/sagas/                   # Tạo saga mới
GET    /api/sagas/{id}/              # Lấy chi tiết saga
POST   /api/sagas/{id}/compensate/   # Compensate saga
```

### Sports Data Service (Port 8005)

```http
GET    /api/sports/                  # Lấy danh sách môn thể thao
GET    /api/matches/                 # Lấy danh sách trận đấu
GET    /api/odds/                    # Lấy odds
GET    /api/live-scores/             # Lấy điểm số trực tiếp
```

## 🔗 Tích hợp

### Tích hợp vào dự án mới

1. **Copy shared module**:
```bash
cp -r shared/ /path/to/your/project/
```

2. **Cài đặt dependencies**:
```bash
pip install -r requirements.txt
```

3. **Cấu hình settings**:
```python
# settings.py
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from shared.base_settings import *

# Thêm cấu hình riêng của bạn
```

4. **Sử dụng shared utilities**:
```python
from shared.utils import ServiceClient, ResponseFormatter
from shared.common_models import BaseModel, AuditModel
from shared.constants import SERVICE_NAMES, STATUS_CODES
```

### Tích hợp service riêng lẻ

Mỗi service có thể được tích hợp độc lập:

```python
# Ví dụ tích hợp Betting Service
from shared.utils import ServiceClient

betting_client = ServiceClient('betting', 'http://localhost:8002')
response = betting_client.get('/api/bets/')
```

## 🚀 Deployment

### Production với Docker

```bash
# Build production images
make prod-build

# Khởi động production
make prod-up

# Kiểm tra logs
docker-compose logs -f
```

### Environment Variables

Tạo file `.env` với các biến môi trường:

```bash
# Database
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host

# Redis
REDIS_HOST=your_redis_host
REDIS_PORT=6379

# API Keys
BETTING_API_KEY=your_api_key
INTERNAL_API_KEY=your_internal_key

# Security
SECRET_KEY=your_secret_key
DEBUG=False
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/sport_betting
server {
    listen 80;
    server_name your-domain.com;

    location /api/betting/ {
        proxy_pass http://localhost:8002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/carousel/ {
        proxy_pass http://localhost:8006/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🧪 Testing

### Unit Tests

```bash
# Chạy tests cho tất cả services
make test

# Chạy tests cho service cụ thể
make test-betting
```

### Integration Tests

```bash
# Test API endpoints
curl -X GET http://localhost:8002/api/bets/
curl -X GET http://localhost:8006/api/carousel/
```

### Load Testing

```bash
# Sử dụng Apache Bench
ab -n 1000 -c 10 http://localhost:8002/api/bets/
```

## 📊 Monitoring

### Health Checks

```bash
# Kiểm tra health của tất cả services
make health

# Kiểm tra health của service cụ thể
curl http://localhost:8002/health/
```

### Logs

```bash
# Xem logs của tất cả services
make logs

# Xem logs của service cụ thể
docker-compose logs -f betting_service
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

### Coding Standards

- Sử dụng Python 3.11+
- Tuân thủ PEP 8
- Viết tests cho mọi tính năng mới
- Cập nhật documentation

## 📄 License

Dự án này được phân phối dưới MIT License. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 🆘 Hỗ trợ

- 📧 Email: support@sportbetting.com
- 📱 Discord: [Join our server](https://discord.gg/sportbetting)
- 📖 Documentation: [Wiki](https://github.com/your-repo/wiki)
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)

## 🙏 Acknowledgments

- Django Framework
- Django REST Framework
- PostgreSQL
- Redis
- Docker
- Tất cả contributors

---

**Made with ❤️ by SPORT_BETTING_MODULE Team**
