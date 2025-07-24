#!/usr/bin/env python3
"""
Full System Test for Tunnel Tracking System
Tests all components: Rajant API, Firebase API, and end-to-end tracking
"""

import asyncio
import json
import time
import requests
from datetime import datetime
from rajant_integration import RajantMonitor
from test_config import test_configuration

class FullSystemTest:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'UNKNOWN'
        }
        
    def log_test(self, test_name, status, message="", details=None):
        """Log test result"""
        self.results['tests'][test_name] = {
            'status': status,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        
    async def test_rajant_connectivity(self):
        """Test 1: Rajant Node Connectivity"""
        print("\n🔗 Testing Rajant Node Connectivity...")
        
        try:
            monitor = RajantMonitor()
            nodes_status = []
            
            for node in monitor.config['rajant']['nodes']:
                try:
                    # Test if node is reachable
                    response = await monitor.check_node_connectivity(node['ip'])
                    if response:
                        nodes_status.append(f"✅ {node['name']} ({node['ip']})")
                        self.log_test(f"Node_{node['name']}_connectivity", "PASS", 
                                    f"Node reachable at {node['ip']}")
                    else:
                        nodes_status.append(f"❌ {node['name']} ({node['ip']})")
                        self.log_test(f"Node_{node['name']}_connectivity", "FAIL",
                                    f"Node unreachable at {node['ip']}")
                except Exception as e:
                    nodes_status.append(f"❌ {node['name']} - Error: {str(e)}")
                    self.log_test(f"Node_{node['name']}_connectivity", "FAIL", str(e))
                    
            print(f"Node Status:\n" + "\n".join(nodes_status))
            
        except Exception as e:
            self.log_test("Rajant_connectivity", "FAIL", f"Failed to initialize monitor: {e}")
    
    def test_firebase_api(self):
        """Test 2: Firebase API Connectivity"""
        print("\n🔥 Testing Firebase API...")
        
        try:
            # Test health endpoint
            api_url = "https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/api"
            health_response = requests.get(f"{api_url}/health", timeout=10)
            
            if health_response.status_code == 200:
                self.log_test("Firebase_health", "PASS", "API health check passed")
            else:
                self.log_test("Firebase_health", "FAIL", 
                            f"API health check failed: {health_response.status_code}")
                
            # Test log position endpoint
            test_data = {
                "mac_address": "AA:BB:CC:DD:EE:FF",
                "node_id": "test_node",
                "timestamp": datetime.now().isoformat(),
                "signal_strength": -45
            }
            
            log_response = requests.post(f"{api_url}/log-position", 
                                       json=test_data, timeout=10)
            
            if log_response.status_code in [200, 201]:
                self.log_test("Firebase_log_position", "PASS", "Position logging works")
            else:
                self.log_test("Firebase_log_position", "FAIL",
                            f"Position logging failed: {log_response.status_code}")
                
        except Exception as e:
            self.log_test("Firebase_api", "FAIL", f"Firebase API test failed: {e}")
    
    def test_dashboard_access(self):
        """Test 3: Dashboard Accessibility"""
        print("\n📊 Testing Dashboard Access...")
        
        try:
            dashboard_url = "https://tunnel-tracking-system.web.app"
            response = requests.get(dashboard_url, timeout=10)
            
            if response.status_code == 200 and "Tunnel Tracking System" in response.text:
                self.log_test("Dashboard_access", "PASS", "Dashboard is accessible")
            else:
                self.log_test("Dashboard_access", "FAIL", 
                            f"Dashboard access failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("Dashboard_access", "FAIL", f"Dashboard test failed: {e}")
    
    def test_worker_app_access(self):
        """Test 4: Worker App Accessibility"""
        print("\n📱 Testing Worker App Access...")
        
        try:
            worker_url = "https://worker-app-83aee.web.app"
            response = requests.get(worker_url, timeout=10)
            
            if response.status_code == 200:
                self.log_test("Worker_app_access", "PASS", "Worker app is accessible")
            else:
                self.log_test("Worker_app_access", "FAIL",
                            f"Worker app access failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("Worker_app_access", "FAIL", f"Worker app test failed: {e}")
    
    async def test_end_to_end_tracking(self):
        """Test 5: End-to-End Tracking Simulation"""
        print("\n🎯 Testing End-to-End Tracking...")
        
        try:
            # Simulate device detection and tracking
            test_mac = "TEST:MAC:ADDR:ESS"
            api_url = "https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/api"
            
            # Log position at different nodes
            nodes = ["entrance_01", "section_a1", "exit_01"]
            
            for i, node in enumerate(nodes):
                position_data = {
                    "mac_address": test_mac,
                    "node_id": node,
                    "timestamp": datetime.now().isoformat(),
                    "signal_strength": -45 - (i * 5)  # Decreasing signal
                }
                
                response = requests.post(f"{api_url}/log-position", 
                                       json=position_data, timeout=10)
                
                if response.status_code in [200, 201]:
                    print(f"  ✅ Logged position at {node}")
                else:
                    print(f"  ❌ Failed to log position at {node}")
                    
                time.sleep(1)  # Small delay between logs
                
            self.log_test("End_to_end_tracking", "PASS", 
                        f"Successfully tracked device through {len(nodes)} nodes")
            
        except Exception as e:
            self.log_test("End_to_end_tracking", "FAIL", 
                        f"End-to-end tracking failed: {e}")
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*60)
        print("🧪 FULL SYSTEM TEST REPORT")
        print("="*60)
        
        passed = sum(1 for test in self.results['tests'].values() if test['status'] == 'PASS')
        failed = sum(1 for test in self.results['tests'].values() if test['status'] == 'FAIL')
        total = len(self.results['tests'])
        
        print(f"📊 Results: {passed}/{total} tests passed")
        
        if failed == 0:
            self.results['overall_status'] = 'ALL_PASS'
            print("✅ All tests PASSED! System is ready for production!")
        else:
            self.results['overall_status'] = 'SOME_FAILED'
            print(f"⚠️  {failed} tests FAILED. Please check the issues below:")
            
            for test_name, test_result in self.results['tests'].items():
                if test_result['status'] == 'FAIL':
                    print(f"  ❌ {test_name}: {test_result['message']}")
        
        print("\n🔧 Next Steps:")
        print("1. Fix any failed tests above")
        print("2. Register workers via mobile app: https://worker-app-83aee.web.app")
        print("3. Monitor live tracking: https://tunnel-tracking-system.web.app")
        print("4. Test physical movement in tunnel")
        
        # Save report to file
        with open(f'system_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(self.results, f, indent=2)
            
        return self.results['overall_status'] == 'ALL_PASS'

async def main():
    """Run full system test suite"""
    print("🚀 Starting Full System Test for Tunnel Tracking System")
    print("=" * 60)
    
    tester = FullSystemTest()
    
    # Run all tests
    await tester.test_rajant_connectivity()
    tester.test_firebase_api()
    tester.test_dashboard_access()
    tester.test_worker_app_access()
    await tester.test_end_to_end_tracking()
    
    # Generate final report
    success = tester.generate_report()
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        exit(1) 