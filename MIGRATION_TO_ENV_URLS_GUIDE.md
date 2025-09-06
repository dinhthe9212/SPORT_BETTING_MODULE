# 🔄 Hướng dẫn Migration từ Hard-coded URLs sang Biến Môi trường

## 📋 Tổng quan

Tài liệu này hướng dẫn cách migration từ hard-coded URLs sang sử dụng biến môi trường trong dự án SPORT_BETTING_MODULE.

## 🎯 Mục tiêu

- **Loại bỏ hard-coded URLs** trong code
- **Sử dụng cấu hình tập trung** cho tất cả service URLs
- **Tăng tính linh hoạt** khi triển khai ở các môi trường khác nhau
- **Dễ bảo trì** và cập nhật URLs

## 🔍 Những gì đã được cải thiện

### ✅ **Trước khi migration:**
```python
# ❌ Hard-coded URLs - Khó bảo trì
betting_url = "http://localhost:8002"
risk_url = "http://localhost:8003"
sports_url = "http://localhost:8005"

# ❌ Inconsistent configuration
url1 = os.getenv('BETTING_URL', 'http://localhost:8002')
url2 = getattr(settings, 'RISK_URL', 'http://risk-service:8000')
url3 = config('SPORTS_URL', default='http://sports:8005')
```

### ✅ **Sau khi migration:**
```python
# ✅ Cấu hình tập trung - Dễ bảo trì
from shared.base_settings import get_service_url

betting_url = get_service_url('betting')
risk_url = get_service_url('risk')
sports_url = get_service_url('sports')

# ✅ Lấy tất cả URLs
from shared.base_settings import get_all_service_urls
all_urls = get_all_service_urls()
```

## 🛠️ Các thay đổi đã thực hiện

### 1. **Cập nhật `shared/base_settings.py`**
- Thêm helper functions: `get_service_url()`, `get_all_service_urls()`
- Chuẩn hóa cấu hình tất cả service URLs
- Thêm documentation chi tiết

### 2. **Cập nhật Service Files**
- `risk_management_service/risk_manager/services.py`
- `betting_service/betting/services.py`
- `saga_orchestrator/saga_orchestrator/services.py`
- `risk_management_service/risk_manager/circuit_breakers.py`

### 3. **Cập nhật Environment Variables**
- Thêm `NOTIFICATION_SERVICE_URL` vào `.env.example`
- Cập nhật `ENVIRONMENT_VARIABLES_GUIDE.md`

## 📚 Cách sử dụng mới

### **1. Lấy URL của một service cụ thể:**
```python
from shared.base_settings import get_service_url

# Lấy URL của betting service
betting_url = get_service_url('betting')
# Kết quả: http://betting_service:8002 (trong Docker)
# Hoặc: http://localhost:8002 (trong development)

# Lấy URL của risk management service
risk_url = get_service_url('risk')
```

### **2. Lấy tất cả service URLs:**
```python
from shared.base_settings import get_all_service_urls

all_urls = get_all_service_urls()
print(all_urls)
# Kết quả:
# {
#     'auth': 'http://auth_service:8001',
#     'betting': 'http://betting_service:8002',
#     'risk': 'http://risk_management_service:8003',
#     'wallet': 'http://wallet_service:8004',
#     'sports': 'http://sports_data_service:8005',
#     'carousel': 'http://carousel_service:8006',
#     'individual_bookmaker': 'http://individual_bookmaker_service:8007',
#     'saga': 'http://saga_orchestrator:8008',
#     'promotions': 'http://promotions_service:8009',
#     'groups': 'http://groups_service:8010',
#     'payment': 'http://payment_service:8011',
#     'notification': 'http://notification_service:8012'
# }
```

### **3. Xử lý lỗi khi service không tồn tại:**
```python
from shared.base_settings import get_service_url

try:
    betting_url = get_service_url('betting')
except KeyError as e:
    print(f"Service không tồn tại: {e}")
    # Xử lý lỗi...
```

## 🔧 Cấu hình cho các môi trường khác nhau

### **Development Environment:**
```bash
# .env.development
BETTING_SERVICE_URL=http://localhost:8002
RISK_SERVICE_URL=http://localhost:8003
SPORTS_SERVICE_URL=http://localhost:8005
```

