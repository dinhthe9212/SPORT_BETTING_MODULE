"""
Comprehensive API Documentation cho Risk Management Service
Swagger/OpenAPI documentation với examples và error codes
"""

from drf_yasg import openapi

# ============================================================================
# RISK CHECK API DOCUMENTATION
# ============================================================================

risk_check_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['user_id', 'match_id', 'bet_type_id', 'outcome', 'stake_amount', 'odds_value'],
    properties={
        'user_id': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='ID của người dùng đặt cược',
            example='user_123'
        ),
        'match_id': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='ID của trận đấu',
            example='match_456'
        ),
        'bet_type_id': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='ID của loại cược',
            example='bet_type_789'
        ),
        'outcome': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Kết quả được chọn',
            example='Home Win'
        ),
        'stake_amount': openapi.Schema(
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
            description='Số tiền cược',
            example=100.00
        ),
        'odds_value': openapi.Schema(
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
            description='Tỷ lệ cược',
            example=2.00
        )
    }
)

risk_check_success_response = openapi.Response(
    description='Risk check thành công - Bet được chấp nhận',
    examples={
        'application/json': {
            'approved': True,
            'risk_level': 'LOW',
            'liability_impact': 200.0,
            'current_liability': 1500.0,
            'new_liability': 1700.0,
            'threshold': 10000.0,
            'remaining_capacity': 8300.0,
            'user_risk_status': 'WITHIN_LIMITS',
            'market_status': 'MARKET_ACTIVE',
            'recommendations': [
                'Bet được chấp nhận, rủi ro trong ngưỡng cho phép'
            ]
        }
    }
)

risk_check_rejected_response = openapi.Response(
    description='Risk check thất bại - Bet bị từ chối',
    examples={
        'application/json': {
            'approved': False,
            'risk_level': 'HIGH',
            'liability_impact': 200.0,
            'current_liability': 9500.0,
            'new_liability': 9700.0,
            'threshold': 10000.0,
            'exceeds_by': 0.0,
            'user_risk_status': 'WITHIN_LIMITS',
            'market_status': 'MARKET_ACTIVE',
            'rejection_reason': 'Vượt quá ngưỡng rủi ro: $0.00',
            'recommendations': [
                'Giảm số tiền cược để giảm rủi ro',
                'Chọn outcome khác có rủi ro thấp hơn'
            ]
        }
    }
)

risk_check_error_response = openapi.Response(
    description='Lỗi hệ thống',
    examples={
        'application/json': {
            'approved': False,
            'error': 'Lỗi kết nối hệ thống, vui lòng thử lại sau',
            'error_details': {
                'error_type': 'ConnectionError',
                'error_category': 'CONNECTION_ERROR',
                'error_message': 'Connection timeout',
                'timestamp': '2024-01-15T10:30:00Z'
            },
            'risk_level': 'UNKNOWN',
            'recommendations': [
                'Kiểm tra lại thông tin đầu vào',
                'Thử lại sau vài phút',
                'Liên hệ hỗ trợ nếu lỗi tiếp tục xảy ra'
            ]
        }
    }
)

# ============================================================================
# LIABILITY CALCULATION API DOCUMENTATION
# ============================================================================

liability_calculation_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['match_id', 'bet_type_id', 'outcome'],
    properties={
        'match_id': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='ID của trận đấu',
            example='match_456'
        ),
        'bet_type_id': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='ID của loại cược',
            example='bet_type_789'
        ),
        'outcome': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Kết quả được chọn',
            example='Home Win'
        )
    }
)

liability_calculation_response = openapi.Response(
    description='Tính toán liability thành công',
    examples={
        'application/json': {
            'match_id': 'match_456',
            'bet_type_id': 'bet_type_789',
            'outcome': 'Home Win',
            'current_liability': 1500.0,
            'total_bets': 25,
            'average_stake': 60.0,
            'max_stake': 200.0,
            'last_updated': '2024-01-15T10:30:00Z'
        }
    }
)

# ============================================================================
# USER RISK LIMITS API DOCUMENTATION
# ============================================================================

user_risk_limits_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['user_id'],
    properties={
        'user_id': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='ID của người dùng',
            example='user_123'
        )
    }
)

user_risk_limits_response = openapi.Response(
    description='Thông tin giới hạn rủi ro của user',
    examples={
        'application/json': {
            'user_id': 'user_123',
            'max_stake': 1000.0,
            'daily_limit': 5000.0,
            'today_stake': 1200.0,
            'remaining_daily_limit': 3800.0,
            'risk_level': 'MEDIUM',
            'last_updated': '2024-01-15T10:30:00Z'
        }
    }
)

