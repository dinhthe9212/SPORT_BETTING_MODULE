# 🔗 Hướng dẫn tích hợp SPORT_BETTING_MODULE

## 📋 Mục lục

- [Tổng quan tích hợp](#tổng-quan-tích-hợp)
- [Tích hợp toàn bộ hệ thống](#tích-hợp-toàn-bộ-hệ-thống)
- [Tích hợp từng service riêng lẻ](#tích-hợp-từng-service-riêng-lẻ)
- [Tích hợp shared module](#tích-hợp-shared-module)
- [API Integration](#api-integration)
- [Database Integration](#database-integration)
- [Authentication & Security](#authentication--security)
- [Troubleshooting](#troubleshooting)

## 🎯 Tổng quan tích hợp

SPORT_BETTING_MODULE được thiết kế để có thể tích hợp linh hoạt vào các dự án khác theo 3 cách:

1. **Tích hợp toàn bộ hệ thống** - Sử dụng tất cả services
2. **Tích hợp từng service riêng lẻ** - Chỉ sử dụng service cần thiết
3. **Tích hợp shared module** - Chỉ sử dụng các utilities chung

## 🏗️ Tích hợp toàn bộ hệ thống

### Bước 1: Chuẩn bị môi trường

```bash
# Clone repository
git clone <repository-url>
cd SPORT_BETTING_MODULE

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### Bước 2: Cấu hình môi trường

```bash
# Copy file environment
cp .env.example .env

# Chỉnh sửa file .env theo môi trường của bạn
nano .env
```

### Bước 3: Khởi động với Docker

```bash
# Khởi động tất cả services
make up

# Kiểm tra trạng thái
make health
```

### Bước 4: Tích hợp vào dự án của bạn

```python
# main.py hoặc settings.py của dự án chính
import os
import sys
from pathlib import Path

# Thêm SPORT_BETTING_MODULE vào Python path
SPORT_BETTING_PATH = Path(__file__).resolve().parent / 'SPORT_BETTING_MODULE'
sys.path.insert(0, str(SPORT_BETTING_PATH))

# Import và sử dụng
from shared.utils import ServiceClient

# Khởi tạo clients cho các services
betting_client = ServiceClient('betting', 'http://localhost:8002')
carousel_client = ServiceClient('carousel', 'http://localhost:8006')
```

## 🔧 Tích hợp từng service riêng lẻ

### Tích hợp Betting Service

```python
# 1. Copy service vào dự án
cp -r betting_service/ /path/to/your/project/

# 2. Cài đặt dependencies
cd betting_service
pip install -r requirements.txt

# 3. Cấu hình settings
# betting_service/betting_service_project/settings.py
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from shared.base_settings import *

# 4. Sử dụng trong dự án chính
from betting_service.betting.models import Bet
from betting_service.betting.serializers import BetSerializer
```

### Tích hợp Carousel Service

```python
# 1. Copy service
cp -r carousel_service/ /path/to/your/project/

# 2. Cài đặt dependencies
cd carousel_service
pip install -r requirements.txt

# 3. Sử dụng
from carousel_service.carousel.models import CarouselItem
from carousel_service.carousel.views import CarouselViewSet
```

### Tích hợp Risk Management Service

```python
# 1. Copy service
cp -r risk_management_service/ /path/to/your/project/

# 2. Sử dụng
from risk_management_service.risk_manager.models import RiskThreshold
from risk_management_service.risk_manager.utils import assess_risk
```

## 📦 Tích hợp Shared Module

### Bước 1: Copy shared module

```bash
cp -r shared/ /path/to/your/project/
```

### Bước 2: Cài đặt dependencies

```bash
pip install django djangorestframework python-decouple redis celery
```

### Bước 3: Sử dụng trong dự án

```python
# settings.py
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from shared.base_settings import *

# Thêm cấu hình riêng
INSTALLED_APPS += [
    'your_app',
]

# models.py
from shared.common_models import BaseModel, AuditModel
from shared.constants import STATUS_CODES

class YourModel(BaseModel):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CODES.choices)
    
    class Meta:
        abstract = False

# views.py
from shared.utils import ResponseFormatter, ServiceClient
from shared.middleware import RateLimitMiddleware

class YourViewSet(viewsets.ModelViewSet):
    def list(self, request):
        data = YourModel.objects.all()
        return Response(ResponseFormatter.success(data))
```

## 🌐 API Integration

### Sử dụng ServiceClient

```python
from shared.utils import ServiceClient

# Khởi tạo client
betting_client = ServiceClient('betting', 'http://localhost:8002')

# GET request
bets = betting_client.get('/api/bets/')

# POST request
new_bet = betting_client.post('/api/bets/', {
    'amount': 100,
    'odds': 2.5,
    'match_id': 'match_123'
})

# PUT request
updated_bet = betting_client.put('/api/bets/123/', {
    'amount': 150
})

# DELETE request
betting_client.delete('/api/bets/123/')
```

### Sử dụng ResponseFormatter

```python
from shared.utils import ResponseFormatter

# Success response
def success_view(request):
    data = {'message': 'Operation successful'}
    return Response(ResponseFormatter.success(data))

# Error response
def error_view(request):
    errors = {'field': ['This field is required']}
    return Response(ResponseFormatter.error('Validation failed', errors))

# Paginated response
def paginated_view(request):
    data = list(range(100))
    page = 1
    page_size = 20
    total = len(data)
    return Response(ResponseFormatter.paginated(data, page, page_size, total))
```

## 🗄️ Database Integration

### Sử dụng BaseModel

```python
from shared.common_models import BaseModel, AuditModel, SoftDeleteModel

# Model với UUID và timestamps
class Product(BaseModel):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Model với audit fields
class Order(AuditModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

# Model với soft delete
class Category(SoftDeleteModel):
    name = models.CharField(max_length=255)
    
    def delete(self):
        self.soft_delete()  # Soft delete thay vì hard delete
```

### Sử dụng CacheManager

```python
from shared.utils import CacheManager

# Cache data
CacheManager.set('user_123', user_data, timeout=3600)

# Get cached data
user_data = CacheManager.get('user_123')

# Delete cache
CacheManager.delete('user_123')

# Get or set pattern
def get_expensive_data():
    return CacheManager.get_or_set('expensive_data', expensive_function, timeout=1800)
```

## 🔐 Authentication & Security

### Sử dụng SecurityUtils

```python
from shared.utils import SecurityUtils

# Generate API key
api_key = SecurityUtils.generate_api_key()

# Hash password
hashed_password = SecurityUtils.hash_password('user_password')

# Verify password
is_valid = SecurityUtils.verify_password('user_password', hashed_password)
```

### Sử dụng middleware

```python
# settings.py
MIDDLEWARE = [
    'shared.middleware.RequestLoggingMiddleware',
    'shared.middleware.RateLimitMiddleware',
    'shared.middleware.SecurityHeadersMiddleware',
    'shared.middleware.APIKeyAuthMiddleware',
    # ... other middleware
]

# API Key authentication
INTERNAL_API_KEYS = [
    'your-api-key-123',
    'another-api-key-456',
]
```

## 🧪 Testing Integration

### Unit Tests

```python
# tests.py
from django.test import TestCase
from shared.utils import ServiceClient, ResponseFormatter

class ServiceClientTest(TestCase):
    def setUp(self):
        self.client = ServiceClient('test_service', 'http://localhost:8000')
    
    def test_get_request(self):
        # Mock response
        response = self.client.get('/test/')
        self.assertEqual(response['status'], 'success')

class ResponseFormatterTest(TestCase):
    def test_success_response(self):
        response = ResponseFormatter.success({'data': 'test'})
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['data'], 'test')
```

### Integration Tests

```python
# integration_tests.py
import requests
from django.test import TestCase

class APIIntegrationTest(TestCase):
    def test_betting_service_integration(self):
        response = requests.get('http://localhost:8002/api/bets/')
        self.assertEqual(response.status_code, 200)
    
    def test_carousel_service_integration(self):
        response = requests.get('http://localhost:8006/api/carousel/')
        self.assertEqual(response.status_code, 200)
```

## 🚨 Troubleshooting

### Lỗi thường gặp

#### 1. Import Error: No module named 'shared'

```python
# Giải pháp: Thêm shared module vào Python path
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
```

#### 2. Database Connection Error

```python
# Kiểm tra cấu hình database trong settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### 3. Redis Connection Error

```python
# Kiểm tra cấu hình Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = ''

# Test connection
from django.core.cache import cache
cache.set('test', 'value')
assert cache.get('test') == 'value'
```

#### 4. Service Communication Error

```python
# Kiểm tra service URLs
MICROSERVICES = {
    'betting': 'http://localhost:8002',
    'carousel': 'http://localhost:8006',
    # ...
}

# Test service health
from shared.utils import HealthChecker
is_healthy = HealthChecker.check_service('betting', '/health/')
```

### Debug Mode

```python
# Bật debug mode trong settings.py
DEBUG = True

# Thêm logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Performance Optimization

```python
# Sử dụng connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 300

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
    }
}

# Database optimization
DATABASES['default']['OPTIONS'] = {
    'timeout': 20,
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
}
```

## 📞 Hỗ trợ

Nếu bạn gặp vấn đề trong quá trình tích hợp:

1. **Kiểm tra logs**: `make logs` hoặc `docker-compose logs -f`
2. **Kiểm tra health**: `make health`
3. **Xem documentation**: [README.md](README.md)
4. **Tạo issue**: [GitHub Issues](https://github.com/your-repo/issues)
5. **Liên hệ support**: support@sportbetting.com

---

**Chúc bạn tích hợp thành công! 🚀**