### **Docker Environment:**
```bash
# .env.docker
BETTING_SERVICE_URL=http://betting_service:8002
RISK_SERVICE_URL=http://risk_management_service:8003
SPORTS_SERVICE_URL=http://sports_data_service:8005
```

### **Production Environment:**
```bash
# .env.production
BETTING_SERVICE_URL=https://api.betting.yourdomain.com
RISK_SERVICE_URL=https://api.risk.yourdomain.com
SPORTS_SERVICE_URL=https://api.sports.yourdomain.com
```

## 🚀 Lợi ích của việc migration

### **1. Linh hoạt triển khai:**
- Dễ dàng thay đổi URLs cho các môi trường khác nhau
- Không cần rebuild code khi thay đổi endpoints

### **2. Bảo mật:**
- Không expose internal URLs trong code
- Dễ dàng quản lý secrets và configurations

### **3. Maintainability:**
- Quản lý tập trung tất cả URLs
- Dễ dàng cập nhật khi có thay đổi
- Consistent configuration across services

### **4. Testing:**
- Dễ dàng mock URLs trong unit tests
- Có thể sử dụng test URLs riêng biệt

## 📝 Best Practices

### **1. Luôn sử dụng helper functions:**
```python
# ✅ NÊN DÙNG
from shared.base_settings import get_service_url
url = get_service_url('betting')

# ❌ KHÔNG NÊN
url = os.getenv('BETTING_SERVICE_URL', 'http://localhost:8002')
```

### **2. Xử lý lỗi gracefully:**
```python
try:
    service_url = get_service_url('betting')
except KeyError:
    logger.error("Betting service URL not configured")
    return None
```

### **3. Cache URLs nếu cần:**
```python
class MyService:
    def __init__(self):
        self.betting_url = get_service_url('betting')
        self.risk_url = get_service_url('risk')
    
    def call_betting_service(self):
        # Sử dụng self.betting_url
        pass
```

## 🔍 Kiểm tra migration

### **1. Tìm hard-coded URLs còn lại:**
```bash
# Tìm tất cả hard-coded URLs
grep -r "http://localhost:\|http://[a-zA-Z0-9-]*:" --include="*.py" .

# Tìm URLs không sử dụng helper functions
grep -r "os.getenv.*http\|getattr.*http" --include="*.py" .
```

### **2. Test configuration:**
```python
# Test script
from shared.base_settings import get_service_url, get_all_service_urls

def test_service_urls():
    try:
        # Test từng service
        services = ['betting', 'risk', 'sports', 'carousel', 'saga']
        for service in services:
            url = get_service_url(service)
            print(f"✅ {service}: {url}")
        
        # Test lấy tất cả URLs
        all_urls = get_all_service_urls()
        print(f"✅ Total services: {len(all_urls)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_service_urls()
```

## 🚨 Lưu ý quan trọng

### **1. Backward Compatibility:**
- Các biến môi trường cũ vẫn hoạt động
- Không cần thay đổi file `.env` hiện tại

### **2. Performance:**
- Helper functions có overhead nhỏ
- Nên cache URLs trong class `__init__` nếu gọi nhiều lần

### **3. Error Handling:**
- Luôn xử lý `KeyError` khi service không tồn tại
- Log errors để debug dễ dàng

## 📚 Tài liệu liên quan

- [ENVIRONMENT_VARIABLES_GUIDE.md](./ENVIRONMENT_VARIABLES_GUIDE.md) - Hướng dẫn quản lý biến môi trường
- [shared/base_settings.py](./shared/base_settings.py) - Cấu hình tập trung
- [.env.example](./.env.example) - Template biến môi trường

## 🆘 Troubleshooting

### **Lỗi "Service not found":**
```python
# Kiểm tra service name có đúng không
from shared.base_settings import MICROSERVICES
print("Available services:", list(MICROSERVICES.keys()))
```

### **URL không đúng:**
```python
# Kiểm tra biến môi trường
import os
print("BETTING_SERVICE_URL:", os.getenv('BETTING_SERVICE_URL'))
```

### **Import error:**
```python
# Đảm bảo shared module có thể import được
import sys
sys.path.append('/path/to/SPORT_BETTING_MODULE')
from shared.base_settings import get_service_url
```

---

**🎉 Chúc mừng!** Bạn đã hoàn thành migration từ hard-coded URLs sang biến môi trường. Hệ thống giờ đây linh hoạt và dễ bảo trì hơn rất nhiều!
