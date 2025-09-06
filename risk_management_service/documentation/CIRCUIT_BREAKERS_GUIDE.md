# Hướng Dẫn Sử Dụng Circuit Breakers

## Tổng Quan

Circuit Breakers là hệ thống quản lý rủi ro tự động sử dụng rule-based triggers để phát hiện và phản ứng với các tình huống bất thường trong hệ thống cá cược. Hệ thống này được thiết kế để tiết kiệm chi phí bằng cách không sử dụng Machine Learning.

## Tính Năng Chính

### 1. Các Loại Trigger
- **Volume Spike**: Phát hiện tăng đột biến về khối lượng cá cược
- **Liability Threshold**: Kiểm soát ngưỡng trách nhiệm pháp lý
- **Odds Volatility**: Phát hiện biến động odds bất thường
- **Pattern Detection**: Phát hiện patterns đáng ngờ
- **Time-based**: Rules dựa trên thời gian
- **Combination**: Kết hợp nhiều điều kiện

### 2. Mức Độ Nghiêm Trọng
- **LOW**: Mức độ thấp
- **MEDIUM**: Mức độ trung bình
- **HIGH**: Mức độ cao
- **CRITICAL**: Mức độ nghiêm trọng - cần hành động ngay lập tức

### 3. Các Hành Động
- **LOG_ONLY**: Chỉ ghi log
- **ALERT**: Gửi cảnh báo
- **SUSPEND_MARKET**: Đình chỉ thị trường cụ thể
- **SUSPEND_SPORT**: Đình chỉ toàn bộ môn thể thao
- **REDUCE_LIMITS**: Giảm giới hạn cá cược
- **EMERGENCY_STOP**: Dừng khẩn cấp toàn bộ giao dịch

## Cách Sử Dụng

### 1. Chạy Monitoring

#### Chạy một lần:
```bash
python manage.py run_circuit_breakers --once --verbose
```

#### Chạy liên tục:
```bash
python manage.py run_circuit_breakers --interval 30 --verbose
```

#### Tạo default rules và chạy:
```bash
python manage.py run_circuit_breakers --create-rules --once --verbose
```

### 2. Các Tham Số

- `--interval`: Khoảng thời gian kiểm tra (giây), mặc định: 60
- `--once`: Chạy một lần và thoát
- `--create-rules`: Tạo default rules trước khi chạy
- `--verbose`: Hiển thị thông tin chi tiết

### 3. Ví Dụ Sử Dụng

#### Kiểm tra mỗi 30 giây:
```bash
python manage.py run_circuit_breakers --interval 30 --verbose
```

#### Tạo rules và chạy test:
```bash
python manage.py run_circuit_breakers --create-rules --once --verbose
```

## Cấu Hình Rules

### 1. Volume Spike Rule
```python
{
    'name': 'High Volume Spike Alert',
    'trigger_type': 'VOLUME_SPIKE',
    'severity': 'MEDIUM',
    'action': 'ALERT',
    'rule_parameters': {
        'spike_threshold': 3.0,      # 3x normal volume
        'time_window': 60,           # 60 minutes
        'comparison_period': 7       # 7 days historical
    }
}
```

### 2. Liability Threshold Rule
```python
{
    'name': 'Critical Liability Threshold',
    'trigger_type': 'LIABILITY_THRESHOLD',
    'severity': 'CRITICAL',
    'action': 'SUSPEND_SPORT',
    'rule_parameters': {
        'threshold_percentage': 90.0,  # 90% of limit
        'scope': 'sport'
    }
}
```

### 3. Odds Volatility Rule
```python
{
    'name': 'Odds Manipulation Detection',
    'trigger_type': 'ODDS_VOLATILITY',
    'severity': 'HIGH',
    'action': 'SUSPEND_MARKET',
    'rule_parameters': {
        'volatility_threshold': 25.0,  # 25% change
        'time_window': 10,             # 10 minutes
        'change_frequency': 3          # 3 changes in window
    }
}
```

### 4. Pattern Detection Rule
```python
{
    'name': 'Coordinated Betting Alert',
    'trigger_type': 'PATTERN_DETECTION',
    'severity': 'HIGH',
    'action': 'ALERT',
    'rule_parameters': {
        'pattern_type': 'coordinated_betting',
        'user_threshold': 15,          # 15+ users
        'time_window': 30,             # 30 minutes
        'amount_similarity': 0.05      # 5% variance
    }
}
```

