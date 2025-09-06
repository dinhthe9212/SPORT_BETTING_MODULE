# 🔄 **HƯỚNG DẪN SỬ DỤNG AUTOMATED WORKFLOWS SERVICE**

## **📋 TỔNG QUAN**

Automated Workflows Service là service tự động hóa quy trình xử lý rủi ro, giúp xử lý rủi ro nhanh và chính xác thông qua các workflow được định nghĩa sẵn.

## **🎯 CÁC WORKFLOW CÓ SẴN**

### **1. Critical Risk Workflow**
- **Mục đích**: Xử lý rủi ro CRITICAL
- **Các bước**:
  1. Immediate Alert (Bắt buộc)
  2. Emergency Suspension (Bắt buộc)
  3. Notify Management (Bắt buộc)
  4. Activate Circuit Breakers (Tùy chọn)

### **2. High Risk Workflow**
- **Mục đích**: Xử lý rủi ro HIGH
- **Các bước**:
  1. High Priority Alert (Bắt buộc)
  2. Selective Suspension (Tùy chọn)
  3. Increase Monitoring (Bắt buộc)

### **3. Medium Risk Workflow**
- **Mục đích**: Xử lý rủi ro MEDIUM
- **Các bước**:
  1. Standard Alert (Bắt buộc)
  2. Monitor Closely (Bắt buộc)
  3. Prepare Response (Tùy chọn)

### **4. Low Risk Workflow**
- **Mục đích**: Xử lý rủi ro LOW
- **Các bước**:
  1. Log Event (Bắt buộc)
  2. Continue Monitoring (Bắt buộc)

### **5. Emergency Stop Workflow**
- **Mục đích**: Xử lý tình huống khẩn cấp
- **Các bước**:
  1. Global Suspension (Bắt buộc)
  2. Emergency Notifications (Bắt buộc)
  3. Activate Backup Systems (Bắt buộc)
  4. Contact Authorities (Tùy chọn)

## **🔧 CÁCH SỬ DỤNG**

### **API Endpoints**

#### **1. Thực thi Workflow Cụ thể**
```bash
POST /api/risk-management/automated-workflows/execute_workflow/
```

**Request Body:**
```json
{
    "workflow_name": "critical_risk",
    "event_data": {
        "event_type": "HIGH_VOLATILITY_DETECTED",
        "risk_level": "CRITICAL",
        "sport_name": "football",
        "match_id": "match_123",
        "description": "Extreme odds volatility detected",
        "auto_circuit_breaker": true
    }
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "workflow_name": "critical_risk",
        "execution_id": "critical_risk_1703123456",
        "start_time": 1703123456.123,
        "event_data": {...},
        "steps": [
            {
                "step_name": "Immediate Alert",
                "description": "Gửi cảnh báo ngay lập tức cho tất cả admin",
                "required": true,
                "status": "success",
                "execution_time": 0.15,
                "details": {
                    "alert_id": "alert_456",
                    "notifications_sent": 3,
                    "status": "success"
                }
            },
            {
                "step_name": "Emergency Suspension",
                "description": "Tạm dừng giao dịch khẩn cấp",
                "required": true,
                "status": "success",
                "execution_time": 0.23,
                "details": {
                    "suspension_id": "suspension_789",
                    "suspension_type": "GLOBAL",
                    "status": "success"
                }
            }
        ],
        "overall_status": "success",
        "errors": [],
        "execution_time": 0.85,
        "end_time": 1703123457.008
    }
}
```

#### **2. Tự động Phát hiện và Thực thi Workflow**
```bash
POST /api/risk-management/automated-workflows/auto_detect_and_execute/
```

**Request Body:**
```json
{
    "event_data": {
        "event_type": "UNUSUAL_BETTING_PATTERN",
        "risk_level": "HIGH",
        "sport_name": "basketball",
        "bet_type_id": "bet_type_456",
        "description": "Unusual betting pattern detected",
        "auto_suspend": true
    }
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "workflow_name": "high_risk",
        "execution_id": "high_risk_1703123456",
        "overall_status": "success",
        "execution_time": 0.65
    }
}
```

