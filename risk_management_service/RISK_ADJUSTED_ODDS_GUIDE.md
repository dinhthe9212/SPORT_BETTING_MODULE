# HƯỚNG DẪN SỬ DỤNG RISK-ADJUSTED OFFERED ODDS

## Tổng Quan

Risk-Adjusted Offered Odds là công thức cốt lõi trong hệ thống quản lý rủi ro, kết hợp xác suất lý thuyết với tình hình tài chính thực tế để tính toán tỷ lệ cược chào bán tối ưu.

## Công Thức

```
Odds_chào_bán = (Odds_lý_thuyết / M) * (1 - (L_ròng / T_cố_định))
```

### Tham Số

- **Odds_lý_thuyết**: Tỷ lệ cược lý thuyết dựa trên xác suất thực tế
- **M**: Biên lợi nhuận mong muốn (ví dụ: 1.05 = 5%)
- **L_ròng**: Trách nhiệm ròng hiện tại (có thể âm nếu có lợi nhuận)
- **T_cố_định**: Trần cố định rủi ro

### Logic Hoạt Động

1. **Khi rủi ro cao (L_ròng > 0)**: Hệ số (1 - ...) < 1 → Giảm odds để bảo vệ
2. **Khi an toàn (L_ròng < 0)**: Hệ số (1 - ...) > 1 → Tăng odds để thu hút cược
3. **Khi odds ≤ 1.0**: Hệ thống tự động khóa thị trường

## API Endpoints

### 1. Tính Toán Đơn Lẻ

**POST** `/api/v1/risk/risk-adjusted-odds/`

```json
{
    "theoretical_odds": "2.00",
    "margin_factor": "1.05",
    "net_liability": "8000.00",
    "risk_threshold": "10000.00"
}
```

**Response:**
```json
{
    "success": true,
    "theoretical_odds": 2.0,
    "margin_factor": 1.05,
    "net_liability": 8000.0,
    "risk_threshold": 10000.0,
    "odds_with_margin": 1.9048,
    "liability_ratio": 0.8,
    "risk_adjustment_factor": 0.2,
    "risk_adjusted_odds": 0.3810,
    "market_locked": true,
    "risk_status": "HIGH_RISK",
    "recommendations": [
        "🚫 THỊ TRƯỜNG BỊ KHÓA: Odds ≤ 1.0, cần điều chỉnh ngay lập tức",
        "🟠 Rủi ro cao: Cần hành động ngay",
        "📈 Tăng odds đáng kể để giảm rủi ro"
    ]
}
```

### 2. Giải Thích Chi Tiết

**GET** `/api/v1/risk/risk-adjusted-odds/`

**Query Parameters:**
- `theoretical_odds`: Odds lý thuyết
- `margin_factor`: Biên lợi nhuận
- `net_liability`: Trách nhiệm ròng
- `risk_threshold`: Trần rủi ro

**Response:**
```json
{
    "formula": "Odds_chào_bán = (Odds_lý_thuyết / M) * (1 - (L_ròng / T_cố_định))",
    "steps": {
        "step_1": {
            "description": "Tính (Odds_lý_thuyết / M)",
            "calculation": "2.0 / 1.05",
            "result": 1.9048,
            "explanation": "Áp dụng biên lợi nhuận 1.05 để đảm bảo lợi nhuận"
        },
        "step_2": {
            "description": "Tính (L_ròng / T_cố_định)",
            "calculation": "8000.0 / 10000.0",
            "result": 0.8,
            "explanation": "Tỷ lệ rủi ro hiện tại: 80.00%"
        },
        "step_3": {
            "description": "Tính (1 - (L_ròng / T_cố_định))",
            "calculation": "1 - 0.8",
            "result": 0.2,
            "explanation": "Hệ số 0.200 < 1: Rủi ro cao, giảm odds để bảo vệ"
        },
        "step_4": {
            "description": "Tính Odds_chào_bán cuối cùng",
            "calculation": "1.9048 * 0.2",
            "result": 0.3810,
            "explanation": "Kết quả cuối cùng sau khi điều chỉnh rủi ro"
        }
    },
    "risk_analysis": {
        "net_liability": 8000.0,
        "risk_threshold": 10000.0,
        "liability_ratio": 0.8,
        "risk_status": "HIGH_RISK",
        "market_impact": "Giảm odds"
    }
}
```

### 3. Tính Toán Batch

**POST** `/api/v1/risk/risk-adjusted-odds/batch/`

