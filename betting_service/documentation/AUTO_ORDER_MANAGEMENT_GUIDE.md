# 🎯 **HƯỚNG DẪN SỬ DỤNG TÍNH NĂNG "CHỐT LỜI & CẮT LỖ" TỰ ĐỘNG**

## 📋 **TỔNG QUAN**

Tính năng "Chốt Lời & Cắt Lỗ" tự động (Auto Order Management) cho phép người chơi thiết lập các ngưỡng tự động để hệ thống thực hiện Cash Out khi phiếu cược đạt đến mức lợi nhuận hoặc thua lỗ mong muốn.

### **🎯 Tính Năng Chính**

- **Chốt Lời (Take Profit)**: Tự động Cash Out khi đạt mức lợi nhuận mục tiêu
- **Cắt Lỗ (Stop Loss)**: Tự động Cash Out khi giảm xuống mức thua lỗ tối đa
- **Giám sát tự động**: Hệ thống quét liên tục mỗi 10 giây
- **Quản lý thông minh**: Tự động tạm dừng khi thị trường bị khóa

## 🚀 **CÁCH SỬ DỤNG**

### **1. Thiết Lập Lệnh Tự Động**

#### **API Endpoint**
```
POST /api/auto-orders/setup/
```

#### **Request Body**
```json
{
    "bet_slip_id": 123,
    "take_profit_threshold": 150.00,
    "stop_loss_threshold": 80.00
}
```

#### **Response**
```json
{
    "success": true,
    "message": "Lệnh tự động đã được thiết lập thành công",
    "bet_slip_id": 123,
    "auto_order_status": "ACTIVE",
    "take_profit_threshold": 150.00,
    "stop_loss_threshold": 80.00
}
```

### **2. Kiểm Tra Trạng Thái Lệnh Tự Động**

#### **API Endpoint**
```
GET /api/auto-orders/status/{bet_slip_id}/
```

#### **Response**
```json
{
    "bet_slip_id": 123,
    "auto_order_status": "ACTIVE",
    "take_profit_threshold": 150.00,
    "stop_loss_threshold": 80.00,
    "auto_order_created_at": "2024-01-15T10:30:00Z",
    "auto_order_triggered_at": null,
    "auto_order_reason": null,
    "auto_order_enabled": true,
    "current_cashout_value": 120.00,
    "can_setup_auto_order": false,
    "has_active_auto_order": true
}
```

### **3. Hủy Lệnh Tự Động**

#### **API Endpoint**
```
POST /api/auto-orders/cancel/
```

#### **Request Body**
```json
{
    "bet_slip_id": 123
}
```

#### **Response**
```json
{
    "success": true,
    "message": "Lệnh tự động đã được hủy thành công",
    "bet_slip_id": 123
}
```

### **4. Xem Danh Sách Lệnh Tự Động**

#### **API Endpoint**
```
GET /api/auto-orders/user/
```

#### **Response**
```json
{
    "auto_orders": [
        {
            "id": 123,
            "user": 1,
            "bet_type": "SINGLE",
            "bet_status": "CONFIRMED",
            "total_stake": 100.00,
            "auto_order_status": "ACTIVE",
            "take_profit_threshold": 150.00,
            "stop_loss_threshold": 80.00
        }
    ],
    "total_count": 1
}
```

## 🔧 **CẤU HÌNH HỆ THỐNG**

### **1. Biến Môi Trường**

```bash
# Khoảng thời gian giám sát (giây)
AUTO_CASHOUT_MONITORING_INTERVAL=10

# Số lượng phiếu cược xử lý mỗi batch
AUTO_CASHOUT_MAX_BATCH_SIZE=100
```

### **2. Celery Beat Schedule**

```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'monitor-auto-orders': {
        'task': 'betting.monitor_auto_orders',
        'schedule': 10.0,  # Mỗi 10 giây
    },
    'cleanup-completed-auto-orders': {
        'task': 'betting.cleanup_completed_auto_orders',
        'schedule': crontab(hour=2, minute=0),  # Mỗi ngày lúc 2:00 AM
    },
}
```

## 📊 **TRẠNG THÁI LỆNH TỰ ĐỘNG**

