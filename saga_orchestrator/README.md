# SAGA ORCHESTRATOR - Microservice

## Overview

Saga Orchestrator is a microservice responsible for coordinating distributed transactions and ensuring data consistency.

## 📚 **API Documentation**
- **Swagger UI**: `http://localhost:8008/api/docs/` - Interactive API documentation
- **ReDoc**: `http://localhost:8008/api/redoc/` - Alternative API documentation  
- **OpenAPI Schema**: `http://localhost:8008/api/schema/` - Raw OpenAPI schema

## Main Features

- **Core Functionality**: Core functionality of the service
- **API Management**: API endpoints management
- **Data Processing**: Data processing capabilities
- **Integration**: Integration with other services
- **Monitoring**: Monitoring and logging
- **🎯 Cash Out Saga**: Complete Cash Out transaction orchestration with rollback support

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
DB_NAME=saga_orchestrator_db
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

# Microservices URLs
BETTING_SERVICE_URL=http://betting-service:8000
WALLET_SERVICE_URL=http://wallet-service:8000
RISK_MANAGEMENT_SERVICE_URL=http://risk-management-service:8000
```

### Running the Service

```bash
# Development
python manage.py runserver

# Production
gunicorn saga_orchestrator_project.wsgi:application --bind 0.0.0.0:8000
```

## API Endpoints

### Core Endpoints
- `GET /api/health/` - Health check
- `GET /api/status/` - Service status

### Cash Out Saga Endpoints
- `POST /api/sagas/cashout/start/` - Khởi tạo Cash Out Saga
- `POST /api/sagas/cashout/rollback/` - Rollback Cash Out Saga
- `GET /api/sagas/cashout/status/{id}/` - Trạng thái chi tiết của Saga
- `GET /api/sagas/cashout/list/` - Danh sách các Cash Out Saga
- `POST /api/sagas/cashout/{id}/retry/{step}/` - Retry một bước cụ thể

### General Saga Endpoints
- `GET /api/sagas/transactions/` - Danh sách tất cả saga transactions
- `GET /api/sagas/definitions/` - Danh sách saga definitions
- `GET /api/sagas/events/` - Danh sách saga events
- `POST /api/sagas/start/` - Khởi tạo saga chung
- `GET /api/sagas/statistics/` - Thống kê saga

## 🎯 Cash Out Saga Implementation

### Overview
Cash Out Saga là một workflow hoàn chỉnh để xử lý giao dịch Cash Out, đảm bảo tính nhất quán dữ liệu giữa các service.

### Workflow Steps
1. **cashout_validation** - Kiểm tra tính đủ điều kiện Cash Out
2. **live_odds_fetch** - Lấy live odds từ Risk Management Service
3. **cashout_quote** - Tính toán báo giá Cash Out
4. **wallet_credit** - Cộng tiền vào ví người dùng
5. **liability_update** - Cập nhật liability trong Risk Management Service
6. **cashout_completion** - Hoàn thành giao dịch Cash Out

### Compensation Strategy
Mỗi step đều có compensation logic để rollback khi có lỗi:
- **Wallet Credit Rollback**: Trừ tiền khỏi ví nếu cộng tiền thành công nhưng các bước sau thất bại
- **Liability Update Rollback**: Khôi phục liability nếu cập nhật thành công nhưng hoàn thành thất bại
- **Completion Rollback**: Khôi phục trạng thái bet slip nếu hoàn thành thất bại

### Usage Example

```python
from sagas.orchestrator import SagaOrchestrator

# Khởi tạo orchestrator
orchestrator = SagaOrchestrator()

# Bắt đầu Cash Out Saga
saga = orchestrator.start_cashout_saga(
    bet_slip_id=123,
    user_id=456,
    bookmaker_type='SYSTEM',
    bookmaker_id='system'
)

# Rollback nếu cần
orchestrator.rollback_cashout_saga(
    saga_transaction_id=str(saga.id),
    reason="User cancelled"
)
```

## Project Structure

```
saga_orchestrator/
├── saga_orchestrator_project/     # Django project settings
├── sagas/                         # Main saga app
│   ├── models.py                  # Saga models (CashOutSagaDefinition, CashOutSagaInstance)
│   ├── orchestrator.py            # Saga orchestration logic
│   ├── views.py                   # API endpoints
│   ├── urls.py                    # URL routing
│   ├── fixtures/                  # Saga definitions
│   │   ├── cashout_saga_definition.json  # Cash Out workflow
│   │   └── initial_saga_definitions.json # Other sagas
│   └── tests/                     # Test files
├── documentation/                  # Technical documentation
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── load_cashout_fixture.py        # Script load Cash Out fixture
├── test_cashout_saga.py           # Test script cho Cash Out Saga
└── README.md                       # This file
```

## Setup Cash Out Saga

### 1. Load Fixture
```bash
cd saga_orchestrator
python load_cashout_fixture.py
```

### 2. Test Functionality
```bash
python test_cashout_saga.py
```

### 3. Verify in Admin
- Truy cập Django Admin
- Kiểm tra `SagaDefinition` với `saga_type='cashout_flow'`
- Kiểm tra workflow definition có 6 steps

## Security Features

### Basic Security
- **Authentication**: User authentication
- **Authorization**: Access control
- **Input Validation**: Input validation
- **Rate Limiting**: Request rate limiting

### Saga Security
- **Correlation ID**: Mỗi saga có unique correlation ID
- **User Context**: Saga được liên kết với user cụ thể
- **Timeout Protection**: Mỗi saga có timeout để tránh treo
- **Retry Limits**: Giới hạn số lần retry để tránh loop vô hạn

## Monitoring and Logging

### Logging Configuration
- **Format**: JSON structured logging
- **Level**: INFO (root), DEBUG (service-specific)
- **Output**: Console and file logs

### Saga Monitoring
- **Step Progress**: Tracking tiến độ từng bước
- **Event Logging**: Log tất cả events (start, complete, fail, rollback)
- **Performance Metrics**: Thời gian xử lý từng step
- **Error Tracking**: Chi tiết lỗi và compensation attempts

### Health Checks
- **Service Health**: `/api/health/`
- **Saga Statistics**: `/api/sagas/statistics/`
- **Active Sagas**: Monitoring số lượng saga đang xử lý

## Integration with Other Services

### Betting Service
- Cash Out validation và quote calculation
- Bet slip status management

### Wallet Service
- Credit/debit operations
- Transaction tracking

### Risk Management Service
- Live odds provision
- Liability management

## Troubleshooting

### Common Issues
1. **Saga Timeout**: Kiểm tra timeout settings và service response times
2. **Compensation Failures**: Kiểm tra compensation endpoints có hoạt động không
3. **Service Unavailable**: Kiểm tra kết nối đến các microservices

### Debug Commands
```bash
# Kiểm tra saga status
python manage.py shell
from sagas.models import SagaTransaction
saga = SagaTransaction.objects.get(id='saga_id')
print(saga.status, saga.steps.all())

# Kiểm tra events
for event in saga.events.all():
    print(f"{event.event_type}: {event.message}")
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## License

This project is licensed under the MIT License.
