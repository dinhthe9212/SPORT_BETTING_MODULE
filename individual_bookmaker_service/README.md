# Individual Bookmaker Service

## Tổng quan
Individual Bookmaker Service là một microservice cung cấp dashboard và công cụ quản lý rủi ro cho các nhà cái cá nhân. Service này giúp người dùng hiểu rõ rủi ro, học cách quản lý rủi ro hiệu quả, và theo dõi hiệu suất của mình.

## Tính năng chính

### 1. Dashboard
- Tổng quan về tài khoản và rủi ro
- Thống kê hiệu suất theo thời gian
- Biểu đồ và báo cáo trực quan
- Thông tin cập nhật theo thời gian thực

### 2. Hệ thống Giáo dục Rủi ro
- Tutorials về quản lý rủi ro
- Bài học theo cấp độ khó
- Theo dõi tiến độ học tập
- Chứng chỉ hoàn thành

### 3. Cảnh báo Rủi ro Thời gian thực
- Thông báo khi rủi ro tăng cao
- Cảnh báo về thay đổi tỷ lệ cược
- Hướng dẫn giảm thiểu rủi ro
- Lịch sử cảnh báo

### 4. Phân tích Hiệu suất
- Đánh giá hiệu suất theo thời gian
- So sánh với các chỉ số chuẩn
- Báo cáo chi tiết về lợi nhuận/thua lỗ
- Khuyến nghị cải thiện

### 5. Tutorial & Best Practices
- Hướng dẫn chi tiết về cá cược an toàn
- Best practices từ chuyên gia
- Case studies thực tế
- Công cụ tính toán rủi ro

## Công nghệ sử dụng

### Backend
- **Python 3.9+**: Ngôn ngữ lập trình chính
- **Django 4.2+**: Framework web
- **Django REST Framework**: API framework
- **PostgreSQL**: Database chính
- **Redis**: Cache và session storage

### Frontend Integration
- **REST API**: Giao diện lập trình ứng dụng
- **WebSocket**: Kết nối thời gian thực
- **JWT**: Xác thực và phân quyền

### Monitoring & Logging
- **Django Logging**: Hệ thống log
- **Health Checks**: Kiểm tra trạng thái service
- **Performance Metrics**: Đo lường hiệu suất

## Cài đặt

### Yêu cầu hệ thống
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Virtual environment

### Bước 1: Clone repository
```bash
git clone <repository-url>
cd individual_bookmaker_service
```

### Bước 2: Tạo virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Cấu hình database
```bash
python manage.py makemigrations
python manage.py migrate
```

### Bước 5: Tạo superuser
```bash
python manage.py createsuperuser
```

### Bước 6: Chạy service
```bash
python manage.py runserver
```

## Biến môi trường

Tạo file `.env` trong thư mục gốc:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Service Configuration
SERVICE_NAME=individual_bookmaker
SERVICE_VERSION=1.0.0
LOG_LEVEL=INFO
```

## API Endpoints

### API Documentation
- **Swagger UI**: `http://localhost:8007/api/docs/` - Interactive API documentation
- **ReDoc**: `http://localhost:8007/api/redoc/` - Alternative API documentation  
- **OpenAPI Schema**: `http://localhost:8007/api/schema/` - Raw OpenAPI schema

### Dashboard & Overview Endpoints
- `GET /api/dashboard/` - Dashboard chính cho Individual Bookmaker (yêu cầu authentication)
- `GET /api/risk-overview/` - Tổng quan về rủi ro và phân tích risk profile
- `GET /api/performance/` - Dữ liệu hiệu suất và thống kê chi tiết

### Education System Endpoints
- `GET /api/education/` - Danh sách tutorials và khóa học giáo dục rủi ro
- `POST /api/education/complete/` - Đánh dấu hoàn thành tutorial và cập nhật tiến độ
- `GET /api/tutorials/` - Quản lý tutorials (CRUD operations)
- `GET /api/tutorials/{id}/` - Chi tiết tutorial cụ thể
- `POST /api/tutorials/` - Tạo tutorial mới (admin only)
- `PUT /api/tutorials/{id}/` - Cập nhật tutorial (admin only)
- `DELETE /api/tutorials/{id}/` - Xóa tutorial (admin only)

### Risk Alerts Management Endpoints
- `GET /api/alerts/` - Danh sách cảnh báo rủi ro thời gian thực
- `POST /api/alerts/mark-read/` - Đánh dấu cảnh báo đã đọc
- `GET /api/alerts/{id}/` - Chi tiết cảnh báo cụ thể
- `POST /api/alerts/` - Tạo cảnh báo mới (admin only)
- `PUT /api/alerts/{id}/` - Cập nhật cảnh báo (admin only)
- `DELETE /api/alerts/{id}/` - Xóa cảnh báo (admin only)

### Best Practices & Guidelines Endpoints
- `GET /api/best-practices/` - Danh sách best practices và hướng dẫn
- `GET /api/best-practices/{id}/` - Chi tiết best practice cụ thể
- `POST /api/best-practices/` - Tạo best practice mới (admin only)
- `PUT /api/best-practices/{id}/` - Cập nhật best practice (admin only)
- `DELETE /api/best-practices/{id}/` - Xóa best practice (admin only)

