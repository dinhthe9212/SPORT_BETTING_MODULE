# CAROUSEL SERVICE - Microservice

## Overview

Carousel Service is a microservice responsible for managing and displaying carousel, banner and advertising content.

## Main Features

- **Core Functionality**: Core functionality of the service
- **API Management**: API endpoints management
- **Data Processing**: Data processing capabilities
- **Integration**: Integration with other services
- **Monitoring**: Monitoring and logging

## Installation and Setup

### Prerequisites

- Python 3.8+
- PostgreSQL/MySQL
- Redis (if needed)
- Docker (optional)

### Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

```bash
# Database
DB_NAME=carousel_service_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=postgres
DB_PORT=5432

# Redis (if needed)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Security
SECRET_KEY=your-secret-key
DEBUG=True
```

### Running the Service

```bash
# Development
python manage.py runserver

# Production
gunicorn carousel_service_project.wsgi:application --bind 0.0.0.0:8000
```

## API Endpoints

### Core Endpoints
- `GET /api/health/` - Health check
- `GET /api/status/` - Service status

### API Documentation
- **Swagger UI**: `http://localhost:8006/api/docs/` - Interactive API documentation
- **ReDoc**: `http://localhost:8006/api/redoc/` - Alternative API documentation  
- **OpenAPI Schema**: `http://localhost:8006/api/schema/` - Raw OpenAPI schema

### Carousel Management Endpoints
- `GET|POST /api/carousel/` - Quản lý carousel items
- `GET|POST|PUT|DELETE /api/carousel/{id}/` - Chi tiết carousel item
- `GET /api/carousel/prioritized/` - Lấy danh sách carousel items đã được ưu tiên theo quy tắc business
- `GET /api/carousel/randomized/` - Lấy chuỗi sản phẩm ngẫu nhiên cho auto-refresh
- `POST /api/carousel/{id}/purchase/` - Ghi nhận việc mua sản phẩm
- `POST /api/carousel/confirm-purchase/` - Xác nhận đơn hàng (thường được gọi từ payment service)
- `PATCH /api/carousel/{id}/toggle-active/` - Bật/tắt trạng thái active của carousel item
- `PATCH /api/carousel/update-order/` - Cập nhật thứ tự hiển thị của carousel items

### Health Check Endpoints
- `GET /health/` - Health check cơ bản
- `GET /health/comprehensive/` - Health check toàn diện (database, cache, external services)
- `GET /health/ready/` - Readiness check (service sẵn sàng nhận traffic)
- `GET /health/live/` - Liveness check (service đang hoạt động)
- `GET /metrics/` - Metrics endpoint (Prometheus format)

### Analytics Endpoints
- `GET /analytics/trending/` - Lấy danh sách items đang trending
- `GET /analytics/dashboard/` - Dashboard analytics tổng quan
- `GET /analytics/user-behavior/` - Phân tích hành vi người dùng
- `GET /analytics/conversion/` - Phân tích chuyển đổi và tỷ lệ mua hàng
- `GET /analytics/public-summary/` - Tóm tắt analytics công khai
- `POST /analytics/refresh-cache/` - Làm mới cache analytics

### WebSocket Endpoints (Real-time)
- `ws/carousel/` - WebSocket chính cho carousel real-time updates
- `ws/carousel/stats/` - WebSocket cho thống kê real-time (admin only)

### Query Parameters
#### Carousel Endpoints
- `is_active` (boolean): Lọc theo trạng thái active
- `limit` (integer): Giới hạn số lượng items trả về (default: 20)
- `device_type` (string): Loại thiết bị (desktop, mobile, tablet)

#### Analytics Endpoints
- `period` (string): Khoảng thời gian (today, week, month, year)
- `limit` (integer): Giới hạn số lượng kết quả
- `sort_by` (string): Sắp xếp theo (popularity, revenue, conversion)

## Project Structure

```
carousel_service/
├── carousel_service_project/     # Django project settings
├── [app_folders]/              # Django apps
├── documentation/               # Technical documentation
│   ├── implementation/         # Implementation docs
│   ├── security/              # Security docs
│   ├── testing/               # Testing docs
│   ├── guides/                # Usage guides
│   └── changelog/             # Change history
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
└── README.md                   # This file
```

## Security Features

### Basic Security
- **Authentication**: User authentication
- **Authorization**: Access control
- **Input Validation**: Input validation
- **Rate Limiting**: Request rate limiting

## Monitoring and Logging

### Logging Configuration
- **Format**: JSON structured logging
- **Level**: INFO (root), DEBUG (service-specific)
- **Output**: Console and file logs

### Metrics
- **Health Checks**: Service health monitoring
- **Performance Metrics**: Performance tracking

## Testing

### Unit Tests
```bash
python manage.py test
```

### Integration Tests
```bash
python manage.py test --settings=carousel_service_project.test_settings
```

## Deployment

### Docker
```bash
docker build -t carousel_service .
docker run -p 8000:8000 carousel_service
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## Troubleshooting

### Common Issues
1. **Database Connection**: Check database service and connection string
2. **Migration**: Run `python manage.py migrate`
3. **Dependencies**: Check `requirements.txt`

### Logs
```bash
# View service logs
tail -f logs/carousel_service.log

# View Django logs
python manage.py runserver --verbosity=2
```

## Documentation

See detailed documentation in the [documentation/](./documentation/README.md) folder

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

- **Documentation**: [documentation/README.md](./documentation/README.md)
- **Issues**: GitHub Issues
- **Team**: Development Team
