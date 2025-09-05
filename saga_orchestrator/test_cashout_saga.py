#!/usr/bin/env python3
"""
Script test để kiểm tra Cash Out Saga functionality
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Thêm đường dẫn project vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thiết lập Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga_orchestrator_project.settings')
django.setup()

from sagas.models import SagaDefinition, SagaTransaction
from sagas.orchestrator import SagaOrchestrator

class CashOutSagaTester:
    """Test class cho Cash Out Saga"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"  # Saga Orchestrator service
        self.orchestrator = SagaOrchestrator()
        
    def test_saga_definition_exists(self):
        """Test xem Cash Out Saga definition có tồn tại không"""
        print("🔍 Testing Cash Out Saga definition...")
        
        try:
            saga_def = SagaDefinition.objects.filter(saga_type='cashout_flow').first()
            if saga_def:
                print(f"✅ Cash Out Saga definition tồn tại:")
                print(f"   - ID: {saga_def.id}")
                print(f"   - Name: {saga_def.name}")
                print(f"   - Active: {saga_def.is_active}")
                print(f"   - Steps: {len(saga_def.workflow_definition.get('steps', []))}")
                return True
            else:
                print("❌ Cash Out Saga definition không tồn tại")
                return False
        except Exception as e:
            print(f"❌ Lỗi khi kiểm tra saga definition: {e}")
            return False
    
    def test_start_cashout_saga(self):
        """Test khởi tạo Cash Out Saga"""
        print("\n🚀 Testing start Cash Out Saga...")
        
        try:
            # Test data
            test_data = {
                'bet_slip_id': 123,
                'user_id': 456,
                'bookmaker_type': 'SYSTEM',
                'bookmaker_id': 'system'
            }
            
            # Gọi API
            response = requests.post(
                f"{self.base_url}/api/sagas/cashout/start/",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Cash Out Saga đã được khởi tạo thành công:")
                print(f"   - Saga ID: {result.get('saga_transaction_id')}")
                print(f"   - Correlation ID: {result.get('correlation_id')}")
                print(f"   - Status: {result.get('status')}")
                return result.get('saga_transaction_id')
            else:
                print(f"❌ Không thể khởi tạo saga: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Không thể kết nối đến Saga Orchestrator service")
            print("   Hãy đảm bảo service đang chạy trên port 8000")
            return None
        except Exception as e:
            print(f"❌ Lỗi khi test start saga: {e}")
            return None
    
    def test_get_saga_status(self, saga_id):
        """Test lấy trạng thái Saga"""
        print(f"\n📊 Testing get saga status cho ID: {saga_id}...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/sagas/cashout/status/{saga_id}/",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Saga status retrieved:")
                print(f"   - Status: {result.get('status')}")
                print(f"   - Progress: {result.get('progress', {}).get('percentage', 0)}%")
                print(f"   - Total Steps: {result.get('progress', {}).get('total_steps', 0)}")
                print(f"   - Completed Steps: {result.get('progress', {}).get('completed_steps', 0)}")
                return True
            else:
                print(f"❌ Không thể lấy saga status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi khi test get saga status: {e}")
            return False
    
    def test_list_cashout_sagas(self):
        """Test lấy danh sách Cash Out Saga"""
        print("\n📋 Testing list Cash Out Sagas...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/sagas/cashout/list/",
                params={'page': 1, 'page_size': 10},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                sagas = result.get('sagas', [])
                pagination = result.get('pagination', {})
                
                print(f"✅ Cash Out Sagas list retrieved:")
                print(f"   - Total count: {pagination.get('total_count', 0)}")
                print(f"   - Page: {pagination.get('page', 1)}")
                print(f"   - Page size: {pagination.get('page_size', 10)}")
                print(f"   - Sagas in current page: {len(sagas)}")
                
                if sagas:
                    print(f"   - Sample saga: {sagas[0].get('saga_id')} - {sagas[0].get('status')}")
                
                return True
            else:
                print(f"❌ Không thể lấy danh sách sagas: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi khi test list sagas: {e}")
            return False
    
    def test_orchestrator_methods(self):
        """Test các method của SagaOrchestrator"""
        print("\n🧪 Testing SagaOrchestrator methods...")
        
        try:
            # Test start_cashout_saga method
            saga_transaction = self.orchestrator.start_cashout_saga(
                bet_slip_id=789,
                user_id=101,
                bookmaker_type='SYSTEM',
                bookmaker_id='system'
            )
            
            if saga_transaction:
                print(f"✅ start_cashout_saga method hoạt động:")
                print(f"   - Saga ID: {saga_transaction.id}")
                print(f"   - Type: {saga_transaction.saga_type}")
                print(f"   - Status: {saga_transaction.status}")
                
                # Test rollback method
                success = self.orchestrator.rollback_cashout_saga(
                    str(saga_transaction.id),
                    "Test rollback"
                )
                
                if success:
                    print(f"✅ rollback_cashout_saga method hoạt động")
                else:
                    print(f"❌ rollback_cashout_saga method thất bại")
                
                return True
            else:
                print("❌ start_cashout_saga method thất bại")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi khi test orchestrator methods: {e}")
            return False
    
    def run_all_tests(self):
        """Chạy tất cả các test"""
        print("🎯 Bắt đầu test Cash Out Saga functionality...")
        print("=" * 60)
        
        results = []
        
        # Test 1: Saga definition
        results.append(("Saga Definition", self.test_saga_definition_exists()))
        
        # Test 2: Start saga (chỉ test nếu service đang chạy)
        saga_id = self.test_start_cashout_saga()
        results.append(("Start Saga", saga_id is not None))
        
        # Test 3: Get saga status (chỉ test nếu có saga_id)
        if saga_id:
            results.append(("Get Saga Status", self.test_get_saga_status(saga_id)))
        else:
            results.append(("Get Saga Status", False))
        
        # Test 4: List sagas
        results.append(("List Sagas", self.test_list_cashout_sagas()))
        
        # Test 5: Orchestrator methods
        results.append(("Orchestrator Methods", self.test_orchestrator_methods()))
        
        # Tổng kết kết quả
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY:")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
        
        print("=" * 60)
        print(f"Total: {total} | Passed: {passed} | Failed: {total - passed}")
        
        if passed == total:
            print("🎉 TẤT CẢ TESTS ĐÃ PASS!")
        else:
            print("⚠️  MỘT SỐ TESTS ĐÃ FAIL!")
        
        return passed == total

def main():
    """Main function"""
    tester = CashOutSagaTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Cash Out Saga đã sẵn sàng để sử dụng!")
        sys.exit(0)
    else:
        print("\n❌ Cash Out Saga cần được kiểm tra thêm!")
        sys.exit(1)

if __name__ == '__main__':
    main()
