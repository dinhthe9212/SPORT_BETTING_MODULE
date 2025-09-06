#!/usr/bin/env python3
"""
Test script cho Risk-Adjusted Offered Odds Service
Kiểm tra triển khai công thức: Odds_chào_bán = (Odds_lý_thuyết / M) * (1 - (L_ròng / T_cố_định))
"""

import sys
import os
from decimal import Decimal

# Thêm path để import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from risk_manager.services import RiskAdjustedOddsService


def test_basic_calculation():
    """Test tính toán cơ bản"""
    print("=" * 60)
    print("TEST 1: TÍNH TOÁN CƠ BẢN")
    print("=" * 60)
    
    service = RiskAdjustedOddsService()
    
    # Test case 1: Tình huống an toàn (L_ròng < 0)
    print("\n📊 Test Case 1: Tình huống AN TOÀN (L_ròng < 0)")
    result1 = service.calculate_risk_adjusted_odds(
        theoretical_odds=Decimal('2.00'),
        margin_factor=Decimal('1.05'),
        net_liability=Decimal('-1000.00'),  # Có lợi nhuận
        risk_threshold=Decimal('10000.00')
    )
    
    print(f"Kết quả: {result1}")
    print(f"Odds chào bán: {result1.get('risk_adjusted_odds', 'N/A')}")
    print(f"Trạng thái rủi ro: {result1.get('risk_status', 'N/A')}")
    print(f"Thị trường bị khóa: {result1.get('market_locked', 'N/A')}")
    
    # Test case 2: Tình huống rủi ro cao (L_ròng > 0)
    print("\n📊 Test Case 2: Tình huống RỦI RO CAO (L_ròng > 0)")
    result2 = service.calculate_risk_adjusted_odds(
        theoretical_odds=Decimal('2.00'),
        margin_factor=Decimal('1.05'),
        net_liability=Decimal('8000.00'),  # Rủi ro cao
        risk_threshold=Decimal('10000.00')
    )
    
    print(f"Kết quả: {result2}")
    print(f"Odds chào bán: {result2.get('risk_adjusted_odds', 'N/A')}")
    print(f"Trạng thái rủi ro: {result2.get('risk_status', 'N/A')}")
    print(f"Thị trường bị khóa: {result2.get('market_locked', 'N/A')}")
    
    # Test case 3: Tình huống thị trường bị khóa (odds ≤ 1.0)
    print("\n📊 Test Case 3: Tình huống THỊ TRƯỜNG BỊ KHÓA")
    result3 = service.calculate_risk_adjusted_odds(
        theoretical_odds=Decimal('1.50'),
        margin_factor=Decimal('1.10'),
        net_liability=Decimal('9500.00'),  # Rủi ro rất cao
        risk_threshold=Decimal('10000.00')
    )
    
    print(f"Kết quả: {result3}")
    print(f"Odds chào bán: {result3.get('risk_adjusted_odds', 'N/A')}")
    print(f"Trạng thái rủi ro: {result3.get('risk_status', 'N/A')}")
    print(f"Thị trường bị khóa: {result3.get('market_locked', 'N/A')}")


def test_detailed_explanation():
    """Test giải thích chi tiết"""
    print("\n" + "=" * 60)
    print("TEST 2: GIẢI THÍCH CHI TIẾT")
    print("=" * 60)
    
    service = RiskAdjustedOddsService()
    
    # Test với tình huống rủi ro trung bình
    explanation = service.get_risk_adjustment_explanation(
        theoretical_odds=Decimal('2.50'),
        margin_factor=Decimal('1.08'),
        net_liability=Decimal('3000.00'),
        risk_threshold=Decimal('10000.00')
    )
    
    print(f"\n📋 Công thức: {explanation['formula']}")
    print(f"\n🔢 Các bước tính toán:")
    
    for step_key, step_data in explanation['steps'].items():
        print(f"\n{step_key.upper()}:")
        print(f"  Mô tả: {step_data['description']}")
        print(f"  Tính toán: {step_data['calculation']}")
        print(f"  Kết quả: {step_data['result']}")
        print(f"  Giải thích: {step_data['explanation']}")
    
    print(f"\n📊 Phân tích rủi ro:")
    risk_analysis = explanation['risk_analysis']
    for key, value in risk_analysis.items():
        print(f"  {key}: {value}")


def test_batch_calculation():
    """Test tính toán batch"""
    print("\n" + "=" * 60)
    print("TEST 3: TÍNH TOÁN BATCH")
    print("=" * 60)
    
    service = RiskAdjustedOddsService()
    
    # Tạo nhiều cấu hình test
    odds_configs = [
        {
            'id': 'match_1_home',
            'theoretical_odds': '2.00',
            'margin_factor': '1.05',
            'net_liability': '-500.00',
            'risk_threshold': '10000.00'
        },
        {
            'id': 'match_1_away',
            'theoretical_odds': '3.50',
            'margin_factor': '1.05',
            'net_liability': '2000.00',
            'risk_threshold': '10000.00'
        },
        {
            'id': 'match_1_draw',
            'theoretical_odds': '3.20',
            'margin_factor': '1.05',
            'net_liability': '1500.00',
            'risk_threshold': '10000.00'
        },
        {
            'id': 'match_2_home',
            'theoretical_odds': '1.80',
            'margin_factor': '1.10',
            'net_liability': '8000.00',
            'risk_threshold': '10000.00'
        }
    ]
    
    batch_result = service.calculate_batch_risk_adjusted_odds(odds_configs)
    
    print(f"📊 Tổng kết batch:")
    print(f"  Tổng cấu hình: {batch_result['total_configs']}")
    print(f"  Thành công: {batch_result['successful_configs']}")
    print(f"  Thất bại: {batch_result['failed_configs']}")
    print(f"  Thị trường bị khóa: {batch_result['locked_markets']}")
    print(f"  Tỷ lệ thành công: {batch_result['summary']['success_rate']:.2f}%")
    print(f"  Tỷ lệ khóa: {batch_result['summary']['lock_rate']:.2f}%")
    
    print(f"\n📋 Chi tiết từng cấu hình:")
    for config_id, result in batch_result['results'].items():
        print(f"\n  {config_id}:")
        if result.get('success'):
            print(f"    Odds chào bán: {result['risk_adjusted_odds']:.4f}")
            print(f"    Trạng thái: {result['risk_status']}")
            print(f"    Bị khóa: {result['market_locked']}")
        else:
            print(f"    Lỗi: {result.get('error', 'Unknown error')}")


