#!/usr/bin/env python3
"""
Script để load Cash Out Saga fixture vào database
"""

import os
import sys
import django

# Thêm đường dẫn project vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thiết lập Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga_orchestrator_project.settings')
django.setup()

from django.core.management import call_command
from sagas.models import SagaDefinition
import json

def load_cashout_fixture():
    """Load Cash Out Saga fixture"""
    try:
        # Kiểm tra xem fixture đã tồn tại chưa
        existing = SagaDefinition.objects.filter(saga_type='cashout_flow').first()
        if existing:
            print(f"✅ Cash Out Saga definition đã tồn tại với ID: {existing.id}")
            return existing
        
        # Load fixture
        fixture_path = os.path.join(
            os.path.dirname(__file__), 
            'sagas', 
            'fixtures', 
            'cashout_saga_definition.json'
        )
        
        if not os.path.exists(fixture_path):
            print(f"❌ Không tìm thấy fixture file: {fixture_path}")
            return None
        
        print(f"📁 Loading fixture từ: {fixture_path}")
        
        # Load fixture
        call_command('loaddata', fixture_path, verbosity=1)
        
        # Kiểm tra kết quả
        cashout_saga = SagaDefinition.objects.filter(saga_type='cashout_flow').first()
        if cashout_saga:
            print(f"✅ Cash Out Saga definition đã được load thành công!")
            print(f"   - ID: {cashout_saga.id}")
            print(f"   - Name: {cashout_saga.name}")
            print(f"   - Type: {cashout_saga.saga_type}")
            print(f"   - Active: {cashout_saga.is_active}")
            print(f"   - Steps: {len(cashout_saga.workflow_definition.get('steps', []))}")
            return cashout_saga
        else:
            print("❌ Không thể load Cash Out Saga definition")
            return None
            
    except Exception as e:
        print(f"❌ Lỗi khi load fixture: {e}")
        return None

def verify_cashout_saga():
    """Verify Cash Out Saga definition"""
    try:
        cashout_saga = SagaDefinition.objects.filter(saga_type='cashout_flow').first()
        if not cashout_saga:
            print("❌ Không tìm thấy Cash Out Saga definition")
            return False
        
        workflow = cashout_saga.workflow_definition
        steps = workflow.get('steps', [])
        
        print(f"\n🔍 Verifying Cash Out Saga Definition:")
        print(f"   - Total steps: {len(steps)}")
        
        expected_steps = [
            'cashout_validation',
            'live_odds_fetch', 
            'cashout_quote',
            'wallet_credit',
            'liability_update',
            'cashout_completion'
        ]
        
        for i, step in enumerate(steps):
            step_name = step.get('name', '')
            service = step.get('service', '')
            endpoint = step.get('endpoint', '')
            
            print(f"   Step {i+1}: {step_name}")
            print(f"     - Service: {service}")
            print(f"     - Endpoint: {endpoint}")
            
            if step_name in expected_steps:
                print(f"     ✅ Expected step")
            else:
                print(f"     ⚠️  Unexpected step")
        
        # Kiểm tra các bước bắt buộc
        step_names = [step.get('name', '') for step in steps]
        missing_steps = [step for step in expected_steps if step not in step_names]
        
        if missing_steps:
            print(f"\n❌ Missing required steps: {missing_steps}")
            return False
        else:
            print(f"\n✅ Tất cả các bước bắt buộc đã được định nghĩa")
            return True
            
    except Exception as e:
        print(f"❌ Lỗi khi verify: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Bắt đầu load Cash Out Saga fixture...")
    
    # Load fixture
    saga = load_cashout_fixture()
    if not saga:
        print("❌ Không thể load fixture")
        sys.exit(1)
    
    # Verify
    if verify_cashout_saga():
        print("\n🎉 Cash Out Saga fixture đã được load và verify thành công!")
        print("\n📋 Các API endpoints có sẵn:")
        print("   - POST /api/sagas/cashout/start/ - Khởi tạo Cash Out Saga")
        print("   - POST /api/sagas/cashout/rollback/ - Rollback Cash Out Saga")
        print("   - GET  /api/sagas/cashout/status/{id}/ - Trạng thái Saga")
        print("   - GET  /api/sagas/cashout/list/ - Danh sách Cash Out Saga")
        print("   - POST /api/sagas/cashout/{id}/retry/{step}/ - Retry step")
    else:
        print("\n❌ Cash Out Saga fixture có vấn đề")
        sys.exit(1)

if __name__ == '__main__':
    main()
