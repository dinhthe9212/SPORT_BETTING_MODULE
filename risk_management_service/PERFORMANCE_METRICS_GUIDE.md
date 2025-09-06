# 📊 **HƯỚNG DẪN SỬ DỤNG PERFORMANCE METRICS SERVICE**

## **📋 TỔNG QUAN**

Performance Metrics Service là service đo lường hiệu quả hệ thống quản lý rủi ro, giúp biết hệ thống có hoạt động tốt không và đưa ra các khuyến nghị cải thiện.

## **🎯 CÁC TÍNH NĂNG CHÍNH**

### **1. System Performance Overview**
- Tổng quan hiệu suất hệ thống
- Overall performance score (0-100)
- Performance grade (EXCELLENT, GOOD, ACCEPTABLE, NEEDS_IMPROVEMENT, POOR)

### **2. Performance Metrics Categories**
- **Risk Detection Metrics**: Phát hiện rủi ro
- **Response Time Metrics**: Thời gian phản ứng
- **Accuracy Metrics**: Độ chính xác
- **Availability Metrics**: Tính khả dụng
- **Efficiency Metrics**: Hiệu quả

### **3. Performance Trends**
- Xu hướng hiệu suất theo thời gian
- Daily performance scores
- Performance changes analysis
- Trend consistency evaluation

### **4. Performance Recommendations**
- Khuyến nghị cải thiện hiệu suất
- Priority-based recommendations
- Actionable improvement steps

### **5. Performance Reports**
- Export performance data
- Multiple formats (JSON, CSV)
- Historical data analysis

## **🔧 CÁCH SỬ DỤNG**

### **API Endpoints**

#### **1. Lấy Tổng quan Hiệu suất Hệ thống**
```bash
GET /api/risk-management/performance-metrics/get_overview/?hours=24
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "period_hours": 24,
        "timestamp": "2023-12-21T10:30:00+00:00",
        "overall_score": 87.5,
        "performance_grade": "GOOD",
        "risk_detection": {
            "total_alerts": 45,
            "critical_alerts": 3,
            "high_alerts": 8,
            "alert_rate_per_hour": 1.88,
            "pattern_confirmation_rate": 92.3,
            "false_positive_rate": 7.7
        },
        "response_time": {
            "total_actions": 1250,
            "average_response_time": 0.156,
            "response_time_grade": "GOOD",
            "excellent_count": 890,
            "good_count": 320,
            "acceptable_count": 35,
            "poor_count": 5
        },
        "accuracy": {
            "overall_accuracy": 89.2,
            "accuracy_grade": "GOOD",
            "pattern_accuracy": 92.3,
            "alert_accuracy": 86.1
        },
        "availability": {
            "availability_percentage": 99.72,
            "availability_grade": "GOOD",
            "uptime_minutes": 1435,
            "downtime_minutes": 5
        },
        "efficiency": {
            "cache_hit_rate": 89.3,
            "processing_success_rate": 100.0,
            "auto_response_rate": 85.0
        },
        "execution_time": 0.45,
        "status": "success"
    }
}
```

#### **2. Lấy Xu hướng Hiệu suất**
```bash
GET /api/risk-management/performance-metrics/get_trends/?days=7
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "daily_scores": [
            {
                "date": "2023-12-21",
                "score": 87.5,
                "grade": "GOOD"
            },
            {
                "date": "2023-12-20",
                "score": 85.2,
                "grade": "GOOD"
            },
            {
                "date": "2023-12-19",
                "score": 82.8,
                "grade": "GOOD"
            }
        ],
        "performance_changes": {
            "score_change": 2.3,
            "change_percentage": 2.7,
            "trend_direction": "IMPROVING"
        },
        "trend_analysis": {
            "average_score": 85.2,
            "min_score": 82.8,
            "max_score": 87.5,
            "score_volatility": 4.7,
            "consistency": "HIGH"
        }
    }
}
```

#### **3. Lấy Khuyến nghị Cải thiện Hiệu suất**
```bash
GET /api/risk-management/performance-metrics/get_recommendations/
```

**Response:**
```json
{
    "status": "success",
    "result": [
        {
            "type": "response_time",
            "priority": "MEDIUM",
            "title": "Cải thiện thời gian phản ứng",
            "description": "Thời gian phản ứng trung bình có thể được cải thiện thêm. Hiện tại: 156ms, Mục tiêu: <100ms",
            "actions": [
                "Tối ưu hóa database indexes",
                "Implement query caching",
                "Sử dụng connection pooling",
                "Phân tích slow queries"
            ]
        },
        {
            "type": "efficiency",
            "priority": "LOW",
            "title": "Cải thiện cache hit rate",
            "description": "Cache hit rate có thể được tối ưu hóa thêm. Hiện tại: 89.3%, Mục tiêu: >95%",
            "actions": [
                "Review cache keys",
                "Adjust cache TTL",
                "Implement cache warming",
                "Monitor cache usage patterns"
            ]
        }
    ]
}
```