#### **3. Lấy Trạng thái Workflow Execution**
```bash
GET /api/risk-management/automated-workflows/get_workflow_status/?execution_id=critical_risk_1703123456
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "workflow_name": "critical_risk",
        "execution_id": "critical_risk_1703123456",
        "overall_status": "success",
        "steps": [...],
        "execution_time": 0.85
    }
}
```

#### **4. Lấy Lịch sử Workflow Executions**
```bash
GET /api/risk-management/automated-workflows/get_workflow_history/?limit=10
```

**Response:**
```json
{
    "status": "success",
    "result": [
        {
            "workflow_name": "critical_risk",
            "execution_id": "critical_risk_1703123456",
            "overall_status": "success",
            "execution_time": 0.85
        },
        {
            "workflow_name": "high_risk",
            "execution_id": "high_risk_1703123400",
            "overall_status": "success",
            "execution_time": 0.65
        }
    ]
}
```

#### **5. Escalate Critical Risks**
```bash
POST /api/risk-management/automated-workflows/escalate_critical_risks/
```

**Request Body:**
```json
{
    "risk_level": "CRITICAL"
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "status": "success",
        "escalation_sent": true,
        "notification_result": {...},
        "escalation_data": {
            "risk_level": "CRITICAL",
            "escalation_time": "2023-12-21T10:30:00+00:00",
            "escalation_reason": "Risk level CRITICAL requires immediate attention"
        }
    }
}
```

#### **6. Tự động Thông báo Stakeholders**
```bash
POST /api/risk-management/automated-workflows/auto_notify_stakeholders/
```

**Request Body:**
```json
{
    "risk_event": {
        "event_type": "MARKET_MANIPULATION_SUSPECTED",
        "risk_level": "HIGH",
        "sport_name": "football",
        "description": "Suspicious betting activity detected"
    }
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "status": "success",
        "stakeholders_notified": 2,
        "notification_results": [...]
    }
}
```

## **⚙️ CẤU HÌNH WORKFLOW**

### **Workflow Configuration**
```python
# Tùy chỉnh workflow steps
class CustomWorkflowStep(WorkflowStep):
    def __init__(self, name, condition, action, description="", required=True):
        super().__init__(name, condition, action, description, required)

# Tạo custom workflow
custom_workflow = [
    CustomWorkflowStep(
        name="Custom Alert",
        condition=lambda event: event.get('custom_condition', False),
        action=custom_alert_action,
        description="Custom alert action",
        required=True
    )
]
```

### **Condition Functions**
```python
# Điều kiện đơn giản
simple_condition = lambda event: event.get('risk_level') == 'CRITICAL'

# Điều kiện phức tạp
complex_condition = lambda event: (
    event.get('risk_level') == 'HIGH' and
    event.get('sport_name') == 'football' and
    event.get('bet_amount', 0) > 10000
)

# Điều kiện với logic phức tạp
def advanced_condition(event):
    risk_level = event.get('risk_level')
    time_of_day = event.get('time_of_day', 0)
    
    if risk_level == 'CRITICAL':
        return True
    elif risk_level == 'HIGH' and time_of_day > 18:  # Sau 6h tối
        return True
    return False
```

### **Action Functions**
```python
# Action đơn giản
def simple_action(event_data):
    return {
        'status': 'success',
        'action_performed': 'simple_action',
        'timestamp': timezone.now().isoformat()
    }

# Action phức tạp với database operations
def complex_action(event_data):
    try:
        # Tạo risk alert
        alert = RiskAlert.objects.create(
            alert_type='CUSTOM_ALERT',
            severity='HIGH',
            title=f"Custom Alert: {event_data.get('event_type')}",
            message=event_data.get('description', ''),
            related_data=event_data,
            status='ACTIVE'
        )
        
        # Gửi notification
        notification_result = send_custom_notification(alert)
        
        return {
            'status': 'success',
            'alert_id': str(alert.id),
            'notification_result': notification_result
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
```

## **📊 MONITORING VÀ LOGGING**

### **Workflow Execution Logs**
```python
# Log workflow execution
logger.info(f"Workflow {workflow_name} started for event: {event_data.get('event_type')}")
logger.info(f"Workflow step {step.name} executed successfully")
logger.info(f"Workflow {workflow_name} completed in {execution_time:.2f}s")

# Log errors
logger.error(f"Workflow step {step.name} failed: {e}")
logger.error(f"Workflow {workflow_name} execution failed: {e}")
```