```json
{
    "odds_configs": [
        {
            "id": "match_1_home",
            "theoretical_odds": "2.00",
            "margin_factor": "1.05",
            "net_liability": "-500.00",
            "risk_threshold": "10000.00"
        },
        {
            "id": "match_1_away",
            "theoretical_odds": "3.50",
            "margin_factor": "1.05",
            "net_liability": "2000.00",
            "risk_threshold": "10000.00"
        }
    ]
}
```

### 4. Test Cases

**GET** `/api/v1/risk/risk-adjusted-odds/test/`

Chạy các test case mẫu để kiểm tra hoạt động của API.

## Trạng Thái Rủi Ro

| Trạng Thái | Điều Kiện | Hành Động |
|------------|-----------|-----------|
| **SAFE** | L_ròng < 0 | Tăng odds để thu hút cược |
| **LOW_RISK** | 0 ≤ L_ròng/T_cố_định < 0.5 | Theo dõi |
| **MEDIUM_RISK** | 0.5 ≤ L_ròng/T_cố_định < 0.8 | Cân nhắc tăng odds |
| **HIGH_RISK** | 0.8 ≤ L_ròng/T_cố_định < 1.0 | Tăng odds đáng kể |
| **CRITICAL_RISK** | L_ròng/T_cố_định ≥ 1.0 | Tạm dừng nhận cược |

## Khuyến Nghị Tự Động

Hệ thống tự động tạo khuyến nghị dựa trên trạng thái rủi ro:

- ✅ **An toàn**: Có thể tăng odds để thu hút thêm cược
- 🟢 **Rủi ro thấp**: Tiếp tục theo dõi
- 🟡 **Rủi ro trung bình**: Cần theo dõi chặt chẽ
- 🟠 **Rủi ro cao**: Cần hành động ngay
- 🔴 **Rủi ro cực kỳ cao**: Hành động khẩn cấp

## Sử Dụng Trong Code

### Python

```python
from risk_manager.services import RiskAdjustedOddsService
from decimal import Decimal

# Khởi tạo service
service = RiskAdjustedOddsService()

# Tính toán risk-adjusted odds
result = service.calculate_risk_adjusted_odds(
    theoretical_odds=Decimal('2.00'),
    margin_factor=Decimal('1.05'),
    net_liability=Decimal('8000.00'),
    risk_threshold=Decimal('10000.00')
)

print(f"Odds chào bán: {result['risk_adjusted_odds']}")
print(f"Thị trường bị khóa: {result['market_locked']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function calculateRiskAdjustedOdds() {
    try {
        const response = await axios.post('http://localhost:8000/api/v1/risk/risk-adjusted-odds/', {
            theoretical_odds: "2.00",
            margin_factor: "1.05",
            net_liability: "8000.00",
            risk_threshold: "10000.00"
        });
        
        console.log('Odds chào bán:', response.data.risk_adjusted_odds);
        console.log('Thị trường bị khóa:', response.data.market_locked);
    } catch (error) {
        console.error('Lỗi:', error.response.data);
    }
}
```

## Test và Demo

### Chạy Test Script

```bash
cd risk_management_service
python test_risk_adjusted_odds.py
```

### Chạy Demo API

```bash
cd risk_management_service
python demo_risk_adjusted_odds.py
```

## Lưu Ý Quan Trọng

1. **Validation**: Tất cả tham số đầu vào đều được validate
2. **Error Handling**: Xử lý lỗi graceful với thông báo rõ ràng
3. **Logging**: Ghi log tất cả tính toán để audit
4. **Performance**: Tối ưu hóa cho tính toán batch
5. **Security**: Kiểm tra quyền truy cập API

## Troubleshooting

### Lỗi Thường Gặp

1. **"Odds lý thuyết phải > 0"**: Kiểm tra giá trị theoretical_odds
2. **"Biên lợi nhuận phải > 1.0"**: Kiểm tra margin_factor
3. **"Trần rủi ro phải > 0"**: Kiểm tra risk_threshold
4. **"Thiếu trường bắt buộc"**: Kiểm tra tất cả tham số đầu vào

### Debug

Sử dụng endpoint giải thích chi tiết để debug:

```bash
curl "http://localhost:8000/api/v1/risk/risk-adjusted-odds/?theoretical_odds=2.0&margin_factor=1.05&net_liability=8000&risk_threshold=10000"
```

## Cập Nhật

- **Phiên bản**: 1.0
- **Cập nhật lần cuối**: 2024
- **Tương thích**: Django 3.2+, Python 3.8+

---

**Tài liệu này được tạo tự động từ SPORT_BETTING_MODULE**
**Liên hệ**: Development Team