#### **4. Xuất Báo cáo Hiệu suất**
```bash
GET /api/risk-management/performance-metrics/export_report/?format=csv
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "format": "csv",
        "data": "Metric,Value,Grade,Status\nOverall Score,87.5,GOOD,Active\nAlert Rate,1.88/hour,MEDIUM,Active\nPattern Confirmation,92.3%,EXCELLENT,Active\nAvg Response Time,0.156s,GOOD,Active\nOverall Accuracy,89.2%,GOOD,Active\nSystem Availability,99.72%,EXCELLENT,Active",
        "filename": "performance_report_20231221_103000.csv"
    }
}
```

## **⚙️ CẤU HÌNH PERFORMANCE THRESHOLDS**

### **Default Thresholds**
```python
performance_thresholds = {
    'response_time': {
        'excellent': 0.1,    # < 100ms
        'good': 0.5,         # < 500ms
        'acceptable': 1.0,    # < 1s
        'poor': 2.0          # > 2s
    },
    'accuracy': {
        'excellent': 95,      # > 95%
        'good': 90,          # > 90%
        'acceptable': 80,     # > 80%
        'poor': 70           # < 70%
    },
    'availability': {
        'excellent': 99.9,    # > 99.9%
        'good': 99.5,        # > 99.5%
        'acceptable': 99.0,   # > 99.0%
        'poor': 95.0         # < 95%
    }
}
```

### **Custom Thresholds**
```python
# Tùy chỉnh thresholds
custom_thresholds = {
    'response_time': {
        'excellent': 0.05,   # < 50ms
        'good': 0.2,         # < 200ms
        'acceptable': 0.5,   # < 500ms
        'poor': 1.0          # > 1s
    }
}

# Cập nhật thresholds
metrics_service.performance_thresholds.update(custom_thresholds)
```

## **📊 INTERPRETING PERFORMANCE METRICS**

### **Overall Performance Score (0-100)**

#### **Score Ranges:**
- **90-100**: EXCELLENT - Hệ thống hoạt động xuất sắc
- **80-89**: GOOD - Hệ thống hoạt động tốt
- **70-79**: ACCEPTABLE - Hệ thống hoạt động chấp nhận được
- **60-69**: NEEDS_IMPROVEMENT - Cần cải thiện
- **0-59**: POOR - Hiệu suất kém

#### **Score Calculation:**
```python
# Weighted scoring
weights = {
    'risk_detection': 0.25,    # 25%
    'response_time': 0.20,     # 20%
    'accuracy': 0.25,          # 25%
    'availability': 0.20,      # 20%
    'efficiency': 0.10         # 10%
}

# Overall score = sum(component_score * weight)
```

### **Risk Detection Metrics**

#### **Key Indicators:**
- **Alert Rate**: Số cảnh báo mỗi giờ
  - < 5/hour: LOW (Tốt)
  - 5-15/hour: MEDIUM (Bình thường)
  - > 15/hour: HIGH (Cần chú ý)

- **Pattern Confirmation Rate**: Tỷ lệ phát hiện chính xác
  - > 95%: EXCELLENT
  - 90-95%: GOOD
  - 80-90%: ACCEPTABLE
  - < 80%: POOR

- **False Positive Rate**: Tỷ lệ cảnh báo sai
  - < 5%: EXCELLENT
  - 5-10%: GOOD
  - 10-20%: ACCEPTABLE
  - > 20%: POOR

### **Response Time Metrics**

#### **Performance Grades:**
- **EXCELLENT**: < 100ms
- **GOOD**: 100-500ms
- **ACCEPTABLE**: 500ms-1s
- **POOR**: > 1s

#### **Percentile Analysis:**
- **P95**: 95% requests hoàn thành trong thời gian này
- **P99**: 99% requests hoàn thành trong thời gian này

### **Accuracy Metrics**

#### **Overall Accuracy:**
- **EXCELLENT**: > 95%
- **GOOD**: 90-95%
- **ACCEPTABLE**: 80-90%
- **POOR**: < 80%

#### **Component Accuracy:**
- **Pattern Accuracy**: Độ chính xác phát hiện pattern
- **Alert Accuracy**: Độ chính xác cảnh báo

### **Availability Metrics**

#### **Uptime Percentage:**
- **EXCELLENT**: > 99.9% (Downtime < 8.76 giờ/năm)
- **GOOD**: 99.5-99.9% (Downtime 8.76-43.8 giờ/năm)
- **ACCEPTABLE**: 99.0-99.5% (Downtime 43.8-87.6 giờ/năm)
- **POOR**: < 99.0% (Downtime > 87.6 giờ/năm)

### **Efficiency Metrics**