### **Audit Trail**
```python
# Tự động ghi audit log cho mỗi workflow execution
RiskAuditLog.objects.create(
    action_type='WORKFLOW_EXECUTION',
    action_description=f"Workflow {workflow_name} executed",
    user_id='AUTOMATED_WORKFLOW',
    related_object_type='WorkflowExecution',
    related_object_id=execution_id,
    action_details={
        'workflow_name': workflow_name,
        'event_data': event_data,
        'results': results
    },
    success=True
)
```

## **🔍 TROUBLESHOOTING**

### **Common Issues**

#### **1. Workflow Step Failed**
```python
# Kiểm tra step execution
step_result = workflow_service._execute_workflow_step(step, event_data)
if step_result['status'] == 'error':
    print(f"Step {step.name} failed: {step_result['error']}")
    
# Kiểm tra step condition
if step.condition(event_data):
    print(f"Step {step.name} condition met")
else:
    print(f"Step {step.name} condition not met")
```

#### **2. Workflow Not Found**
```python
# Kiểm tra available workflows
available_workflows = list(workflow_service.workflows.keys())
print(f"Available workflows: {available_workflows}")

# Kiểm tra workflow name
if workflow_name in workflow_service.workflows:
    print(f"Workflow {workflow_name} exists")
else:
    print(f"Workflow {workflow_name} not found")
```

#### **3. Event Data Issues**
```python
# Validate event data
required_fields = ['event_type', 'risk_level']
for field in required_fields:
    if field not in event_data:
        print(f"Missing required field: {field}")

# Check data types
if not isinstance(event_data.get('risk_level'), str):
    print("risk_level must be a string")
```

### **Debug Mode**
```python
# Bật debug logging
LOGGING = {
    'loggers': {
        'risk_manager.workflow': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}

# Debug workflow execution
workflow_service.workflows['critical_risk'][0].condition(event_data)
workflow_service.workflows['critical_risk'][0].action(event_data)
```

## **📈 BEST PRACTICES**

### **1. Workflow Design**
- **Single Responsibility**: Mỗi step chỉ làm một việc
- **Error Handling**: Luôn có error handling cho mỗi step
- **Logging**: Log đầy đủ thông tin execution
- **Audit Trail**: Ghi lại tất cả actions

### **2. Performance**
- **Async Processing**: Sử dụng async cho các operations chậm
- **Batch Processing**: Xử lý nhiều items cùng lúc
- **Caching**: Cache data thường xuyên sử dụng
- **Monitoring**: Monitor execution time và resource usage

### **3. Security**
- **Input Validation**: Validate tất cả input data
- **Access Control**: Kiểm tra quyền truy cập
- **Audit Logging**: Log tất cả security events
- **Error Handling**: Không expose sensitive information

## **🚨 EMERGENCY PROCEDURES**

### **Critical Workflow Failures**
1. **Immediate Actions:**
   - Stop all automated workflows
   - Activate manual intervention mode
   - Notify emergency response team

2. **Investigation:**
   - Check workflow execution logs
   - Analyze failed steps
   - Identify root cause

3. **Recovery:**
   - Fix workflow issues
   - Restart automated workflows
   - Monitor recovery

### **Emergency Stop**
```python
# Emergency stop tất cả workflows
for workflow_name in workflow_service.workflows:
    workflow_service.workflows[workflow_name] = []
    
# Activate emergency mode
emergency_mode = True
```

## **📞 SUPPORT**

### **Contact Information**
- **Technical Support**: tech-support@company.com
- **Emergency Hotline**: +84-xxx-xxx-xxx
- **Documentation**: [Internal Wiki Link]

### **Escalation Matrix**
1. **Level 1**: System Administrator
2. **Level 2**: DevOps Engineer  
3. **Level 3**: System Architect
4. **Level 4**: CTO

---

**📝 Lưu ý**: Automated Workflows Service được thiết kế để tự động xử lý rủi ro. Trong trường hợp khẩn cấp, có thể can thiệp thủ công thông qua các API endpoints hoặc emergency procedures.
