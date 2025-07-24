#!/usr/bin/env python3
"""
Rajant Integration Script for Tunnel Tracking System
====================================================

This script integrates Rajant mesh nodes with our Firebase-based tracking system.

Features:
- Discovers Rajant nodes on network
- Registers nodes in Firebase 
- Monitors MAC addresses from node associations
- Sends position updates to Cloud Functions API

Requirements:
- Rajant InstaMesh network access
- Python 3.8+
- Network access to Rajant nodes
"""

import requests
import json
import time
import socket
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import argparse

# Configuration
import yaml
import os

def load_config():
    """Load configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logger.error(f"❌ Failed to load config.yaml: {e}")
        # Fallback configuration
        return {
            'firebase': {
                'api_url': 'https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/api',
                'timeout': 10,
                'retry_attempts': 3
            },
            'rajant': {
                'default_username': 'admin',
                'default_password': 'admin',
                'api_timeout': 5,
                'nodes': [
                    {'ip': '192.168.100.10', 'name': 'Tunnel Entrance'},
                    {'ip': '192.168.100.11', 'name': 'Section A1'},
                    {'ip': '192.168.100.12', 'name': 'Tunnel Exit'}
                ]
            },
            'monitoring': {
                'scan_interval': 30,
                'signal_threshold': -80,
                'log_level': 'INFO'
            }
        }

CONFIG = load_config()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rajant_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import smart MAC filtering
try:
    from mac_filtering import MobilePhoneDetector
    MAC_FILTERING_AVAILABLE = True
    logger.info("✅ Smart MAC filtering enabled")
except ImportError:
    logger.warning("⚠️ MAC filtering module not available - all devices will be tracked")
    MAC_FILTERING_AVAILABLE = False

# Import Rajant API library
try:
    from rajant_api import RajantAPI
    RAJANT_API_AVAILABLE = True
    logger.info("✅ Rajant API library available")
except ImportError:
    logger.warning("⚠️ rajant-api library not installed - install with: pip install rajant-api")
    RAJANT_API_AVAILABLE = False

class RajantNodeDiscovery:
    """Discovers and manages Rajant nodes on the network."""
    
    def __init__(self):
        self.known_nodes = {}
        self.api_headers = {'Content-Type': 'application/json'}
    
    async def discover_nodes(self) -> List[Dict]:
        """Discover Rajant nodes on the network."""
        logger.info("🔍 Discovering Rajant nodes...")
        
        nodes = []
        
        # Method 1: Network scan for Rajant devices
        potential_nodes = await self._scan_network()
        
        for node_ip in potential_nodes:
            node_info = await self._get_node_info(node_ip)
            if node_info:
                nodes.append(node_info)
        
        logger.info(f"✅ Discovered {len(nodes)} Rajant nodes")
        return nodes
    
    async def _scan_network(self) -> List[str]:
        """Scan network for potential Rajant nodes using config.yaml."""
        # Get node IPs from configuration
        rajant_nodes = CONFIG.get('rajant', {}).get('nodes', [])
        potential_ips = [node.get('ip') for node in rajant_nodes if node.get('ip')]
        
        if not potential_ips:
            logger.warning("⚠️ No Rajant node IPs found in config.yaml")
            return []
        
        logger.info(f"🔍 Scanning {len(potential_ips)} configured Rajant nodes...")
        
        active_nodes = []
        for ip in potential_ips:
            if await self._ping_node(ip):
                active_nodes.append(ip)
                logger.info(f"✅ Node {ip} is reachable")
            else:
                logger.warning(f"❌ Node {ip} is not reachable")
        
        return active_nodes
    
    async def _ping_node(self, ip: str) -> bool:
        """Check if node is reachable."""
        try:
            # Use asyncio.subprocess for better async support
            process = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', '2', ip,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10.0)
            
            if process.returncode == 0:
                logger.info(f"✅ Ping successful to {ip}")
                return True
            else:
                logger.warning(f"❌ Ping failed to {ip} (return code: {process.returncode})")
                if stderr:
                    logger.debug(f"Ping stderr: {stderr.decode()}")
                return False
                
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Ping timeout to {ip}")
            return False
        except Exception as e:
            logger.error(f"❌ Ping error to {ip}: {e}")
            return False
    
    async def _get_node_info(self, ip: str) -> Optional[Dict]:
        """Get detailed information from Rajant node using rajant-api."""
        try:
            if RAJANT_API_AVAILABLE:
                # Use Rajant API to get actual node information
                rajant = RajantAPI(
                    host=ip,
                    username=CONFIG.get('rajant', {}).get('default_username', 'admin'),
                    password=CONFIG.get('rajant', {}).get('default_password', 'admin')
                )
                
                await rajant.connect()
                node_status = await rajant.get_node_status()
                node_config = await rajant.get_node_config()
                await rajant.disconnect()
                
                node_info = {
                    'ip_address': ip,
                    'node_id': f'rajant_{ip.split(".")[-1]}',
                    'name': node_status.get('hostname', f'Rajant Node {ip.split(".")[-1]}'),
                    'model': node_status.get('model', 'Unknown'),
                    'firmware_version': node_status.get('firmware_version', 'Unknown'),
                    'location': self._determine_location(ip),
                    'status': 'active' if node_status.get('online', False) else 'inactive',
                    'last_seen': datetime.now().isoformat(),
                    'uptime': node_status.get('uptime', '0'),
                    'load_average': node_status.get('load_average', 0),
                    'memory_usage': node_status.get('memory_usage', 0)
                }
                
                logger.info(f"📡 Found Rajant node: {node_info['name']} ({ip}) - Model: {node_info['model']}")
                return node_info
            else:
                # Fallback to simulated data
                node_info = {
                    'ip_address': ip,
                    'node_id': f'rajant_{ip.split(".")[-1]}',
                    'name': f'Rajant Node {ip.split(".")[-1]}',
                    'model': 'Unknown',  # Cannot determine without API
                    'firmware_version': 'Unknown',
                    'location': self._determine_location(ip),
                    'status': 'active',
                    'last_seen': datetime.now().isoformat()
                }
                
                logger.info(f"📡 Found Rajant node (mock): {node_info['name']} ({ip})")
                return node_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get info from {ip}: {e}")
            # Return basic info even if API fails
            return {
                'ip_address': ip,
                'node_id': f'rajant_{ip.split(".")[-1]}',
                'name': f'Rajant Node {ip.split(".")[-1]}',
                'model': 'Unknown',
                'firmware_version': 'Unknown',
                'location': self._determine_location(ip),
                'status': 'unknown',
                'last_seen': datetime.now().isoformat()
            }
    
    def _determine_location(self, ip: str) -> Dict[str, float]:
        """Determine physical location based on IP or configuration."""
        # Map IP addresses to physical tunnel positions
        location_map = {
            '192.168.100.10': {'x': 50, 'y': 100},   # Entrance
            '192.168.100.11': {'x': 200, 'y': 100},  # Section A
            '192.168.100.12': {'x': 350, 'y': 100},  # Exit
        }
        
        return location_map.get(ip, {'x': 0, 'y': 0})
    
    async def register_node_in_firebase(self, node_info: Dict) -> bool:
        """Register discovered node in Firebase system."""
        try:
            payload = {
                'node_id': node_info['node_id'],
                'name': node_info['name'],
                'location': node_info['location'],
                'active_status': True,
                'metadata': {
                    'ip_address': node_info['ip_address'],
                    'model': node_info['model'],
                    'firmware_version': node_info['firmware_version']
                }
            }
            
            # Register with our API
            response = requests.post(
                f"{CONFIG.get('firebase', {}).get('api_url')}/admin/nodes",
                headers=self.api_headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Node {node_info['name']} registered successfully")
                return True
            else:
                logger.error(f"❌ Failed to register node: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error registering node: {e}")
            return False

class RajantMacMonitor:
    """Monitors MAC addresses from Rajant nodes with smart mobile device filtering."""
    
    def __init__(self):
        self.api_headers = {'Content-Type': 'application/json'}
        self.last_seen_macs = {}
        
        # Initialize mobile phone detector
        if MAC_FILTERING_AVAILABLE:
            self.mobile_detector = MobilePhoneDetector()
            logger.info("📱 Mobile device filtering initialized")
        else:
            self.mobile_detector = None
    
    async def start_monitoring(self, nodes: List[Dict]):
        """Start monitoring MAC addresses from all nodes."""
        logger.info("🔍 Starting MAC address monitoring...")
        
        # Log filter statistics periodically
        scan_count = 0
        
        while True:
            try:
                for node in nodes:
                    await self._monitor_node_associations(node)
                
                scan_count += 1
                
                # Log filtering statistics every 10 scans (~5 minutes with 30s interval)
                if scan_count % 10 == 0 and self.mobile_detector:
                    stats = self.mobile_detector.get_device_stats()
                    logger.info(f"📊 Filtering Stats - Total: {stats['total_devices_seen']}, Mobile: {stats['mobile_devices']}, Filtered: {stats['infrastructure_devices']}, Efficiency: {stats['filter_efficiency']:.1%}")
                
                await asyncio.sleep(CONFIG.get('monitoring', {}).get('scan_interval', 30))
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                # Log final statistics
                if self.mobile_detector:
                    stats = self.mobile_detector.get_device_stats()
                    logger.info(f"📊 Final Filtering Stats - Total: {stats['total_devices_seen']}, Mobile: {stats['mobile_devices']}, Filtered: {stats['infrastructure_devices']}")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_node_associations(self, node: Dict):
        """Monitor MAC addresses associated with a specific node."""
        try:
            # Get associated devices from Rajant node
            associated_macs = await self._get_associated_devices(node)
            
            # Apply smart mobile device filtering
            if self.mobile_detector and associated_macs:
                # Convert to format expected by filter
                device_list = [
                    {
                        'mac': mac_info['mac_address'],
                        'signal': mac_info['signal_strength'],
                        'node': node['node_id']
                    }
                    for mac_info in associated_macs
                ]
                
                # Filter for mobile devices only
                mobile_devices = self.mobile_detector.filter_mobile_devices(device_list)
                
                # Log filtering results
                total_devices = len(device_list)
                mobile_count = len(mobile_devices)
                if total_devices > mobile_count:
                    filtered_count = total_devices - mobile_count
                    logger.info(f"🚫 Filtered out {filtered_count} non-mobile devices at {node['name']}")
                
                # Process only mobile devices
                for mobile_device in mobile_devices:
                    # Convert back to original format with additional mobile info
                    mac_info = {
                        'mac_address': mobile_device['mac'],
                        'signal_strength': mobile_device['signal'],
                        'association_time': datetime.now().isoformat(),
                        'device_type': mobile_device['device_type'],
                        'confidence': mobile_device['confidence'],
                        'vendor': mobile_device['vendor']
                    }
                    await self._process_mac_detection(node, mac_info)
            else:
                # No filtering available or no devices - process all
                for mac_info in associated_macs:
                    await self._process_mac_detection(node, mac_info)
                
        except Exception as e:
            logger.error(f"❌ Error monitoring node {node['name']}: {e}")
    
    async def _get_associated_devices(self, node: Dict) -> List[Dict]:
        """Get list of devices associated with this Rajant node using rajant-api."""
        
        if not RAJANT_API_AVAILABLE:
            logger.warning(f"⚠️ Rajant API not available, using mock data for {node['name']}")
            return self._get_mock_devices(node)
        
        try:
            # Initialize Rajant API connection
            rajant = RajantAPI(
                host=node['ip_address'],
                username=CONFIG.get('rajant_username', 'admin'),
                password=CONFIG.get('rajant_password', 'admin')
            )
            
            # Connect to node
            await rajant.connect()
            
            # Get wireless client information
            wireless_clients = await rajant.get_wireless_clients()
            
            # Convert to our format
            devices = []
            for client in wireless_clients:
                device_info = {
                    'mac_address': client.get('mac_address', ''),
                    'signal_strength': client.get('rssi', -50),
                    'association_time': client.get('connected_time', datetime.now().isoformat()),
                    'device_type': 'unknown',  # Will be determined by MAC filtering
                    'data_rate': client.get('data_rate', ''),
                    'ip_address': client.get('ip_address', ''),
                    'vendor': client.get('vendor', 'Unknown')
                }
                devices.append(device_info)
            
            await rajant.disconnect()
            logger.info(f"📡 Retrieved {len(devices)} clients from {node['name']}")
            return devices
            
        except Exception as e:
            logger.error(f"❌ Failed to get clients from {node['name']} ({node['ip_address']}): {e}")
            # Fallback to mock data for testing
            return self._get_mock_devices(node)
    
    def _get_mock_devices(self, node: Dict) -> List[Dict]:
        """Fallback mock data for testing when Rajant API is not available."""
        
        if node['node_id'] == 'rajant_10':  # Entrance node
            return [
                # Mobile devices (should be detected)
                {
                    'mac_address': '3C:2E:FF:12:34:56',  # iPhone
                    'signal_strength': -45,
                    'association_time': datetime.now().isoformat(),
                    'device_type': 'mobile'
                },
                {
                    'mac_address': '28:39:26:78:9A:BC',  # Samsung
                    'signal_strength': -52,
                    'association_time': datetime.now().isoformat(),
                    'device_type': 'mobile'
                },
                # Infrastructure devices (should be filtered out)
                {
                    'mac_address': 'B8:27:EB:DE:F0:12',  # Raspberry Pi
                    'signal_strength': -30,
                    'association_time': datetime.now().isoformat(),
                    'device_type': 'infrastructure'
                },
                {
                    'mac_address': '04:18:D6:9A:BC:DE',  # Ubiquiti AP
                    'signal_strength': -25,
                    'association_time': datetime.now().isoformat(),
                    'device_type': 'infrastructure'
                }
            ]
        elif node['node_id'] == 'rajant_11':  # Section A node
            return [
                {
                    'mac_address': '5C:51:4F:66:77:88',  # Google Pixel
                    'signal_strength': -48,
                    'association_time': datetime.now().isoformat(),
                    'device_type': 'mobile'
                },
                {
                    'mac_address': 'A2:11:22:33:44:55',  # Randomized MAC (iPhone)
                    'signal_strength': -55,
                    'association_time': datetime.now().isoformat(),
                    'device_type': 'mobile'
                },
                # Non-mobile device
                {
                    'mac_address': '00:0C:42:34:56:78',  # Cisco Switch
                    'signal_strength': -25,
                    'association_time': datetime.now().isoformat(),
                    'device_type': 'infrastructure'
                }
            ]
        elif node['node_id'] == 'rajant_12':  # Exit node
            return [
                {
                    'mac_address': '0C:96:BF:AA:BB:CC',  # Huawei Android
                    'signal_strength': -42,
                    'association_time': datetime.now().isoformat(),
                    'device_type': 'mobile'
                }
            ]
        
        return []
    
    async def _process_mac_detection(self, node: Dict, mac_info: Dict):
        """Process a MAC address detection and send to Firebase."""
        try:
            mac_address = mac_info['mac_address']
            
            # Check if this is a new detection or significant change
            last_node = self.last_seen_macs.get(mac_address)
            if last_node == node['node_id']:
                return  # Same node, skip duplicate
            
            # Log position update with enhanced mobile device info
            position_data = {
                'mac_address': mac_address,
                'node_id': node['node_id'],
                'timestamp': datetime.now().isoformat(),
                'signal_strength': mac_info['signal_strength'],
                'detection_source': 'rajant_node',
                'metadata': {
                    'node_ip': node['ip_address'],
                    'device_type': mac_info.get('device_type', 'unknown'),
                    'vendor': mac_info.get('vendor', 'Unknown'),
                    'confidence': mac_info.get('confidence', 1.0),
                    'filtering_applied': MAC_FILTERING_AVAILABLE
                }
            }
            
            # Send to Firebase API
            success = await self._send_position_update(position_data)
            
            if success:
                self.last_seen_macs[mac_address] = node['node_id']
                vendor_info = mac_info.get('vendor', 'Unknown')
                confidence = mac_info.get('confidence', 1.0)
                logger.info(f"📱 Mobile device {mac_address} ({vendor_info}) detected at {node['name']} (Signal: {mac_info['signal_strength']} dBm, Confidence: {confidence:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Error processing MAC detection: {e}")
    
    async def _send_position_update(self, position_data: Dict) -> bool:
        """Send position update to Firebase Cloud Functions."""
        try:
            response = requests.post(
                f"{CONFIG.get('firebase', {}).get('api_url')}/log-position",
                headers=self.api_headers,
                json=position_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"❌ Failed to send position update: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending position update: {e}")
            return False

async def test_configuration():
    """Test configuration and ping nodes."""
    logger.info("🧪 Testing configuration...")
    
    # Test config loading
    logger.info(f"📋 Loaded config: {CONFIG}")
    
    # Test node discovery
    discovery = RajantNodeDiscovery()
    nodes = await discovery.discover_nodes()
    
    if nodes:
        logger.info(f"✅ Found {len(nodes)} nodes in configuration")
        for node in nodes:
            logger.info(f"  - {node['name']} ({node['ip_address']})")
    else:
        logger.error("❌ No nodes found in configuration")
    
    # Test ping to each configured node
    rajant_nodes = CONFIG.get('rajant', {}).get('nodes', [])
    logger.info(f"🔍 Testing ping to {len(rajant_nodes)} configured nodes...")
    
    for node in rajant_nodes:
        ip = node.get('ip')
        name = node.get('name', 'Unknown')
        if ip:
            is_reachable = await discovery._ping_node(ip)
            status = "✅ REACHABLE" if is_reachable else "❌ NOT REACHABLE"
            logger.info(f"  {status}: {name} ({ip})")

async def main():
    """Main integration function."""
    parser = argparse.ArgumentParser(description='Rajant Integration for Tunnel Tracking')
    parser.add_argument('--discover-only', action='store_true', help='Only discover and register nodes')
    parser.add_argument('--monitor-only', action='store_true', help='Only monitor MAC addresses')
    parser.add_argument('--test-config', action='store_true', help='Test configuration and ping nodes')
    args = parser.parse_args()
    
    # Test configuration if requested
    if args.test_config:
        await test_configuration()
        return
    
    logger.info("🚀 Starting Rajant Integration...")
    
    # Initialize components
    node_discovery = RajantNodeDiscovery()
    mac_monitor = RajantMacMonitor()
    
    # Discover and register nodes
    if not args.monitor_only:
        nodes = await node_discovery.discover_nodes()
        
        for node in nodes:
            await node_discovery.register_node_in_firebase(node)
    
    # Start monitoring if requested
    if not args.discover_only:
        if not args.monitor_only:
            # Get nodes from discovery
            nodes = await node_discovery.discover_nodes()
        else:
            # Load nodes from configuration or API
            nodes = [
                {'node_id': 'rajant_10', 'name': 'Entrance Node', 'ip_address': '192.168.100.10'},
                {'node_id': 'rajant_11', 'name': 'Section A Node', 'ip_address': '192.168.100.11'},
                {'node_id': 'rajant_12', 'name': 'Exit Node', 'ip_address': '192.168.100.12'},
            ]
        
        await mac_monitor.start_monitoring(nodes)

if __name__ == "__main__":
    asyncio.run(main()) 