#### **Cache Hit Rate:**
- **EXCELLENT**: > 95%
- **GOOD**: 90-95%
- **ACCEPTABLE**: 80-90%
- **POOR**: < 80%

#### **Auto Response Rate:**
- **EXCELLENT**: > 95%
- **GOOD**: 90-95%
- **ACCEPTABLE**: 80-90%
- **POOR**: < 80%

## **📈 PERFORMANCE TREND ANALYSIS**

### **Trend Direction**
- **IMPROVING**: Score tăng so với ngày trước
- **DECLINING**: Score giảm so với ngày trước
- **STABLE**: Score ổn định

### **Consistency Analysis**
- **HIGH**: Score variation < 10 điểm
- **MEDIUM**: Score variation 10-20 điểm
- **LOW**: Score variation > 20 điểm

### **Trend Interpretation**
```python
# Ví dụ trend analysis
trend_data = {
    "average_score": 85.2,
    "min_score": 82.8,
    "max_score": 87.5,
    "score_volatility": 4.7,
    "consistency": "HIGH"
}

# Interpretation
if trend_data["consistency"] == "HIGH":
    print("Hệ thống hoạt động ổn định")
elif trend_data["consistency"] == "MEDIUM":
    print("Hệ thống có biến động vừa phải")
else:
    print("Hệ thống có biến động lớn, cần chú ý")
```

## **🔍 TROUBLESHOOTING**

### **Common Performance Issues**

#### **1. Low Overall Score**
```python
# Phân tích từng component
overview = metrics_service.get_system_performance_overview()

if overview['risk_detection']['false_positive_rate'] > 20:
    print("Vấn đề: False positive rate cao")
    
if overview['response_time']['response_time_grade'] == 'POOR':
    print("Vấn đề: Response time chậm")
    
if overview['accuracy']['overall_accuracy'] < 80:
    print("Vấn đề: Độ chính xác thấp")
```

#### **2. High Response Time**
```python
# Kiểm tra response time distribution
response_time = overview['response_time']
poor_count = response_time['poor_count']
total_actions = response_time['total_actions']

poor_percentage = (poor_count / total_actions) * 100
if poor_percentage > 5:
    print(f"Vấn đề: {poor_percentage:.1f}% actions có response time > 1s")
```

#### **3. Low Cache Hit Rate**
```python
# Kiểm tra cache efficiency
efficiency = overview['efficiency']
cache_hit_rate = efficiency['cache_hit_rate']

if cache_hit_rate < 80:
    print(f"Vấn đề: Cache hit rate thấp ({cache_hit_rate:.1f}%)")
    print("Khuyến nghị: Review cache strategy")
```

### **Debug Mode**
```python
# Bật debug logging
LOGGING = {
    'loggers': {
        'risk_manager.metrics': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}

# Debug metrics calculation
metrics_service._calculate_risk_detection_metrics(24)
metrics_service._calculate_response_time_metrics(24)
metrics_service._calculate_overall_performance_score(...)
```

## **📈 BEST PRACTICES**

### **1. Regular Monitoring**
- **Daily**: Kiểm tra performance overview
- **Weekly**: Phân tích trends và patterns
- **Monthly**: Review và cập nhật thresholds

### **2. Performance Optimization**
- **Immediate**: Fix critical issues (score < 70)
- **Short-term**: Address medium priority issues
- **Long-term**: Plan improvements for high scores

### **3. Data Analysis**
- **Historical**: So sánh với dữ liệu lịch sử
- **Benchmarking**: So sánh với industry standards
- **Correlation**: Phân tích mối quan hệ giữa các metrics

### **4. Alert Management**
- **Threshold-based**: Alert khi vượt ngưỡng
- **Trend-based**: Alert khi có xu hướng xấu
- **Anomaly-based**: Alert khi có bất thường

## **🚨 EMERGENCY PROCEDURES**

### **Critical Performance Issues**
1. **Immediate Actions:**
   - Check system health
   - Activate emergency mode
   - Notify technical team

2. **Investigation:**
   - Analyze performance metrics
   - Check system logs
   - Identify root cause

3. **Recovery:**
   - Apply performance fixes
   - Monitor recovery
   - Document lessons learned

### **Performance Threshold Violations**
```python
# Auto-alert khi vượt ngưỡng
def check_performance_thresholds():
    overview = metrics_service.get_system_performance_overview()
    
    if overview['overall_score'] < 70:
        send_emergency_alert("Critical performance degradation")
    
    if overview['availability']['availability_percentage'] < 95:
        send_emergency_alert("System availability below threshold")
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

**📝 Lưu ý**: Performance Metrics Service cung cấp cái nhìn toàn diện về hiệu suất hệ thống. Sử dụng các metrics này để đưa ra quyết định cải thiện và tối ưu hóa hệ thống.
