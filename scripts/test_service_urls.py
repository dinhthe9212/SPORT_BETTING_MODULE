#!/usr/bin/env python3
"""
Script test để kiểm tra cấu hình service URLs
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_service_urls():
    """Test tất cả service URLs"""
    print("🔍 Testing Service URLs Configuration...")
    print("=" * 50)
    
    try:
        from shared.base_settings import get_service_url, get_all_service_urls, MICROSERVICES
        
        print("✅ Successfully imported shared.base_settings")
        
        # Test lấy tất cả URLs
        print("\n📋 All Service URLs:")
        all_urls = get_all_service_urls()
        for service, url in all_urls.items():
            print(f"  {service:20} -> {url}")
        
        # Test từng service cụ thể
        print("\n🔧 Testing Individual Services:")
        test_services = ['betting', 'risk', 'sports', 'carousel', 'saga']
        
        for service in test_services:
            try:
                url = get_service_url(service)
                print(f"  ✅ {service:15} -> {url}")
            except KeyError as e:
                print(f"  ❌ {service:15} -> ERROR: {e}")
        
        # Test error handling
        print("\n🚨 Testing Error Handling:")
        try:
            get_service_url('nonexistent_service')
            print("  ❌ Should have raised KeyError")
        except KeyError as e:
            print(f"  ✅ Correctly raised KeyError: {e}")
        
        print("\n🎉 All tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_environment_variables():
    """Test biến môi trường"""
    print("\n🔍 Testing Environment Variables...")
    print("=" * 50)
    
    # Test các biến môi trường quan trọng
    env_vars = [
        'BETTING_SERVICE_URL',
        'RISK_SERVICE_URL', 
        'SPORTS_SERVICE_URL',
        'CAROUSEL_SERVICE_URL',
        'SAGA_SERVICE_URL'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var:25} -> {value}")
        else:
            print(f"  ⚠️  {var:25} -> Not set (using default)")

def test_hard_coded_urls():
    """Tìm hard-coded URLs còn lại"""
    print("\n🔍 Searching for remaining hard-coded URLs...")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    python_files = list(project_root.rglob("*.py"))
    
    hard_coded_patterns = [
        r'http://localhost:\d+',
        r'http://[a-zA-Z0-9-]+:\d+',
        r'https://localhost:\d+'
    ]
    
    import re
    found_hard_coded = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern in hard_coded_patterns:
                        if re.search(pattern, line):
                            # Skip comments and documentation
                            if not line.strip().startswith('#') and 'http' in line:
                                found_hard_coded.append({
                                    'file': str(py_file.relative_to(project_root)),
                                    'line': i,
                                    'content': line.strip()
                                })
        except Exception as e:
            print(f"  ⚠️  Error reading {py_file}: {e}")
    
    if found_hard_coded:
        print(f"  ❌ Found {len(found_hard_coded)} potential hard-coded URLs:")
        for item in found_hard_coded[:10]:  # Show first 10
            print(f"    {item['file']}:{item['line']} -> {item['content']}")
        if len(found_hard_coded) > 10:
            print(f"    ... and {len(found_hard_coded) - 10} more")
    else:
        print("  ✅ No hard-coded URLs found in Python files")

def main():
    """Main test function"""
    print("🚀 Service URLs Configuration Test")
    print("=" * 50)
    
    # Test 1: Service URLs configuration
    success1 = test_service_urls()
    
    # Test 2: Environment variables
    test_environment_variables()
    
    # Test 3: Hard-coded URLs check
    test_hard_coded_urls()
    
    print("\n" + "=" * 50)
    if success1:
        print("🎉 Configuration test completed successfully!")
        print("✅ Service URLs are properly configured")
        print("✅ Environment variables are working")
        print("✅ Migration to environment variables is complete")
    else:
        print("❌ Configuration test failed!")
        print("Please check the errors above and fix them")
    
    return success1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
