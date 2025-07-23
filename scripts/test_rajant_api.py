#!/usr/bin/env python3
"""
Test Script for Rajant API Integration
=====================================

This script validates connectivity to Rajant nodes using the rajant-api library.
Use this to verify your Rajant integration before running the full tracking system.

Usage:
    python3 test_rajant_api.py --host 192.168.100.10 --username admin --password admin
    python3 test_rajant_api.py --config config.yaml
"""

import asyncio
import argparse
import sys
import yaml
from typing import Dict, List

# Try to import rajant-api
try:
    from rajant_api import RajantAPI
    RAJANT_API_AVAILABLE = True
    print("✅ rajant-api library found")
except ImportError:
    print("❌ rajant-api library not found")
    print("   Install with: pip install rajant-api")
    RAJANT_API_AVAILABLE = False
    sys.exit(1)

class RajantTester:
    """Test class for validating Rajant API connectivity."""
    
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.test_results = {}
    
    async def run_all_tests(self) -> bool:
        """Run comprehensive tests on Rajant node."""
        print(f"\n🔍 Testing Rajant Node: {self.host}")
        print("=" * 50)
        
        try:
            # Test 1: Basic connectivity
            if not await self.test_connection():
                return False
            
            # Test 2: Authentication
            if not await self.test_authentication():
                return False
            
            # Test 3: Node information
            if not await self.test_node_info():
                return False
            
            # Test 4: Wireless clients
            if not await self.test_wireless_clients():
                return False
            
            # Test 5: Performance metrics
            await self.test_performance()
            
            print("\n🎉 All tests completed successfully!")
            self.print_summary()
            return True
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test basic network connectivity."""
        print("\n📡 Test 1: Basic Connectivity")
        
        try:
            rajant = RajantAPI(
                host=self.host,
                username=self.username,
                password=self.password,
                timeout=10
            )
            
            print(f"   Connecting to {self.host}...")
            await rajant.connect()
            print("   ✅ Connection established")
            
            await rajant.disconnect()
            print("   ✅ Connection closed properly")
            
            self.test_results['connection'] = 'PASS'
            return True
            
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            self.test_results['connection'] = f'FAIL: {e}'
            return False
    
    async def test_authentication(self) -> bool:
        """Test authentication with provided credentials."""
        print("\n🔐 Test 2: Authentication")
        
        try:
            rajant = RajantAPI(
                host=self.host,
                username=self.username,
                password=self.password
            )
            
            await rajant.connect()
            print(f"   ✅ Authenticated as user: {self.username}")
            
            # Test invalid credentials
            try:
                rajant_bad = RajantAPI(
                    host=self.host,
                    username=self.username,
                    password="wrong_password"
                )
                await rajant_bad.connect()
                print("   ⚠️  Warning: Authentication should have failed with wrong password")
            except:
                print("   ✅ Correctly rejected invalid credentials")
            
            await rajant.disconnect()
            self.test_results['authentication'] = 'PASS'
            return True
            
        except Exception as e:
            print(f"   ❌ Authentication failed: {e}")
            print("   💡 Check username/password or node configuration")
            self.test_results['authentication'] = f'FAIL: {e}'
            return False
    
    async def test_node_info(self) -> bool:
        """Test retrieving node information."""
        print("\n📊 Test 3: Node Information")
        
        try:
            rajant = RajantAPI(
                host=self.host,
                username=self.username,
                password=self.password
            )
            
            await rajant.connect()
            
            # Get node status
            status = await rajant.get_node_status()
            print(f"   📋 Hostname: {status.get('hostname', 'Unknown')}")
            print(f"   📋 Model: {status.get('model', 'Unknown')}")
            print(f"   📋 Firmware: {status.get('firmware_version', 'Unknown')}")
            print(f"   📋 Status: {'Online' if status.get('online', False) else 'Offline'}")
            print(f"   📋 Uptime: {status.get('uptime', 'Unknown')}")
            
            # Store for summary
            self.test_results['node_info'] = status
            
            await rajant.disconnect()
            print("   ✅ Node information retrieved successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to get node info: {e}")
            self.test_results['node_info'] = f'FAIL: {e}'
            return False
    
    async def test_wireless_clients(self) -> bool:
        """Test retrieving wireless client information."""
        print("\n📱 Test 4: Wireless Clients")
        
        try:
            rajant = RajantAPI(
                host=self.host,
                username=self.username,
                password=self.password
            )
            
            await rajant.connect()
            
            # Get wireless clients
            clients = await rajant.get_wireless_clients()
            client_count = len(clients) if clients else 0
            
            print(f"   📈 Found {client_count} wireless clients")
            
            if client_count > 0:
                print("   📱 Sample clients:")
                for i, client in enumerate(clients[:3]):  # Show first 3
                    mac = client.get('mac_address', 'Unknown')
                    rssi = client.get('rssi', 'Unknown')
                    ip = client.get('ip_address', 'Unknown')
                    print(f"      {i+1}. MAC: {mac} | RSSI: {rssi} | IP: {ip}")
                
                if client_count > 3:
                    print(f"      ... and {client_count - 3} more")
            else:
                print("   ℹ️  No wireless clients currently connected")
                print("   💡 This is normal if no devices are connected to this node")
            
            # Store for summary
            self.test_results['wireless_clients'] = {
                'count': client_count,
                'clients': clients[:5] if clients else []  # Store first 5 for summary
            }
            
            await rajant.disconnect()
            print("   ✅ Wireless client data retrieved successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to get wireless clients: {e}")
            print("   💡 Check if client tracking is enabled on the node")
            self.test_results['wireless_clients'] = f'FAIL: {e}'
            return False
    
    async def test_performance(self):
        """Test API performance and timing."""
        print("\n⚡ Test 5: Performance Metrics")
        
        try:
            import time
            
            rajant = RajantAPI(
                host=self.host,
                username=self.username,
                password=self.password
            )
            
            # Measure connection time
            start_time = time.time()
            await rajant.connect()
            connect_time = time.time() - start_time
            
            # Measure node status retrieval time
            start_time = time.time()
            await rajant.get_node_status()
            status_time = time.time() - start_time
            
            # Measure client retrieval time
            start_time = time.time()
            await rajant.get_wireless_clients()
            clients_time = time.time() - start_time
            
            await rajant.disconnect()
            
            print(f"   ⏱️  Connection time: {connect_time:.2f} seconds")
            print(f"   ⏱️  Node status time: {status_time:.2f} seconds")
            print(f"   ⏱️  Clients query time: {clients_time:.2f} seconds")
            
            # Performance assessment
            if connect_time < 5.0 and status_time < 3.0 and clients_time < 3.0:
                print("   ✅ Performance: Excellent")
            elif connect_time < 10.0 and status_time < 5.0 and clients_time < 5.0:
                print("   ✅ Performance: Good")
            else:
                print("   ⚠️  Performance: Slow (check network)")
            
            self.test_results['performance'] = {
                'connect_time': connect_time,
                'status_time': status_time,
                'clients_time': clients_time
            }
            
        except Exception as e:
            print(f"   ❌ Performance test failed: {e}")
            self.test_results['performance'] = f'FAIL: {e}'
    
    def print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        # Connection status
        conn_status = self.test_results.get('connection', 'NOT_RUN')
        print(f"Connection:      {'✅ PASS' if conn_status == 'PASS' else '❌ ' + conn_status}")
        
        # Authentication status
        auth_status = self.test_results.get('authentication', 'NOT_RUN')
        print(f"Authentication:  {'✅ PASS' if auth_status == 'PASS' else '❌ ' + auth_status}")
        
        # Node info
        node_info = self.test_results.get('node_info', {})
        if isinstance(node_info, dict):
            print(f"Node Info:       ✅ PASS")
            print(f"  Model:         {node_info.get('model', 'Unknown')}")
            print(f"  Firmware:      {node_info.get('firmware_version', 'Unknown')}")
        else:
            print(f"Node Info:       ❌ {node_info}")
        
        # Wireless clients
        clients_data = self.test_results.get('wireless_clients', {})
        if isinstance(clients_data, dict):
            client_count = clients_data.get('count', 0)
            print(f"Wireless Clients: ✅ PASS ({client_count} clients)")
        else:
            print(f"Wireless Clients: ❌ {clients_data}")
        
        # Performance
        perf_data = self.test_results.get('performance', {})
        if isinstance(perf_data, dict):
            print(f"Performance:     ✅ PASS")
            print(f"  Connect time:  {perf_data.get('connect_time', 0):.2f}s")
            print(f"  Query time:    {perf_data.get('clients_time', 0):.2f}s")
        else:
            print(f"Performance:     ❌ {perf_data}")
        
        print("\n💡 Recommendations:")
        if conn_status == 'PASS' and auth_status == 'PASS':
            print("   ✅ Rajant node is ready for integration!")
            print("   ✅ You can proceed with full tunnel tracking setup")
        else:
            print("   ⚠️  Fix connection/authentication issues before proceeding")
            print("   💡 Check network connectivity and Rajant node configuration")

async def test_from_config(config_file: str):
    """Test multiple nodes from configuration file."""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        rajant_config = config.get('rajant', {})
        username = rajant_config.get('username', 'admin')
        password = rajant_config.get('password', 'admin')
        nodes = rajant_config.get('nodes', [])
        
        if not nodes:
            print("❌ No nodes found in configuration file")
            return False
        
        print(f"🔍 Testing {len(nodes)} nodes from configuration...")
        
        all_passed = True
        for i, node in enumerate(nodes):
            node_ip = node.get('ip', '')
            node_name = node.get('name', f'Node {i+1}')
            
            print(f"\n{'='*60}")
            print(f"Testing Node {i+1}/{len(nodes)}: {node_name} ({node_ip})")
            print(f"{'='*60}")
            
            if not node_ip:
                print(f"❌ No IP address for node: {node_name}")
                all_passed = False
                continue
            
            tester = RajantTester(node_ip, username, password)
            success = await tester.run_all_tests()
            
            if not success:
                all_passed = False
        
        print(f"\n{'='*60}")
        print("🏁 OVERALL RESULTS")
        print(f"{'='*60}")
        
        if all_passed:
            print("🎉 All nodes tested successfully!")
            print("✅ Your Rajant network is ready for tunnel tracking!")
        else:
            print("⚠️  Some nodes failed testing")
            print("💡 Fix issues before running full system")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False

async def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description='Test Rajant API connectivity')
    parser.add_argument('--host', help='Rajant node IP address')
    parser.add_argument('--username', default='admin', help='Rajant username (default: admin)')
    parser.add_argument('--password', default='admin', help='Rajant password (default: admin)')
    parser.add_argument('--config', help='YAML configuration file with multiple nodes')
    
    args = parser.parse_args()
    
    print("🧪 Rajant API Test Suite")
    print("========================")
    
    if args.config:
        # Test multiple nodes from config file
        success = await test_from_config(args.config)
    elif args.host:
        # Test single node
        tester = RajantTester(args.host, args.username, args.password)
        success = await tester.run_all_tests()
    else:
        print("❌ Please provide either --host or --config parameter")
        print("\nExamples:")
        print("  python3 test_rajant_api.py --host 192.168.100.10")
        print("  python3 test_rajant_api.py --host 192.168.100.10 --username admin --password mypass")
        print("  python3 test_rajant_api.py --config config.yaml")
        return False
    
    # Final message
    print("\n" + "="*60)
    if success:
        print("🚀 Ready to proceed with tunnel tracking system!")
        print("   Next steps:")
        print("   1. Configure all Rajant nodes with same credentials")
        print("   2. Set up Raspberry Pi with integration script")
        print("   3. Deploy Firebase backend")
        print("   4. Test end-to-end system")
    else:
        print("🔧 Please fix issues before proceeding")
        print("   Common solutions:")
        print("   - Check network connectivity: ping [NODE_IP]")
        print("   - Verify Rajant credentials")
        print("   - Enable API access on Rajant nodes")
        print("   - Check firewall settings")
    
    return success

if __name__ == "__main__":
    if not RAJANT_API_AVAILABLE:
        sys.exit(1)
    
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 