| **Trạng Thái** | **Mô Tả** | **Hành Động Tiếp Theo** |
|----------------|------------|-------------------------|
| `INACTIVE` | Không hoạt động | Có thể thiết lập |
| `ACTIVE` | Đang hoạt động | Hệ thống đang giám sát |
| `TRIGGERED` | Đã kích hoạt | Đang thực hiện Cash Out |
| `COMPLETED` | Đã hoàn thành | Lệnh đã hoàn tất |
| `CANCELLED` | Đã hủy | Không thể sử dụng lại |
| `SUSPENDED` | Tạm dừng | Chờ khôi phục |

## ⚠️ **LƯU Ý QUAN TRỌNG**

### **1. Điều Kiện Thiết Lập**

- Phiếu cược phải ở trạng thái `CONFIRMED`
- Phải có ít nhất một ngưỡng (chốt lời hoặc cắt lỗ)
- Phiếu cược phải hỗ trợ Cash Out
- Không được có lệnh tự động đang hoạt động

### **2. Quy Tắc Nghiệp Vụ**

- Lệnh tự động sẽ bị tạm dừng khi thị trường bị khóa
- Hệ thống sẽ tự động khôi phục khi thị trường mở lại
- Người dùng có thể hủy lệnh bất cứ lúc nào
- Lệnh tự động chỉ áp dụng cho phiếu cược đang hoạt động

### **3. Giới Hạn Kỹ Thuật**

- Giám sát mỗi 10 giây để đảm bảo hiệu suất
- Xử lý theo batch để tránh quá tải
- Tự động retry nếu có lỗi
- Log đầy đủ để theo dõi và debug

## 🧪 **KIỂM THỬ**

### **1. Test Thiết Lập Lệnh Tự Động**

```bash
# Test thiết lập thành công
curl -X POST http://localhost:8001/api/auto-orders/setup/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "bet_slip_id": 123,
    "take_profit_threshold": 150.00,
    "stop_loss_threshold": 80.00
  }'
```

### **2. Test Kiểm Tra Trạng Thái**

```bash
# Test kiểm tra trạng thái
curl -X GET http://localhost:8001/api/auto-orders/status/123/ \
  -H "Authorization: Bearer {token}"
```

### **3. Test Hủy Lệnh**

```bash
# Test hủy lệnh
curl -X POST http://localhost:8001/api/auto-orders/cancel/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"bet_slip_id": 123}'
```

## 📈 **GIÁM SÁT VÀ BẢO TRÌ**

### **1. Log Files**

```bash
# Theo dõi log giám sát
tail -f logs/betting_service.log | grep "Auto Order"

# Theo dõi lỗi
tail -f logs/betting_service.log | grep "ERROR.*Auto Order"
```

### **2. Metrics Dashboard**

```bash
# Thống kê lệnh tự động
curl -X GET http://localhost:8001/api/auto-orders/statistics/ \
  -H "Authorization: Bearer {admin_token}"
```

### **3. Health Check**

```bash
# Kiểm tra trạng thái service
curl -X GET http://localhost:8001/api/health/
```

## 🔍 **TROUBLESHOOTING**

### **1. Lệnh Tự Động Không Hoạt Động**

- Kiểm tra trạng thái phiếu cược
- Kiểm tra quyền Cash Out
- Kiểm tra log lỗi
- Kiểm tra kết nối Risk Management Service

### **2. Giám Sát Không Chạy**

- Kiểm tra Celery worker
- Kiểm tra Celery beat
- Kiểm tra cấu hình môi trường
- Kiểm tra log task

### **3. Performance Issues**

- Giảm `AUTO_CASHOUT_MONITORING_INTERVAL`
- Giảm `AUTO_CASHOUT_MAX_BATCH_SIZE`
- Kiểm tra database indexes
- Kiểm tra cache configuration

## 📚 **TÀI LIỆU THAM KHẢO**

- [Cash Out Service Documentation](./CASH_OUT_SERVICE_GUIDE.md)
- [Risk Management Integration](./RISK_MANAGEMENT_INTEGRATION.md)
- [Saga Pattern Implementation](./SAGA_PATTERN_GUIDE.md)
- [Celery Task Management](./CELERY_TASK_GUIDE.md)

---

**📞 Hỗ Trợ Kỹ Thuật**: betting_service@company.com  
**🐛 Báo Cáo Lỗi**: https://github.com/company/betting-service/issues  
**📖 API Documentation**: https://api.company.com/betting-service/docs/