### Individual Bookmaker Management Endpoints
- `GET /api/bookmakers/` - Danh sách bookmaker profiles
- `POST /api/bookmakers/` - Tạo profile bookmaker mới
- `GET /api/bookmakers/{id}/` - Chi tiết profile bookmaker
- `PUT /api/bookmakers/{id}/` - Cập nhật profile bookmaker
- `DELETE /api/bookmakers/{id}/` - Xóa profile bookmaker
- `PATCH /api/bookmakers/{id}/` - Cập nhật một phần profile

### Performance Analytics Endpoints
- `GET /api/performance/` - Dữ liệu hiệu suất tổng quan
- `GET /api/performance/{id}/` - Chi tiết hiệu suất bookmaker cụ thể
- `POST /api/performance/` - Tạo bản ghi hiệu suất mới
- `PUT /api/performance/{id}/` - Cập nhật dữ liệu hiệu suất
- `DELETE /api/performance/{id}/` - Xóa bản ghi hiệu suất

### Health Check & Integration Endpoints
- `GET /api/health/` - Health check cơ bản
- `GET /health/` - Health check endpoint chính
- `POST /api/webhook/risk-update/` - Webhook nhận cập nhật rủi ro từ external services

### Query Parameters & Filtering
#### Bookmaker Endpoints
- `user_id` (integer): Lọc theo user ID
- `status` (string): Lọc theo trạng thái (ACTIVE, SUSPENDED, INACTIVE, PENDING_VERIFICATION)
- `risk_level` (string): Lọc theo mức độ rủi ro
- `experience_level` (string): Lọc theo cấp độ kinh nghiệm (BEGINNER, INTERMEDIATE, ADVANCED, EXPERT)

#### Tutorial Endpoints
- `difficulty_level` (string): Lọc theo độ khó
- `category` (string): Lọc theo danh mục
- `is_completed` (boolean): Lọc theo trạng thái hoàn thành

#### Alert Endpoints
- `alert_type` (string): Lọc theo loại cảnh báo
- `severity` (string): Lọc theo mức độ nghiêm trọng
- `is_read` (boolean): Lọc theo trạng thái đã đọc

#### Performance Endpoints
- `date_from` (date): Lọc từ ngày
- `date_to` (date): Lọc đến ngày
- `metric_type` (string): Lọc theo loại metric

## Cấu trúc dự án

```
individual_bookmaker_service/
├── individual_bookmaker/
│   ├── __init__.py
│   ├── models.py          # Django models
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── services.py        # Business logic
│   ├── urls.py            # URL routing
│   └── admin.py           # Django admin
├── templates/              # HTML templates
├── static/                 # Static files
├── tests/                  # Test files
├── manage.py              # Django management
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
└── README.md              # This file
```

## Tính năng bảo mật

- **Authentication**: JWT token-based
- **Authorization**: Role-based access control
- **Input Validation**: Strict validation cho tất cả inputs
- **SQL Injection Protection**: Sử dụng Django ORM
- **XSS Protection**: Django built-in protection
- **Rate Limiting**: Giới hạn số request
- **Audit Logging**: Ghi log tất cả hoạt động

## Monitoring & Logging

### Logging
- **Application Logs**: Ghi log tất cả hoạt động
- **Error Logs**: Ghi log lỗi và exceptions
- **Access Logs**: Ghi log truy cập API
- **Performance Logs**: Ghi log thời gian xử lý

### Health Checks
- **Database Connection**: Kiểm tra kết nối DB
- **Redis Connection**: Kiểm tra kết nối Redis
- **Service Status**: Trạng thái tổng thể
- **Dependencies**: Kiểm tra các service phụ thuộc

## Testing

### Unit Tests
```bash
python manage.py test individual_bookmaker.tests.unit
```

### Integration Tests
```bash
python manage.py test individual_bookmaker.tests.integration
```

### API Tests
```bash
python manage.py test individual_bookmaker.tests.api
```

### Coverage Report
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Deployment

### Production Setup
1. **Environment**: Production environment variables
2. **Database**: Production PostgreSQL instance
3. **Redis**: Production Redis instance
4. **Static Files**: CDN hoặc static file server
5. **WSGI**: Gunicorn hoặc uWSGI
6. **Reverse Proxy**: Nginx hoặc Apache

### Docker Deployment
```bash
# Build image
docker build -t individual-bookmaker-service .

# Run container
docker run -d -p 8000:8000 individual-bookmaker-service
```

### Kubernetes Deployment
```bash
# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Apply service
kubectl apply -f k8s/service.yaml
```

## Troubleshooting

### Common Issues

#### Database Connection Error
- Kiểm tra PostgreSQL service
- Kiểm tra connection string
- Kiểm tra firewall settings

#### Redis Connection Error
- Kiểm tra Redis service
- Kiểm tra Redis configuration
- Kiểm tra network connectivity

#### Performance Issues
- Kiểm tra database queries
- Kiểm tra Redis cache hit rate
- Kiểm tra memory usage

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug
python manage.py runserver --verbosity=2
```

## Documentation

- **API Documentation**: Swagger/OpenAPI
- **User Guide**: Hướng dẫn sử dụng
- **Developer Guide**: Hướng dẫn phát triển
- **Deployment Guide**: Hướng dẫn triển khai

## Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

### Code Standards
- **PEP 8**: Python style guide
- **Type Hints**: Sử dụng type annotations
- **Docstrings**: Documentation cho functions
- **Tests**: Unit tests cho mọi feature

## License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## Support

- **Issues**: GitHub Issues
- **Documentation**: Wiki pages
- **Community**: Discussion forum
- **Email**: support@example.com
