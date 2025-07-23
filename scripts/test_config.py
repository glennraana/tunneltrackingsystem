#!/usr/bin/env python3
"""
Configuration Test Script
========================

Tests the updated config.yaml file and all integrations on Raspberry Pi.
Run this to verify everything is working before live Rajant testing.

Usage:
    python3 test_config.py
"""

import sys
import yaml
import traceback
from datetime import datetime

def test_config_loading():
    """Test loading and parsing config.yaml."""
    print("\n📋 Testing config.yaml loading...")
    print("-" * 40)
    
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        print("✅ Config file loaded successfully")
        
        # Check required sections
        required_sections = ['firebase', 'rajant', 'monitoring', 'tunnel']
        for section in required_sections:
            if section in config:
                print(f"✅ {section} section present")
            else:
                print(f"❌ {section} section missing")
                return False, None
        
        # Show key config values
        firebase_url = config['firebase']['api_url']
        nodes_count = len(config['rajant']['nodes'])
        scan_interval = config['monitoring']['scan_interval']
        
        print(f"📄 Firebase API URL: {firebase_url}")
        print(f"📄 Rajant nodes configured: {nodes_count}")
        print(f"📄 Scan interval: {scan_interval} seconds")
        
        return True, config
        
    except FileNotFoundError:
        print("❌ config.yaml file not found")
        return False, None
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, None