def test_edge_cases():
    """Test các trường hợp đặc biệt"""
    print("\n" + "=" * 60)
    print("TEST 4: CÁC TRƯỜNG HỢP ĐẶC BIỆT")
    print("=" * 60)
    
    service = RiskAdjustedOddsService()
    
    # Test case 1: Tham số không hợp lệ
    print("\n🚫 Test Case 1: Tham số không hợp lệ")
    invalid_result = service.calculate_risk_adjusted_odds(
        theoretical_odds=Decimal('0'),  # Không hợp lệ
        margin_factor=Decimal('1.05'),
        net_liability=Decimal('1000.00'),
        risk_threshold=Decimal('10000.00')
    )
    print(f"Kết quả: {invalid_result}")
    
    # Test case 2: Margin factor = 1.0 (không hợp lệ)
    print("\n🚫 Test Case 2: Margin factor = 1.0")
    invalid_result2 = service.calculate_risk_adjusted_odds(
        theoretical_odds=Decimal('2.00'),
        margin_factor=Decimal('1.0'),  # Không hợp lệ
        net_liability=Decimal('1000.00'),
        risk_threshold=Decimal('10000.00')
    )
    print(f"Kết quả: {invalid_result2}")
    
    # Test case 3: Risk threshold = 0 (không hợp lệ)
    print("\n🚫 Test Case 3: Risk threshold = 0")
    invalid_result3 = service.calculate_risk_adjusted_odds(
        theoretical_odds=Decimal('2.00'),
        margin_factor=Decimal('1.05'),
        net_liability=Decimal('1000.00'),
        risk_threshold=Decimal('0')  # Không hợp lệ
    )
    print(f"Kết quả: {invalid_result3}")


def test_formula_verification():
    """Test xác minh công thức"""
    print("\n" + "=" * 60)
    print("TEST 5: XÁC MINH CÔNG THỨC")
    print("=" * 60)
    
    service = RiskAdjustedOddsService()
    
    # Test với các giá trị cụ thể để xác minh công thức
    theoretical_odds = Decimal('2.00')
    margin_factor = Decimal('1.05')
    net_liability = Decimal('2000.00')
    risk_threshold = Decimal('10000.00')
    
    result = service.calculate_risk_adjusted_odds(
        theoretical_odds, margin_factor, net_liability, risk_threshold
    )
    
    print(f"📊 Tham số đầu vào:")
    print(f"  Odds lý thuyết: {theoretical_odds}")
    print(f"  Biên lợi nhuận (M): {margin_factor}")
    print(f"  Trách nhiệm ròng (L_ròng): {net_liability}")
    print(f"  Trần rủi ro (T_cố_định): {risk_threshold}")
    
    print(f"\n🔢 Tính toán thủ công:")
    # Bước 1: (Odds_lý_thuyết / M)
    step1 = theoretical_odds / margin_factor
    print(f"  Bước 1: {theoretical_odds} / {margin_factor} = {step1}")
    
    # Bước 2: (L_ròng / T_cố_định)
    step2 = net_liability / risk_threshold
    print(f"  Bước 2: {net_liability} / {risk_threshold} = {step2}")
    
    # Bước 3: (1 - (L_ròng / T_cố_định))
    step3 = Decimal('1.0') - step2
    print(f"  Bước 3: 1 - {step2} = {step3}")
    
    # Bước 4: Kết quả cuối cùng
    final_odds = step1 * step3
    print(f"  Bước 4: {step1} * {step3} = {final_odds}")
    
    print(f"\n✅ Kết quả từ service: {result.get('risk_adjusted_odds', 'N/A')}")
    print(f"✅ Kết quả tính thủ công: {final_odds}")
    print(f"✅ Khớp nhau: {abs(float(result.get('risk_adjusted_odds', 0)) - float(final_odds)) < 0.0001}")


def main():
    """Chạy tất cả các test"""
    print("🧪 BẮT ĐẦU TEST RISK-ADJUSTED OFFERED ODDS SERVICE")
    print("=" * 80)
    
    try:
        test_basic_calculation()
        test_detailed_explanation()
        test_batch_calculation()
        test_edge_cases()
        test_formula_verification()
        
        print("\n" + "=" * 80)
        print("✅ TẤT CẢ TEST ĐÃ HOÀN THÀNH THÀNH CÔNG!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH TEST: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
