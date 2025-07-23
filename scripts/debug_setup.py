#!/usr/bin/env python3
"""
Debug Script for Tunnel Tracking System
=======================================

Troubleshoots Pi setup, rajant-api package, and Firebase connectivity.
Run this to diagnose issues with the integration.

Usage:
    python3 debug_setup.py
"""

import sys
import traceback

def test_rajant_api():
    """Test rajant-api package structure and functionality."""
    print("\n📡 Testing rajant-api package...")
    print("-" * 40)
    
    try:
        import rajant_api
        print("✅ rajant_api imported successfully")
        
        # Show available attributes
        attrs = dir(rajant_api)
        print(f"📋 Available attributes ({len(attrs)}):")
        
        # Categorize attributes
        functions = []
        classes = []
        modules = []
        
        for attr in attrs:
            if not attr.startswith('_'):
                obj = getattr(rajant_api, attr)
                if callable(obj):
                    functions.append(attr)
                elif hasattr(obj, '__module__'):
                    classes.append(attr)
                elif attr.endswith('_pb2'):
                    modules.append(attr)
        
        if functions:
            print(f"  🔧 Functions: {', '.join(functions[:5])}" + ("..." if len(functions) > 5 else ""))
        if classes:
            print(f"  📦 Classes: {', '.join(classes[:5])}" + ("..." if len(classes) > 5 else ""))
        if modules:
            print(f"  📄 Protobuf modules: {', '.join(modules[:3])}" + ("..." if len(modules) > 3 else ""))
        
        # Test specific functions
        test_functions = ['is_host_reachable', 'get_gps', 'pack', 'unpack']
        for func_name in test_functions:
            if hasattr(rajant_api, func_name):
                print(f"  ✅ {func_name} available")
                try:
                    func = getattr(rajant_api, func_name)
                    if func_name == 'is_host_reachable':
                        # Test with Google DNS
                        result = func("8.8.8.8", 53, 2)
                        print(f"    🧪 Test call result: {result}")
                except Exception as e:
                    print(f"    ⚠️ Test call failed: {e}")
            else:
                print(f"  ❌ {func_name} not available")
        
        # Check protobuf modules
        print("\n📄 Testing protobuf modules...")
        pb2_modules = [attr for attr in attrs if attr.endswith('_pb2')]
        for module_name in pb2_modules[:3]:  # Test first 3
            try:
                module = getattr(rajant_api, module_name)
                print(f"  ✅ {module_name}: {len(dir(module))} attributes")
            except Exception as e:
                print(f"  ❌ {module_name}: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ rajant_api import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing rajant_api: {e}")
        traceback.print_exc()
        return False

def test_core_packages():
    """Test core Python packages."""
    print("\n📦 Testing core packages...")
    print("-" * 40)
    
    packages = {
        'requests': 'HTTP client',
        'yaml': 'YAML parser', 
        'paramiko': 'SSH client',
        'psutil': 'System utilities',
        'asyncio': 'Async support',
        'json': 'JSON parser',
        'logging': 'Logging'
    }
    
    results = {}
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✅ {package}: {description}")
            results[package] = True
        except ImportError as e:
            print(f"❌ {package}: {e}")
            results[package] = False
    
    return all(results.values())

def test_firebase_api():
    """Test Firebase API connectivity."""
    print("\n🔥 Testing Firebase API...")
    print("-" * 40)
    
    try:
        import requests
        
        # Test different Firebase endpoints
        endpoints = [
            ("Health Check", "https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/health"),
            ("API Root", "https://us-central1-tunnel-tracking-system.cloudfunctions.net/api"),
            ("Function Root", "https://us-central1-tunnel-tracking-system.cloudfunctions.net")
        ]
        
        for name, url in endpoints:
            print(f"\n🌐 Testing {name}...")
            try:
                response = requests.get(url, timeout=10)
                print(f"  ✅ Status: {response.status_code}")
                
                # Show response content (truncated)
                content = response.text.strip()
                if content:
                    display_content = content[:200] + "..." if len(content) > 200 else content
                    print(f"  📄 Response: {display_content}")
                else:
                    print("  📄 Response: (empty)")
                
                if response.status_code == 200:
                    print(f"  🎯 {name} is working!")
                    return True
                    
            except requests.exceptions.Timeout:
                print(f"  ⏰ Timeout connecting to {name}")
            except requests.exceptions.ConnectionError as e:
                print(f"  🔌 Connection error to {name}: {e}")
            except Exception as e:
                print(f"  ❌ Error testing {name}: {e}")
        
        return False
        
    except ImportError:
        print("❌ requests package not available")
        return False

def test_network_connectivity():
    """Test basic network connectivity."""
    print("\n🌐 Testing network connectivity...")
    print("-" * 40)
    
    import socket
    
    # Test hosts
    test_hosts = [
        ("Google DNS", "8.8.8.8", 53),
        ("Firebase", "firebase.google.com", 443),
        ("GitHub", "github.com", 443)
    ]
    
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
                
        except Exception as e:
            print(f"❌ {name} ({host}:{port}) - error: {e}")

def test_system_info():
    """Show system information."""
    print("\n💻 System Information...")
    print("-" * 40)
    
    import platform
    
    print(f"🐍 Python: {sys.version}")
    print(f"💻 Platform: {platform.platform()}")
    print(f"🏗️  Architecture: {platform.architecture()}")
    print(f"📁 Current directory: {sys.path[0]}")
    
    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"🐍 Virtual environment: {sys.prefix}")
    else:
        print("⚠️ Not in virtual environment")

def main():
    """Run all diagnostic tests."""
    print("🔍 Tunnel Tracking System - Diagnostic Tool")
    print("=" * 50)
    
    # System info
    test_system_info()
    
    # Core tests
    results = {
        'core_packages': test_core_packages(),
        'rajant_api': test_rajant_api(),
        'firebase_api': test_firebase_api()
    }
    
    # Network test
    test_network_connectivity()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    overall_status = "✅ READY" if all(results.values()) else "⚠️ NEEDS ATTENTION"
    print(f"\nOverall Status: {overall_status}")
    
    if not all(results.values()):
        print("\n🔧 Next Steps:")
        if not results['core_packages']:
            print("- Reinstall Python packages: pip install -r requirements.txt")
        if not results['rajant_api']:
            print("- Check rajant-api installation and update integration scripts")
        if not results['firebase_api']:
            print("- Check internet connection and Firebase deployment")
    
    print("\n🎯 Diagnostic completed!")

if __name__ == "__main__":
    main() 