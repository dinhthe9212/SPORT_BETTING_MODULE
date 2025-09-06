# BETTING SERVICE - Microservice

## Overview

Betting Service is a microservice responsible for managing all P2P betting activities in the system.

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
DB_NAME=betting_service_db
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
gunicorn betting_service_project.wsgi:application --bind 0.0.0.0:8000
```

## API Endpoints

### Core Endpoints
- `GET /api/health/` - Health check
- `GET /api/status/` - Service status

### API Documentation
- **Swagger UI**: `http://localhost:8002/api/docs/` - Interactive API documentation
- **ReDoc**: `http://localhost:8002/api/redoc/` - Alternative API documentation  
- **OpenAPI Schema**: `http://localhost:8002/api/schema/` - Raw OpenAPI schema

### Core CRUD Endpoints (ViewSets)
- `GET|POST /api/betting/sports/` - Quản lý môn thể thao
- `GET|POST|PUT|DELETE /api/betting/sports/{id}/` - Chi tiết môn thể thao
- `GET|POST /api/betting/teams/` - Quản lý đội bóng
- `GET|POST|PUT|DELETE /api/betting/teams/{id}/` - Chi tiết đội bóng
- `GET|POST /api/betting/matches/` - Quản lý trận đấu
- `GET|POST|PUT|DELETE /api/betting/matches/{id}/` - Chi tiết trận đấu
- `GET|POST /api/betting/bet-types/` - Quản lý loại cược
- `GET|POST|PUT|DELETE /api/betting/bet-types/{id}/` - Chi tiết loại cược
- `GET|POST /api/betting/odds/` - Quản lý tỷ lệ cược
- `GET|POST|PUT|DELETE /api/betting/odds/{id}/` - Chi tiết tỷ lệ cược
- `GET|POST /api/betting/bet-slips/` - Quản lý phiếu cược
- `GET|POST|PUT|DELETE /api/betting/bet-slips/{id}/` - Chi tiết phiếu cược
- `GET|POST /api/betting/bet-selections/` - Quản lý lựa chọn cược
- `GET|POST|PUT|DELETE /api/betting/bet-selections/{id}/` - Chi tiết lựa chọn cược
- `GET|POST /api/betting/bet-slip-purchases/` - Quản lý mua phiếu cược
- `GET|POST|PUT|DELETE /api/betting/bet-slip-purchases/{id}/` - Chi tiết mua phiếu cược

### Odds Management Endpoints
- `GET /api/betting/matches/{match_id}/odds/` - Lấy tỷ lệ cược cho trận đấu
- `GET /api/betting/odds/{odd_id}/history/` - Lịch sử thay đổi tỷ lệ cược
- `GET /api/betting/matches/{match_id}/odds/significant-changes/` - Thay đổi tỷ lệ đáng kể
- `GET /api/betting/matches/{match_id}/odds/analytics/` - Phân tích tỷ lệ cược
- `GET /api/betting/matches/{match_id}/odds/snapshot/` - Ảnh chụp tỷ lệ cược hiện tại
- `POST /api/betting/odds/{odd_id}/adjust/` - Điều chỉnh tỷ lệ thủ công (Admin)
- `POST /api/betting/matches/{match_id}/odds/suspend/` - Tạm dừng tỷ lệ cược (Admin)
- `POST /api/betting/matches/{match_id}/odds/resume/` - Khôi phục tỷ lệ cược (Admin)
- `POST /api/betting/matches/{match_id}/odds/update-risk/` - Cập nhật tỷ lệ theo rủi ro (Admin)

### Risk Integration Endpoints
- `GET /api/betting/odds/{odd_id}/risk-profile/` - Lấy hồ sơ rủi ro của tỷ lệ cược
- `POST /api/betting/odds/{odd_id}/configure-risk/` - Cấu hình tỷ lệ dựa trên rủi ro

### Cash Out Endpoints
- `GET|POST /api/betting/cashout/configurations/` - Quản lý cấu hình cash out
- `GET|PUT|PATCH|DELETE /api/betting/cashout/configurations/{id}/` - Chi tiết cấu hình cash out
- `GET /api/betting/cashout/history/` - Lịch sử cash out
- `GET /api/betting/cashout/history/{id}/` - Chi tiết lịch sử cash out
- `POST /api/betting/cashout/request-quote/` - Yêu cầu báo giá cash out
- `POST /api/betting/cashout/confirm/` - Xác nhận thực hiện cash out
- `GET /api/betting/cashout/check-eligibility/` - Kiểm tra điều kiện cash out