# ============================================================================
# MARKET STATUS API DOCUMENTATION
# ============================================================================

market_status_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['match_id'],
    properties={
        'match_id': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='ID của trận đấu',
            example='match_456'
        )
    }
)

market_status_response = openapi.Response(
    description='Trạng thái thị trường',
    examples={
        'application/json': {
            'match_id': 'match_456',
            'status': 'MARKET_ACTIVE',
            'match_status': 'LIVE',
            'suspension_info': None,
            'last_updated': '2024-01-15T10:30:00Z'
        }
    }
)

market_suspended_response = openapi.Response(
    description='Thị trường bị tạm dừng',
    examples={
        'application/json': {
            'match_id': 'match_456',
            'status': 'MARKET_SUSPENDED',
            'suspension_reason': 'RISK_MANAGEMENT',
            'suspension_description': 'Tạm dừng do vượt ngưỡng rủi ro',
            'suspended_at': '2024-01-15T10:25:00Z',
            'suspended_by': 'SYSTEM',
            'last_updated': '2024-01-15T10:25:00Z'
        }
    }
)

# ============================================================================
# ERROR CODES DOCUMENTATION
# ============================================================================

error_codes = {
    '400': {
        'description': 'Bad Request - Dữ liệu đầu vào không hợp lệ',
        'examples': {
            'VALIDATION_ERROR': {
                'summary': 'Validation Error',
                'value': {
                    'approved': False,
                    'error': 'Dữ liệu đầu vào không hợp lệ',
                    'error_details': {
                        'error_type': 'ValidationError',
                        'error_category': 'VALIDATION_ERROR',
                        'error_message': 'Missing required field: user_id',
                        'timestamp': '2024-01-15T10:30:00Z'
                    }
                }
            }
        }
    },
    '401': {
        'description': 'Unauthorized - Không có quyền truy cập',
        'examples': {
            'PERMISSION_ERROR': {
                'summary': 'Permission Error',
                'value': {
                    'approved': False,
                    'error': 'Không có quyền truy cập tính năng này',
                    'error_details': {
                        'error_type': 'PermissionDenied',
                        'error_category': 'PERMISSION_ERROR',
                        'error_message': 'User does not have required permissions',
                        'timestamp': '2024-01-15T10:30:00Z'
                    }
                }
            }
        }
    },
    '404': {
        'description': 'Not Found - Không tìm thấy tài nguyên',
        'examples': {
            'RESOURCE_NOT_FOUND': {
                'summary': 'Resource Not Found',
                'value': {
                    'approved': False,
                    'error': 'Không tìm thấy thông tin cần thiết',
                    'error_details': {
                        'error_type': 'NotFound',
                        'error_category': 'RESOURCE_ERROR',
                        'error_message': 'Match not found: match_999',
                        'timestamp': '2024-01-15T10:30:00Z'
                    }
                }
            }
        }
    },
    '500': {
        'description': 'Internal Server Error - Lỗi hệ thống',
        'examples': {
            'SYSTEM_ERROR': {
                'summary': 'System Error',
                'value': {
                    'approved': False,
                    'error': 'Lỗi hệ thống, vui lòng liên hệ hỗ trợ',
                    'error_details': {
                        'error_type': 'SystemError',
                        'error_category': 'SYSTEM_ERROR',
                        'error_message': 'Database connection failed',
                        'timestamp': '2024-01-15T10:30:00Z'
                    }
                }
            }
        }
    }
}

# ============================================================================
# RATE LIMITING DOCUMENTATION
# ============================================================================

rate_limiting_info = """
## Rate Limiting

Risk Management Service áp dụng rate limiting để đảm bảo hiệu suất và bảo mật:

### Limits:
- **Risk Check API**: 100 requests/minute per user
- **Liability Calculation**: 50 requests/minute per user  
- **User Risk Limits**: 200 requests/minute per user
- **Market Status**: 300 requests/minute per user

### Headers:
- `X-RateLimit-Limit`: Giới hạn requests trong time window
- `X-RateLimit-Remaining`: Số requests còn lại
- `X-RateLimit-Reset`: Thời gian reset (Unix timestamp)

### Response khi vượt limit:
```json
{
    "error": "Rate limit exceeded",
    "retry_after": 60,
    "limit": 100,
    "window": "1 minute"
}
```
"""

# ============================================================================
# API ENDPOINTS SUMMARY
# ============================================================================