def test_firebase_api(config):
    """Test Firebase API connectivity with config settings."""
    print("\n🔥 Testing Firebase API...")
    print("-" * 40)
    
    try:
        import requests
        
        api_url = config['firebase']['api_url']
        timeout = config['firebase']['timeout']
        
        print(f"🌐 API URL: {api_url}")
        print(f"⏰ Timeout: {timeout} seconds")
        
        # Test health endpoint
        print("\n🧪 Testing health endpoint...")
        try:
            response = requests.get(f"{api_url}/health", timeout=timeout)
            print(f"✅ Health check: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📄 Response: {data}")
            else:
                print(f"📄 Response: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
        
        # Test log-position endpoint
        print("\n🧪 Testing log-position endpoint...")
        try:
            test_data = {
                "mac_address": "AA:BB:CC:DD:EE:FF",
                "node_id": "test_pi_config",
                "timestamp": datetime.now().isoformat() + "Z",
                "signal_strength": -45
            }
            
            response = requests.post(f"{api_url}/log-position", 
                                   json=test_data, 
                                   timeout=timeout)
            print(f"✅ Log position: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")
            
            if response.status_code in [200, 201]:
                print("🎯 Firebase API is working perfectly!")
                return True
            else:
                print("⚠️ Unexpected status code")
                return False
                
        except Exception as e:
            print(f"❌ Log position test failed: {e}")
            return False
            
    except ImportError:
        print("❌ requests package not available")
        return False

def test_rajant_api():
    """Test rajant-api package and functions."""
    print("\n📡 Testing rajant-api package...")
    print("-" * 40)
    
    try:
        import rajant_api
        print("✅ rajant-api imported successfully")
        
        # Get function signature for is_host_reachable
        import inspect
        
        # Test available functions
        test_functions = ['is_host_reachable', 'get_gps', 'pack', 'unpack']
        available_functions = []
        
        for func_name in test_functions:
            if hasattr(rajant_api, func_name):
                func = getattr(rajant_api, func_name)
                try:
                    sig = inspect.signature(func)
                    print(f"✅ {func_name}{sig}")
                    available_functions.append(func_name)
                except:
                    print(f"✅ {func_name} (signature unknown)")
                    available_functions.append(func_name)
            else:
                print(f"❌ {func_name} not available")
        
        # Test is_host_reachable with different signatures
        if 'is_host_reachable' in available_functions:
            print("\n🧪 Testing is_host_reachable function...")
            try:
                # Try with just hostname
                result = rajant_api.is_host_reachable("8.8.8.8")
                print(f"✅ is_host_reachable('8.8.8.8'): {result}")
            except TypeError as e:
                print(f"⚠️ Single argument failed: {e}")
                try:
                    # Try with no arguments
                    result = rajant_api.is_host_reachable()
                    print(f"✅ is_host_reachable(): {result}")
                except Exception as e2:
                    print(f"⚠️ No arguments failed: {e2}")
        
        # Check protobuf modules
        print("\n📄 Available protobuf modules:")
        pb2_modules = [attr for attr in dir(rajant_api) if attr.endswith('_pb2')]
        for module in pb2_modules[:5]:  # Show first 5
            print(f"  ✅ {module}")
        if len(pb2_modules) > 5:
            print(f"  ... and {len(pb2_modules)-5} more")
        
        return True
        
    except ImportError as e:
        print(f"❌ rajant-api import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

def test_core_packages():
    """Test all required Python packages."""
    print("\n📦 Testing core packages...")
    print("-" * 40)
    
    required_packages = {
        'requests': 'HTTP client for Firebase API',
        'yaml': 'Config file parsing',
        'paramiko': 'SSH client for Rajant nodes',
        'psutil': 'System utilities',
        'asyncio': 'Async programming support',
        'json': 'JSON data handling',
        'logging': 'Application logging',
        'datetime': 'Date/time handling',
        'socket': 'Network connectivity',
        'subprocess': 'Process execution'
    }
    
    failed_packages = []
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"❌ {package}: {description} - NOT AVAILABLE")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️ Missing packages: {', '.join(failed_packages)}")
        return False
    else:
        print("\n🎯 All core packages available!")
        return True

def test_network_connectivity():
    """Test network connectivity to required services."""
    print("\n🌐 Testing network connectivity...")
    print("-" * 40)
    
    import socket
    
    test_hosts = [
        ("Google DNS", "8.8.8.8", 53),
        ("Firebase", "firebase.google.com", 443),
        ("GitHub", "github.com", 443),
        ("PyPI", "pypi.org", 443)
    ]
    
    all_reachable = True
    
    for name, host, port in test_hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {name} ({host}:{port}) - reachable")
            else:
                print(f"❌ {name} ({host}:{port}) - not reachable")
                all_reachable = False
                
        except Exception as e:
            print(f"❌ {name} ({host}:{port}) - error: {e}")
            all_reachable = False
    
    return all_reachable

def main():
    """Run all configuration tests."""
    print("🧪 Configuration Test Suite")
    print("=" * 50)
    print(f"📅 Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    results = {}
    
    # Test 1: Config loading
    config_ok, config = test_config_loading()
    results['config_loading'] = config_ok
    
    if not config_ok:
        print("\n❌ Cannot continue without valid config file")
        return
    
    # Test 2: Core packages
    results['core_packages'] = test_core_packages()
    
    # Test 3: Network connectivity
    results['network'] = test_network_connectivity()
    
    # Test 4: rajant-api
    results['rajant_api'] = test_rajant_api()
    
    # Test 5: Firebase API (only if network is ok)
    if results['network']:
        results['firebase_api'] = test_firebase_api(config)
    else:
        print("\n⚠️ Skipping Firebase API test due to network issues")
        results['firebase_api'] = False
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Overall status
    all_passed = all(results.values())
    overall_status = "🎉 ALL TESTS PASSED" if all_passed else "⚠️ SOME TESTS FAILED"
    print(f"\nOverall Status: {overall_status}")
    
    # Next steps
    if all_passed:
        print("\n🚀 READY FOR LIVE TESTING!")
        print("Next steps:")
        print("1. Connect Rajant hardware")
        print("2. Update config.yaml with actual Rajant node IPs")
        print("3. Run: python3 test_rajant_api.py --config config.yaml")
        print("4. Run: python3 rajant_integration.py")
        print("5. Check admin dashboard: https://tunnel-tracking-system.web.app")
    else:
        print("\n🔧 Issues to fix:")
        if not results['config_loading']:
            print("- Fix config.yaml file")
        if not results['core_packages']:
            print("- Install missing packages: pip install -r requirements.txt")
        if not results['network']:
            print("- Check internet connection")
        if not results['rajant_api']:
            print("- Reinstall rajant-api: pip install rajant-api")
        if not results['firebase_api']:
            print("- Check Firebase deployment and config URL")
    
    print(f"\n🎯 Test completed at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main() 