## Cấu Trúc Dữ Liệu

### 1. CircuitBreakerRule
- `id`: UUID primary key
- `name`: Tên rule
- `description`: Mô tả rule
- `trigger_type`: Loại trigger
- `severity`: Mức độ nghiêm trọng
- `action`: Hành động thực hiện
- `target_sports`: Danh sách môn thể thao mục tiêu
- `target_bet_types`: Danh sách loại cược mục tiêu
- `rule_parameters`: Tham số cấu hình (JSON)
- `is_active`: Trạng thái hoạt động

### 2. CircuitBreakerEvent
- `id`: UUID primary key
- `rule`: Reference đến rule
- `triggered_at`: Thời gian trigger
- `trigger_data`: Dữ liệu gây trigger
- `action_taken`: Hành động đã thực hiện
- `sport_name`: Tên môn thể thao
- `bet_type_id`: ID loại cược
- `match_id`: ID trận đấu
- `suspension_id`: ID suspension (nếu có)
- `alert_id`: ID alert (nếu có)

## Monitoring và Logging

### 1. Log Levels
- **INFO**: Thông tin bình thường
- **WARNING**: Cảnh báo khi rule được trigger
- **ERROR**: Lỗi trong quá trình xử lý

### 2. Cache
- Sử dụng Django cache để lưu trữ dữ liệu tạm thời
- Timeout: 5 phút
- Giảm thiểu truy vấn database

### 3. Performance
- Kiểm tra rules theo batch
- Sử dụng database transactions
- Async processing cho các actions

## Tùy Chỉnh và Mở Rộng

### 1. Thêm Rule Mới
```python
# Tạo rule mới
rule = CircuitBreakerRule.objects.create(
    name='Custom Rule',
    trigger_type='VOLUME_SPIKE',
    severity='HIGH',
    action='SUSPEND_MARKET',
    rule_parameters={
        'custom_parameter': 'value'
    }
)
```

### 2. Thêm Trigger Type Mới
```python
# Trong class AdvancedCircuitBreaker
def _check_custom_trigger(self, rule: CircuitBreakerRule) -> Dict[str, Any]:
    # Implement custom logic
    pass

# Trong _check_rule method
elif rule.trigger_type == 'CUSTOM_TRIGGER':
    return self._check_custom_trigger(rule)
```

### 3. Thêm Action Mới
```python
# Trong _execute_rule_action method
elif rule.action == 'CUSTOM_ACTION':
    custom_result = self._execute_custom_action(rule, trigger_result, event)
    action_result.update(custom_result)
    action_result['success'] = True
```

## Troubleshooting

### 1. Lỗi Thường Gặp

#### Import Error
```bash
ModuleNotFoundError: No module named 'risk_manager'
```
**Giải pháp**: Đảm bảo đang chạy từ thư mục gốc của Django project

#### Database Error
```bash
django.db.utils.OperationalError: no such table
```
**Giải pháp**: Chạy migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Permission Error
```bash
Permission denied: cannot create file
```
**Giải pháp**: Kiểm tra quyền ghi file và thư mục

### 2. Debug Mode

#### Verbose Logging
```bash
python manage.py run_circuit_breakers --verbose --once
```

#### Check Rules Status
```python
from risk_manager.circuit_breakers import CircuitBreakerRule

# Kiểm tra active rules
active_rules = CircuitBreakerRule.objects.filter(is_active=True)
for rule in active_rules:
    print(f"{rule.name}: {rule.trigger_type} - {rule.severity}")
```

## Bảo Mật

### 1. Access Control
- Chỉ admin users mới có thể tạo/sửa rules
- Audit log cho tất cả thay đổi
- IP address tracking

### 2. Data Validation
- Validate tất cả input parameters
- Sanitize JSON data
- Rate limiting cho API calls

### 3. Monitoring
- Real-time monitoring
- Alert notifications
- Performance metrics

## Tài Liệu Tham Khảo

- [Django Models Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Management Commands](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Risk Management Best Practices](https://www.iso.org/iso-31000-risk-management.html)

## Liên Hệ Hỗ Trợ

Nếu gặp vấn đề hoặc cần hỗ trợ:
- Tạo issue trên repository
- Liên hệ team development
- Kiểm tra logs và documentation
