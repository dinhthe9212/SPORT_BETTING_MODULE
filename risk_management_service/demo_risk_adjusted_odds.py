#!/usr/bin/env python3
"""
Demo script cho Risk-Adjusted Offered Odds API
Chạy các test case để kiểm tra API hoạt động
"""

import requests
import json
from decimal import Decimal

# Cấu hình API
BASE_URL = "http://localhost:8000/api/v1/risk"
API_ENDPOINTS = {
    'calculate': f"{BASE_URL}/risk-adjusted-odds/",
    'explain': f"{BASE_URL}/risk-adjusted-odds/",
    'batch': f"{BASE_URL}/risk-adjusted-odds/batch/",
    'test': f"{BASE_URL}/risk-adjusted-odds/test/"
}


def test_single_calculation():
    """Test tính toán đơn lẻ"""
    print("=" * 60)
    print("TEST 1: TÍNH TOÁN ĐƠN LẺ")
    print("=" * 60)
    
    # Test case: Tình huống rủi ro cao
    test_data = {
        "theoretical_odds": "2.00",
        "margin_factor": "1.05",
        "net_liability": "8000.00",
        "risk_threshold": "10000.00"
    }
    
    try:
        response = requests.post(API_ENDPOINTS['calculate'], json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Thành công!")
            print(f"📊 Kết quả:")
            print(f"  Odds chào bán: {result.get('risk_adjusted_odds', 'N/A')}")
            print(f"  Trạng thái rủi ro: {result.get('risk_status', 'N/A')}")
            print(f"  Thị trường bị khóa: {result.get('market_locked', 'N/A')}")
            print(f"  Khuyến nghị: {result.get('recommendations', [])}")
        else:
            print(f"❌ Lỗi: {response.status_code}")
            print(f"Chi tiết: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")


def test_detailed_explanation():
    """Test lấy giải thích chi tiết"""
    print("\n" + "=" * 60)
    print("TEST 2: GIẢI THÍCH CHI TIẾT")
    print("=" * 60)
    
    params = {
        "theoretical_odds": "2.50",
        "margin_factor": "1.08",
        "net_liability": "3000.00",
        "risk_threshold": "10000.00"
    }
    
    try:
        response = requests.get(API_ENDPOINTS['explain'], params=params)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Thành công!")
            print(f"📋 Công thức: {result.get('formula', 'N/A')}")
            
            steps = result.get('steps', {})
            for step_key, step_data in steps.items():
                print(f"\n{step_key.upper()}:")
                print(f"  Mô tả: {step_data.get('description', 'N/A')}")
                print(f"  Tính toán: {step_data.get('calculation', 'N/A')}")
                print(f"  Kết quả: {step_data.get('result', 'N/A')}")
                print(f"  Giải thích: {step_data.get('explanation', 'N/A')}")
        else:
            print(f"❌ Lỗi: {response.status_code}")
            print(f"Chi tiết: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")


def test_batch_calculation():
    """Test tính toán batch"""
    print("\n" + "=" * 60)
    print("TEST 3: TÍNH TOÁN BATCH")
    print("=" * 60)
    
    batch_data = {
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
            },
            {
                "id": "match_1_draw",
                "theoretical_odds": "3.20",
                "margin_factor": "1.05",
                "net_liability": "1500.00",
                "risk_threshold": "10000.00"
            },
            {
                "id": "match_2_home",
                "theoretical_odds": "1.80",
                "margin_factor": "1.10",
                "net_liability": "8000.00",
                "risk_threshold": "10000.00"
            }
        ]
    }
    
    try:
        response = requests.post(API_ENDPOINTS['batch'], json=batch_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Thành công!")
            print(f"📊 Tổng kết:")
            print(f"  Tổng cấu hình: {result.get('total_configs', 'N/A')}")
            print(f"  Thành công: {result.get('successful_configs', 'N/A')}")
            print(f"  Thất bại: {result.get('failed_configs', 'N/A')}")
            print(f"  Thị trường bị khóa: {result.get('locked_markets', 'N/A')}")
            
            summary = result.get('summary', {})
            print(f"  Tỷ lệ thành công: {summary.get('success_rate', 0):.2f}%")
            print(f"  Tỷ lệ khóa: {summary.get('lock_rate', 0):.2f}%")
            
            print(f"\n📋 Chi tiết từng cấu hình:")
            results = result.get('results', {})
            for config_id, config_result in results.items():
                print(f"\n  {config_id}:")
                if config_result.get('success'):
                    print(f"    Odds chào bán: {config_result['risk_adjusted_odds']:.4f}")
                    print(f"    Trạng thái: {config_result['risk_status']}")
                    print(f"    Bị khóa: {config_result['market_locked']}")
                else:
                    print(f"    Lỗi: {config_result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Lỗi: {response.status_code}")
            print(f"Chi tiết: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")


def test_predefined_cases():
    """Test các trường hợp được định nghĩa sẵn"""
    print("\n" + "=" * 60)
    print("TEST 4: CÁC TRƯỜNG HỢP ĐỊNH NGHĨA SẴN")
    print("=" * 60)
    
    try:
        response = requests.get(API_ENDPOINTS['test'])
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Thành công!")
            
            summary = result.get('summary', {})
            print(f"📊 Tổng kết:")
            print(f"  Tổng test cases: {summary.get('total_cases', 'N/A')}")
            print(f"  Thành công: {summary.get('successful_cases', 'N/A')}")
            print(f"  Thị trường bị khóa: {summary.get('locked_markets', 'N/A')}")
            
            print(f"\n📋 Chi tiết từng test case:")
            test_cases = result.get('test_cases', {})
            for case_id, case_data in test_cases.items():
                print(f"\n  {case_id}: {case_data.get('name', 'N/A')}")
                case_result = case_data.get('result', {})
                if case_result.get('success'):
                    print(f"    Odds chào bán: {case_result.get('risk_adjusted_odds', 'N/A')}")
                    print(f"    Trạng thái: {case_result.get('risk_status', 'N/A')}")
                    print(f"    Bị khóa: {case_result.get('market_locked', 'N/A')}")
                else:
                    print(f"    Lỗi: {case_result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Lỗi: {response.status_code}")
            print(f"Chi tiết: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")


def test_formula_verification():
    """Test xác minh công thức bằng tính toán thủ công"""
    print("\n" + "=" * 60)
    print("TEST 5: XÁC MINH CÔNG THỨC")
    print("=" * 60)
    
    # Tham số test
    theoretical_odds = Decimal('2.00')
    margin_factor = Decimal('1.05')
    net_liability = Decimal('2000.00')
    risk_threshold = Decimal('10000.00')
    
    print(f"📊 Tham số đầu vào:")
    print(f"  Odds lý thuyết: {theoretical_odds}")
    print(f"  Biên lợi nhuận (M): {margin_factor}")
    print(f"  Trách nhiệm ròng (L_ròng): {net_liability}")
    print(f"  Trần rủi ro (T_cố_định): {risk_threshold}")
    
    # Tính toán thủ công
    print(f"\n🔢 Tính toán thủ công:")
    step1 = theoretical_odds / margin_factor
    print(f"  Bước 1: {theoretical_odds} / {margin_factor} = {step1}")
    
    step2 = net_liability / risk_threshold
    print(f"  Bước 2: {net_liability} / {risk_threshold} = {step2}")
    
    step3 = Decimal('1.0') - step2
    print(f"  Bước 3: 1 - {step2} = {step3}")
    
    final_odds = step1 * step3
    print(f"  Bước 4: {step1} * {step3} = {final_odds}")
    
    # So sánh với API
    test_data = {
        "theoretical_odds": str(theoretical_odds),
        "margin_factor": str(margin_factor),
        "net_liability": str(net_liability),
        "risk_threshold": str(risk_threshold)
    }
    
    try:
        response = requests.post(API_ENDPOINTS['calculate'], json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            api_odds = result.get('risk_adjusted_odds')
            
            print(f"\n✅ Kết quả từ API: {api_odds}")
            print(f"✅ Kết quả tính thủ công: {final_odds}")
            
            if api_odds and abs(float(api_odds) - float(final_odds)) < 0.0001:
                print("✅ Công thức được xác minh chính xác!")
            else:
                print("❌ Có sự khác biệt trong kết quả!")
        else:
            print(f"❌ Lỗi API: {response.status_code}")
            print(f"Chi tiết: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")


def main():
    """Chạy tất cả các test"""
    print("🧪 BẮT ĐẦU DEMO RISK-ADJUSTED OFFERED ODDS API")
    print("=" * 80)
    print(f"🌐 Base URL: {BASE_URL}")
    print("=" * 80)
    
    try:
        test_single_calculation()
        test_detailed_explanation()
        test_batch_calculation()
        test_predefined_cases()
        test_formula_verification()
        
        print("\n" + "=" * 80)
        print("✅ TẤT CẢ DEMO ĐÃ HOÀN THÀNH!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH DEMO: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