### P2P Marketplace & Fractional Ownership Endpoints
- `GET|POST /api/betting/bet-slip-ownerships/` - Quản lý sở hữu phiếu cược
- `GET|POST|PUT|DELETE /api/betting/bet-slip-ownerships/{id}/` - Chi tiết sở hữu phiếu cược
- `GET|POST /api/betting/order-book/` - Quản lý sổ lệnh giao dịch
- `GET|POST|PUT|DELETE /api/betting/order-book/{id}/` - Chi tiết sổ lệnh
- `GET|POST /api/betting/market-suspensions/` - Quản lý tạm dừng thị trường
- `GET|POST|PUT|DELETE /api/betting/market-suspensions/{id}/` - Chi tiết tạm dừng thị trường
- `GET|POST /api/betting/trading-sessions/` - Quản lý phiên giao dịch
- `GET|POST|PUT|DELETE /api/betting/trading-sessions/{id}/` - Chi tiết phiên giao dịch
- `GET|POST /api/betting/p2p-transactions/` - Quản lý giao dịch P2P
- `GET|POST|PUT|DELETE /api/betting/p2p-transactions/{id}/` - Chi tiết giao dịch P2P

### Auto Order Management Endpoints (Chốt Lời & Cắt Lỗ tự động)
- `POST /api/betting/auto-orders/setup/` - Thiết lập lệnh tự động
- `POST /api/betting/auto-orders/cancel/` - Hủy lệnh tự động
- `GET /api/betting/auto-orders/status/{bet_slip_id}/` - Trạng thái lệnh tự động
- `GET /api/betting/auto-orders/user/` - Lệnh tự động của người dùng
- `GET /api/betting/auto-orders/statistics/` - Thống kê lệnh tự động (Admin)
- `POST /api/betting/auto-orders/monitoring/start/` - Bắt đầu giám sát tự động (Admin)

### Market Suspension Endpoints
- `POST /api/betting/webhook/sports/` - Webhook nhận dữ liệu thể thao
- `GET /api/betting/matches/{match_id}/market-suspension/status/` - Trạng thái tạm dừng thị trường
- `POST /api/betting/matches/{match_id}/market-suspension/suspend/` - Tạm dừng thị trường thủ công
- `POST /api/betting/matches/{match_id}/market-suspension/resume/` - Khôi phục thị trường thủ công

### Statistics & Leaderboard Endpoints
- `GET|POST /api/betting/user-statistics/` - Thống kê người dùng
- `GET|POST|PUT|DELETE /api/betting/user-statistics/{id}/` - Chi tiết thống kê người dùng
- `GET|POST /api/betting/leaderboard/` - Bảng xếp hạng
- `GET|POST|PUT|DELETE /api/betting/leaderboard/{id}/` - Chi tiết bảng xếp hạng
- `GET|POST /api/betting/betting-statistics/` - Thống kê cá cược
- `GET|POST|PUT|DELETE /api/betting/betting-statistics/{id}/` - Chi tiết thống kê cá cược
- `GET|POST /api/betting/performance-metrics/` - Chỉ số hiệu suất
- `GET|POST|PUT|DELETE /api/betting/performance-metrics/{id}/` - Chi tiết chỉ số hiệu suất

### Responsible Gaming & Activity Logs
- `GET|POST /api/betting/responsible-gaming-policies/` - Chính sách chơi có trách nhiệm
- `GET|POST|PUT|DELETE /api/betting/responsible-gaming-policies/{id}/` - Chi tiết chính sách
- `GET|POST /api/betting/user-activity-logs/` - Nhật ký hoạt động người dùng
- `GET|POST|PUT|DELETE /api/betting/user-activity-logs/{id}/` - Chi tiết nhật ký hoạt động

## Project Structure

```
betting_service/
├── betting_service_project/     # Django project settings
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
python manage.py test --settings=betting_service_project.test_settings
```

## Deployment

### Docker
```bash
docker build -t betting_service .
docker run -p 8000:8000 betting_service
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
tail -f logs/betting_service.log

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