api_endpoints_summary = """
## API Endpoints Summary

### 1. Risk Check API
- **POST** `/api/v1/risk/risk-check/check_bet/`
- **Mô tả**: Kiểm tra rủi ro của một bet
- **Rate Limit**: 100 requests/minute per user

### 2. Liability Calculation API  
- **GET** `/api/v1/risk/liability/calculate/`
- **Mô tả**: Tính toán liability hiện tại cho outcome
- **Rate Limit**: 50 requests/minute per user

### 3. User Risk Limits API
- **GET** `/api/v1/risk/user/{user_id}/limits/`
- **Mô tả**: Lấy thông tin giới hạn rủi ro của user
- **Rate Limit**: 200 requests/minute per user

### 4. Market Status API
- **GET** `/api/v1/risk/market/{match_id}/status/`
- **Mô tả**: Kiểm tra trạng thái thị trường
- **Rate Limit**: 300 requests/minute per user

### 5. Risk Dashboard API
- **GET** `/api/v1/risk/dashboard/`
- **Mô tả**: Dashboard tổng quan rủi ro
- **Rate Limit**: 30 requests/minute per user

### 6. Circuit Breaker API
- **GET** `/api/v1/risk/circuit-breakers/status/`
- **Mô tả**: Trạng thái circuit breakers
- **Rate Limit**: 50 requests/minute per user
"""

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

usage_examples = """
## Usage Examples

### 1. Kiểm tra rủi ro bet mới

```bash
curl -X POST "http://localhost:8000/api/v1/risk/risk-check/check_bet/" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{
    "user_id": "user_123",
    "match_id": "match_456", 
    "bet_type_id": "bet_type_789",
    "outcome": "Home Win",
    "stake_amount": 100.00,
    "odds_value": 2.00
  }'
```

### 2. Tính toán liability

```bash
curl -X GET "http://localhost:8000/api/v1/risk/liability/calculate/?match_id=match_456&bet_type_id=bet_type_789&outcome=Home%20Win" \\
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Kiểm tra giới hạn user

```bash
curl -X GET "http://localhost:8000/api/v1/risk/user/user_123/limits/" \\
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Kiểm tra trạng thái thị trường

```bash
curl -X GET "http://localhost:8000/api/v1/risk/market/match_456/status/" \\
  -H "Authorization: Bearer YOUR_TOKEN"
```
"""

# ============================================================================
# INTEGRATION GUIDE
# ============================================================================

integration_guide = """
## Integration Guide

### 1. Authentication
Tất cả API endpoints yêu cầu authentication token:
```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

### 2. Error Handling
Luôn kiểm tra response status và error fields:
```python
response = requests.post(risk_check_url, json=bet_data, headers=headers)
if response.status_code == 200:
    result = response.json()
    if result.get('approved'):
        # Bet được chấp nhận
        process_bet(result)
    else:
        # Bet bị từ chối
        handle_rejection(result)
else:
    # Lỗi hệ thống
    handle_error(response)
```

### 3. Retry Logic
Áp dụng retry logic cho transient errors:
```python
import time
from requests.exceptions import RequestException

def risk_check_with_retry(bet_data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(risk_check_url, json=bet_data, timeout=10)
            return response.json()
        except RequestException as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 4. Webhook Integration
Đăng ký webhook để nhận thông báo real-time:
```python
webhook_data = {
    'url': 'https://your-service.com/webhooks/risk-alerts',
    'events': ['risk_threshold_exceeded', 'market_suspended', 'circuit_breaker_triggered']
}

response = requests.post(webhook_registration_url, json=webhook_data)
```

### 5. Monitoring & Alerting
Sử dụng health check endpoints để monitoring:
```python
# Health check
health_response = requests.get(f"{base_url}/api/v1/risk/health/")
if health_response.status_code != 200:
    send_alert("Risk Management Service is down")

# Metrics
metrics_response = requests.get(f"{base_url}/api/v1/risk/metrics/")
metrics = metrics_response.json()
if metrics['risk_level'] == 'HIGH':
    send_alert("High risk level detected")
```
"""

# Export all documentation components
__all__ = [
    'risk_check_request_body',
    'risk_check_success_response', 
    'risk_check_rejected_response',
    'risk_check_error_response',
    'liability_calculation_request_body',
    'liability_calculation_response',
    'user_risk_limits_request_body',
    'user_risk_limits_response',
    'market_status_request_body',
    'market_status_response',
    'market_suspended_response',
    'error_codes',
    'rate_limiting_info',
    'api_endpoints_summary',
    'usage_examples',
    'integration_guide'
]
