#!/usr/bin/env python3
"""
Smart MAC Address Filtering for Mobile Phone Detection
Filters out infrastructure devices and focuses on human-carried devices
"""

import re
import requests
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class DeviceInfo:
    mac: str
    vendor: str
    device_type: str
    confidence: float
    first_seen: datetime
    signal_pattern: List[int]
    behavior_score: float

class MobilePhoneDetector:
    """
    Detekterer mobiltelefoner vs andre enheter basert på:
    1. MAC OUI (vendor identification)
    2. Signal oppførsel
    3. Bevegelsesmønster  
    4. WiFi association patterns
    """
    
    def __init__(self):
        # Mobile phone OUI database (første 3 bytes av MAC)
        self.mobile_ouis = self._load_mobile_ouis()
        
        # Infrastructure device OUIs to exclude
        self.infrastructure_ouis = self._load_infrastructure_ouis()
        
        # Device behavior tracking
        self.device_history: Dict[str, DeviceInfo] = {}
        
        # Filtering thresholds
        self.config = {
            'signal_variance_threshold': 10,  # Mobile phones move = signal varies
            'min_confidence_score': 0.7,     # 70% confidence for mobile detection
            'behavior_window_minutes': 30,   # Analyze behavior over 30 minutes
            'static_device_threshold': 5,    # If signal stable for 5+ scans = likely static
        }
    
    def _load_mobile_ouis(self) -> Dict[str, str]:
        """Load known mobile phone vendor OUIs"""
        return {
            # Apple (iPhone)
            '00:03:93': 'Apple iPhone',
            '00:0A:95': 'Apple iPhone', 
            '00:17:F2': 'Apple iPhone',
            '00:1B:63': 'Apple iPhone',
            '00:1E:C2': 'Apple iPhone',
            '00:23:12': 'Apple iPhone',
            '00:25:BC': 'Apple iPhone',
            '00:26:08': 'Apple iPhone',
            '04:0C:CE': 'Apple iPhone',
            '04:15:52': 'Apple iPhone',
            '04:1E:64': 'Apple iPhone',
            '04:69:F2': 'Apple iPhone',
            '04:DB:56': 'Apple iPhone',
            '04:F7:E4': 'Apple iPhone',
            '08:00:07': 'Apple iPhone',
            '0C:3E:9F': 'Apple iPhone',
            '0C:74:C2': 'Apple iPhone',
            '10:40:F3': 'Apple iPhone',
            '14:20:5E': 'Apple iPhone',
            '14:7D:DA': 'Apple iPhone',
            '18:AF:8F': 'Apple iPhone',
            '1C:AB:A7': 'Apple iPhone',
            '20:A2:E4': 'Apple iPhone',
            '24:A0:74': 'Apple iPhone',
            '28:37:37': 'Apple iPhone',
            '2C:1F:23': 'Apple iPhone',
            '30:35:AD': 'Apple iPhone',
            '30:90:AB': 'Apple iPhone',
            '34:A3:95': 'Apple iPhone',
            '38:B5:4D': 'Apple iPhone',
            '3C:2E:FF': 'Apple iPhone',
            '40:83:DE': 'Apple iPhone',
            '44:4C:0C': 'Apple iPhone',
            '48:74:6E': 'Apple iPhone',
            '4C:3C:16': 'Apple iPhone',
            '50:ED:3C': 'Apple iPhone',
            '54:72:4F': 'Apple iPhone',
            '58:55:CA': 'Apple iPhone',
            '5C:95:AE': 'Apple iPhone',
            '60:F4:45': 'Apple iPhone',
            '64:B0:A6': 'Apple iPhone',
            '68:AE:20': 'Apple iPhone',
            '6C:72:20': 'Apple iPhone',
            '70:1C:E7': 'Apple iPhone',
            '74:E2:F5': 'Apple iPhone',
            '78:4F:43': 'Apple iPhone',
            '7C:6D:62': 'Apple iPhone',
            '80:BE:05': 'Apple iPhone',
            '84:38:35': 'Apple iPhone',
            '88:66:5A': 'Apple iPhone',
            '8C:85:90': 'Apple iPhone',
            '90:72:40': 'Apple iPhone',
            '94:E9:6A': 'Apple iPhone',
            '98:FE:94': 'Apple iPhone',
            '9C:04:EB': 'Apple iPhone',
            'A0:99:9B': 'Apple iPhone',
            'A4:5E:60': 'Apple iPhone',
            'A8:51:AB': 'Apple iPhone',
            'AC:87:A3': 'Apple iPhone',
            'B0:65:BD': 'Apple iPhone',
            'B4:F0:AB': 'Apple iPhone',
            'B8:78:2E': 'Apple iPhone',
            'BC:3B:AF': 'Apple iPhone',
            'C0:9A:D0': 'Apple iPhone',
            'C4:B3:01': 'Apple iPhone',
            'C8:2A:14': 'Apple iPhone',
            'CC:25:EF': 'Apple iPhone',
            'D0:23:DB': 'Apple iPhone',
            'D4:90:9C': 'Apple iPhone',
            'D8:1D:72': 'Apple iPhone',
            'DC:2B:2A': 'Apple iPhone',
            'E0:AC:CB': 'Apple iPhone',
            'E4:8B:7F': 'Apple iPhone',
            'E8:80:2E': 'Apple iPhone',
            'EC:35:86': 'Apple iPhone',
            'F0:24:75': 'Apple iPhone',
            'F4:F1:5A': 'Apple iPhone',
            'F8:27:93': 'Apple iPhone',
            'FC:25:3F': 'Apple iPhone',
            
            # Samsung (Android)
            '00:07:AB': 'Samsung Android',
            '00:0E:07': 'Samsung Android',
            '00:12:47': 'Samsung Android', 
            '00:15:99': 'Samsung Android',
            '00:16:32': 'Samsung Android',
            '00:17:C9': 'Samsung Android',
            '00:1A:8A': 'Samsung Android',
            '00:1D:25': 'Samsung Android',
            '00:1E:E1': 'Samsung Android',
            '00:21:19': 'Samsung Android',
            '00:23:39': 'Samsung Android',
            '00:26:37': 'Samsung Android',
            '04:18:D6': 'Samsung Android',
            '08:37:3D': 'Samsung Android',
            '0C:14:20': 'Samsung Android',
            '0C:89:10': 'Samsung Android',
            '10:1D:C0': 'Samsung Android',
            '14:7F:3C': 'Samsung Android',
            '18:3A:2D': 'Samsung Android',
            '1C:5A:3E': 'Samsung Android',
            '20:13:E0': 'Samsung Android',
            '24:4B:81': 'Samsung Android',
            '28:39:26': 'Samsung Android',
            '2C:44:01': 'Samsung Android',
            '30:07:4D': 'Samsung Android',
            '34:23:87': 'Samsung Android',
            '38:AA:3C': 'Samsung Android',
            '3C:5A:B4': 'Samsung Android',
            '40:0E:85': 'Samsung Android',
            '44:00:10': 'Samsung Android',
            '48:5A:3F': 'Samsung Android',
            '4C:BC:42': 'Samsung Android',
            '50:CC:F8': 'Samsung Android',
            '54:88:0E': 'Samsung Android',
            '58:1F:AA': 'Samsung Android',
            '5C:0A:5B': 'Samsung Android',
            '60:6B:BD': 'Samsung Android',
            '64:16:66': 'Samsung Android',
            '68:EB:C5': 'Samsung Android',
            '6C:2F:2C': 'Samsung Android',
            '70:F9:27': 'Samsung Android',
            '74:45:8A': 'Samsung Android',
            '78:25:AD': 'Samsung Android',
            '7C:61:66': 'Samsung Android',
            '80:57:19': 'Samsung Android',
            '84:25:3F': 'Samsung Android',
            '88:32:9B': 'Samsung Android',
            '8C:77:12': 'Samsung Android',
            '90:18:7C': 'Samsung Android',
            '94:35:0A': 'Samsung Android',
            '98:52:3D': 'Samsung Android',
            '9C:28:EF': 'Samsung Android',
            'A0:21:B7': 'Samsung Android',
            'A4:EB:D3': 'Samsung Android',
            'A8:DB:03': 'Samsung Android',
            'AC:5F:3E': 'Samsung Android',
            'B0:72:BF': 'Samsung Android',
            'B4:62:93': 'Samsung Android',
            'B8:5E:7B': 'Samsung Android',
            'BC:14:85': 'Samsung Android',
            'C0:BD:D1': 'Samsung Android',
            'C4:42:02': 'Samsung Android',
            'C8:BA:94': 'Samsung Android',
            'CC:07:AB': 'Samsung Android',
            'D0:17:6A': 'Samsung Android',
            'D4:87:D8': 'Samsung Android',
            'D8:90:E8': 'Samsung Android',
            'DC:71:96': 'Samsung Android',
            'E0:91:F5': 'Samsung Android',
            'E4:32:CB': 'Samsung Android',
            'E8:50:8B': 'Samsung Android',
            'EC:1F:72': 'Samsung Android',
            'F0:25:B7': 'Samsung Android',
            'F4:0F:24': 'Samsung Android',
            'F8:04:2E': 'Samsung Android',
            'FC:A6:21': 'Samsung Android',
            
            # Google (Pixel phones)
            '00:1A:11': 'Google Pixel',
            '04:C0:6F': 'Google Pixel',
            '5C:51:4F': 'Google Pixel',
            '64:C5:AA': 'Google Pixel',
            '8C:85:90': 'Google Pixel',
            'AC:37:43': 'Google Pixel',
            'B4:77:39': 'Google Pixel',
            'C4:43:8F': 'Google Pixel',
            'DC:2B:61': 'Google Pixel',
            'F8:8F:CA': 'Google Pixel',
            
            # Huawei/Honor
            '00:18:82': 'Huawei Android',
            '00:1E:10': 'Huawei Android',
            '00:25:9E': 'Huawei Android',
            '04:BD:88': 'Huawei Android',
            '08:7A:4C': 'Huawei Android',
            '0C:96:BF': 'Huawei Android',
            '10:1F:74': 'Huawei Android',
            '14:F6:D8': 'Huawei Android',
            '18:4F:32': 'Huawei Android',
            '1C:1D:67': 'Huawei Android',
            '20:F3:A3': 'Huawei Android',
            '24:09:95': 'Huawei Android',
            '28:C6:8E': 'Huawei Android',
            '2C:AB:25': 'Huawei Android',
            '30:B4:9E': 'Huawei Android',
            '34:6B:D3': 'Huawei Android',
            '38:BC:01': 'Huawei Android',
            '3C:8B:FE': 'Huawei Android',
            '40:4D:8E': 'Huawei Android',
            '44:6D:6C': 'Huawei Android',
            '48:DB:50': 'Huawei Android',
            '4C:54:99': 'Huawei Android',
            '50:8F:4C': 'Huawei Android',
            '54:25:EA': 'Huawei Android',
            '58:2A:F7': 'Huawei Android',
            '5C:C9:D3': 'Huawei Android',
            '60:DE:44': 'Huawei Android',
            '64:3E:8C': 'Huawei Android',
            '68:13:E2': 'Huawei Android',
            '6C:E8:73': 'Huawei Android',
            '70:72:3C': 'Huawei Android',
            '74:A7:22': 'Huawei Android',
            '78:D6:F0': 'Huawei Android',
            '7C:B2:1B': 'Huawei Android',
            '80:38:BC': 'Huawei Android',
            '84:A4:23': 'Huawei Android',
            '88:E3:AB': 'Huawei Android',
            '8C:34:FD': 'Huawei Android',
            '90:67:1C': 'Huawei Android',
            '94:04:9C': 'Huawei Android',
            '98:54:1B': 'Huawei Android',
            '9C:28:BF': 'Huawei Android',
            'A0:8C:FD': 'Huawei Android',
            'A4:50:46': 'Huawei Android',
            'A8:1E:84': 'Huawei Android',
            'AC:E2:D3': 'Huawei Android',
            'B0:E2:35': 'Huawei Android',
            'B4:CD:27': 'Huawei Android',
            'B8:08:CF': 'Huawei Android',
            'BC:25:E5': 'Huawei Android',
            'C0:EE:40': 'Huawei Android',
            'C4:0B:CB': 'Huawei Android',
            'C8:14:79': 'Huawei Android',
            'CC:B1:1A': 'Huawei Android',
            'D0:7E:35': 'Huawei Android',
            'D4:6A:6A': 'Huawei Android',
            'D8:49:2F': 'Huawei Android',
            'DC:D8:9D': 'Huawei Android',
            'E0:19:1D': 'Huawei Android',
            'E4:58:B8': 'Huawei Android',
            'E8:CD:2D': 'Huawei Android',
            'EC:23:3D': 'Huawei Android',
            'F0:79:59': 'Huawei Android',
            'F4:28:53': 'Huawei Android',
            'F8:98:B9': 'Huawei Android',
            'FC:48:EF': 'Huawei Android',
            
            # OnePlus
            '00:90:E6': 'OnePlus Android',
            '08:05:81': 'OnePlus Android',
            '0C:8D:DB': 'OnePlus Android',
            '10:68:3F': 'OnePlus Android',
            '14:D1:27': 'OnePlus Android',
            '18:4A:AE': 'OnePlus Android',
            '1C:B0:94': 'OnePlus Android',
            '20:68:9D': 'OnePlus Android',
            '24:CF:24': 'OnePlus Android',
            '28:E1:4C': 'OnePlus Android',
            '2C:F4:32': 'OnePlus Android',
            '30:E1:71': 'OnePlus Android',
            '34:97:F6': 'OnePlus Android',
            '38:A4:ED': 'OnePlus Android',
            '3C:BD:3E': 'OnePlus Android',
            '40:B0:76': 'OnePlus Android',
            '44:91:60': 'OnePlus Android',
            '48:C1:AC': 'OnePlus Android',
            '4C:49:E3': 'OnePlus Android',
            '50:8A:06': 'OnePlus Android',
            '54:E4:3A': 'OnePlus Android',
            '58:CB:52': 'OnePlus Android',
            '5C:A6:E6': 'OnePlus Android',
            '60:AB:14': 'OnePlus Android',
            '64:BC:0C': 'OnePlus Android',
            '68:EB:AE': 'OnePlus Android',
            '6C:24:08': 'OnePlus Android',
            '70:4A:0E': 'OnePlus Android',
            '74:4C:A1': 'OnePlus Android',
            '78:2B:CB': 'OnePlus Android',
            '7C:1C:4E': 'OnePlus Android',
            '80:7A:BF': 'OnePlus Android',
            '84:C7:EA': 'OnePlus Android',
            '88:83:5D': 'OnePlus Android',
            '8C:1A:B0': 'OnePlus Android',
            '90:E8:68': 'OnePlus Android',
            '94:65:9C': 'OnePlus Android',
            '98:22:EF': 'OnePlus Android',
            '9C:07:A3': 'OnePlus Android',
            'A0:C5:89': 'OnePlus Android',
            'A4:34:D9': 'OnePlus Android',
            'A8:26:D9': 'OnePlus Android',
            'AC:22:0B': 'OnePlus Android',
            'B0:A7:37': 'OnePlus Android',
            'B4:52:7E': 'OnePlus Android',
            'B8:9A:2A': 'OnePlus Android',
            'BC:25:E5': 'OnePlus Android',
            'C0:05:C2': 'OnePlus Android',
            'C4:07:2F': 'OnePlus Android',
            'C8:FF:77': 'OnePlus Android',
            'CC:15:31': 'OnePlus Android',
            'D0:53:49': 'OnePlus Android',
            'D4:6E:0E': 'OnePlus Android',
            'D8:55:A3': 'OnePlus Android',
            'DC:91:A7': 'OnePlus Android',
            'E0:B9:4D': 'OnePlus Android',
            'E4:42:A6': 'OnePlus Android',
            'E8:92:A4': 'OnePlus Android',
            'EC:F4:BB': 'OnePlus Android',
            'F0:27:2D': 'OnePlus Android',
            'F4:0E:22': 'OnePlus Android',
            'F8:63:3F': 'OnePlus Android',
            'FC:05:A6': 'OnePlus Android',
        }
    
    def _load_infrastructure_ouis(self) -> Dict[str, str]:
        """Load OUIs for infrastructure devices to EXCLUDE"""
        return {
            # Network Infrastructure
            '00:00:0C': 'Cisco Router/Switch',
            '00:01:42': 'Cisco Router/Switch', 
            '00:01:43': 'Cisco Router/Switch',
            '00:01:96': 'Cisco Router/Switch',
            '00:01:97': 'Cisco Router/Switch',
            '00:02:16': 'Cisco Router/Switch',
            '00:02:17': 'Cisco Router/Switch',
            '00:02:4A': 'Cisco Router/Switch',
            '00:02:4B': 'Cisco Router/Switch',
            '00:02:B9': 'Cisco Router/Switch',
            '00:02:BA': 'Cisco Router/Switch',
            '00:03:31': 'Cisco Router/Switch',
            '00:03:32': 'Cisco Router/Switch',
            '00:03:6B': 'Cisco Router/Switch',
            '00:03:6C': 'Cisco Router/Switch',
            '00:03:A0': 'Cisco Router/Switch',
            '00:03:E3': 'Cisco Router/Switch',
            '00:03:FD': 'Cisco Router/Switch',
            '00:03:FE': 'Cisco Router/Switch',
            '00:04:27': 'Cisco Router/Switch',
            '00:04:28': 'Cisco Router/Switch',
            '00:04:4D': 'Cisco Router/Switch',
            '00:04:6D': 'Cisco Router/Switch',
            '00:04:9A': 'Cisco Router/Switch',
            '00:04:C0': 'Cisco Router/Switch',
            '00:04:C1': 'Cisco Router/Switch',
            '00:04:DD': 'Cisco Router/Switch',
            
            # Ubiquiti (UniFi Access Points)
            '04:18:D6': 'Ubiquiti UniFi AP',
            '18:E8:29': 'Ubiquiti UniFi AP',
            '24:5A:4C': 'Ubiquiti UniFi AP',
            '44:D9:E7': 'Ubiquiti UniFi AP',
            '68:72:51': 'Ubiquiti UniFi AP',
            '74:83:C2': 'Ubiquiti UniFi AP',
            '78:8A:20': 'Ubiquiti UniFi AP',
            '80:2A:A8': 'Ubiquiti UniFi AP',
            'B4:FB:E4': 'Ubiquiti UniFi AP',
            'DC:9F:DB': 'Ubiquiti UniFi AP',
            'E4:38:83': 'Ubiquiti UniFi AP',
            'F0:9F:C2': 'Ubiquiti UniFi AP',
            'FC:EC:DA': 'Ubiquiti UniFi AP',
            
            # TP-Link Access Points/Routers
            '14:CC:20': 'TP-Link Router/AP',
            '50:C7:BF': 'TP-Link Router/AP',
            '60:E3:27': 'TP-Link Router/AP',
            '6C:5A:B0': 'TP-Link Router/AP',
            '84:16:F9': 'TP-Link Router/AP',
            'A0:F3:C1': 'TP-Link Router/AP',
            'B0:4E:26': 'TP-Link Router/AP',
            'C0:25:A2': 'TP-Link Router/AP',
            'E8:DE:27': 'TP-Link Router/AP',
            'F4:EC:38': 'TP-Link Router/AP',
            
            # Raspberry Pi (should be excluded from client detection)
            'B8:27:EB': 'Raspberry Pi',
            'DC:A6:32': 'Raspberry Pi',
            'E4:5F:01': 'Raspberry Pi',
            
            # Industrial IoT Devices
            '00:13:A2': 'Digi XBee',
            '00:50:C2': 'IEEE 802.11 devices',
            '02:00:00': 'Private/Random MAC',
            
            # Rajant Mesh Nodes
            '00:0E:8E': 'Rajant Mesh Node',
            '00:1C:9E': 'Rajant Mesh Node',
            '00:24:7E': 'Rajant Mesh Node',
        }
    
    def get_oui(self, mac: str) -> str:
        """Extract OUI (first 3 bytes) from MAC address"""
        return mac.upper().replace(':', '').replace('-', '')[:6]
    
    def format_oui(self, oui: str) -> str:
        """Format OUI with colons: ABC123 -> AB:C1:23"""
        return f"{oui[:2]}:{oui[2:4]}:{oui[4:6]}"
    
    def is_mobile_device(self, mac: str) -> Tuple[bool, float, str]:
        """
        Determine if MAC address belongs to mobile device
        Returns: (is_mobile, confidence, device_type)
        """
        oui = self.get_oui(mac)
        formatted_oui = self.format_oui(oui)
        
        # Check against mobile phone database
        if formatted_oui in self.mobile_ouis:
            return True, 0.95, self.mobile_ouis[formatted_oui]
        
        # Check against infrastructure exclusions  
        if formatted_oui in self.infrastructure_ouis:
            return False, 0.95, self.infrastructure_ouis[formatted_oui]
        
        # Randomized MAC addresses (iOS/Android privacy feature)
        if self._is_randomized_mac(mac):
            return True, 0.8, "Mobile (Randomized MAC)"
        
        # Unknown OUI - analyze behavior
        return self._analyze_unknown_device(mac)
    
    def _is_randomized_mac(self, mac: str) -> bool:
        """
        Detect randomized MAC addresses used by modern mobile devices
        Second bit of first octet = 1 indicates locally administered (randomized)
        """
        try:
            first_octet = int(mac.split(':')[0], 16)
            return (first_octet & 0x02) != 0  # Check locally administered bit
        except:
            return False
    
    def _analyze_unknown_device(self, mac: str) -> Tuple[bool, float, str]:
        """
        Analyze device behavior for unknown OUIs
        Mobile devices typically show:
        - Variable signal strength (movement)
        - Periodic connections/disconnections
        - Shorter association times
        """
        if mac not in self.device_history:
            return False, 0.3, "Unknown Device (Need More Data)"
        
        device = self.device_history[mac]
        
        # Analyze signal variance (movement indicates mobile)
        signal_variance = self._calculate_signal_variance(device.signal_pattern)
        movement_score = min(signal_variance / self.config['signal_variance_threshold'], 1.0)
        
        # Analyze connection behavior
        behavior_score = device.behavior_score
        
        # Combined confidence
        confidence = (movement_score * 0.6 + behavior_score * 0.4)
        
        is_mobile = confidence > self.config['min_confidence_score']
        device_type = f"Unknown Mobile (Behavior Score: {confidence:.2f})" if is_mobile else "Unknown Static Device"
        
        return is_mobile, confidence, device_type
    
    def _calculate_signal_variance(self, signals: List[int]) -> float:
        """Calculate signal strength variance to detect movement"""
        if len(signals) < 2:
            return 0
        
        avg = sum(signals) / len(signals)
        variance = sum((s - avg) ** 2 for s in signals) / len(signals)
        return variance ** 0.5  # Standard deviation
    
    def update_device_history(self, mac: str, signal_strength: int, node_id: str):
        """Update device behavior tracking"""
        now = datetime.now()
        
        if mac not in self.device_history:
            self.device_history[mac] = DeviceInfo(
                mac=mac,
                vendor="Unknown",
                device_type="Unknown", 
                confidence=0.0,
                first_seen=now,
                signal_pattern=[signal_strength],
                behavior_score=0.0
            )
        else:
            device = self.device_history[mac]
            device.signal_pattern.append(signal_strength)
            
            # Keep only recent signal data
            cutoff_time = now - timedelta(minutes=self.config['behavior_window_minutes'])
            # Simplified: keep last 20 measurements
            device.signal_pattern = device.signal_pattern[-20:]
            
            # Update behavior score based on patterns
            device.behavior_score = self._calculate_behavior_score(device)
    
    def _calculate_behavior_score(self, device: DeviceInfo) -> float:
        """
        Calculate behavior score indicating mobile device probability
        Factors:
        - Signal variance (movement)
        - Connection frequency 
        - Time patterns
        """
        # Signal movement score
        signal_variance = self._calculate_signal_variance(device.signal_pattern)
        movement_score = min(signal_variance / 15.0, 1.0)  # Normalize to 0-1
        
        # Time-based patterns (mobile devices connect during work hours)
        time_score = 0.7  # Simplified - could analyze connection times
        
        # Connection frequency (mobile devices connect/disconnect more)
        frequency_score = 0.6  # Simplified - could track connection events
        
        return (movement_score * 0.5 + time_score * 0.3 + frequency_score * 0.2)
    
    def filter_mobile_devices(self, detected_devices: List[Dict]) -> List[Dict]:
        """
        Filter list of detected devices to include only mobile phones
        Input: [{"mac": "AA:BB:CC:DD:EE:FF", "signal": -45, "node": "entrance"}]
        Output: Filtered list with mobile devices only + confidence scores
        """
        mobile_devices = []
        
        for device in detected_devices:
            mac = device['mac']
            signal = device.get('signal', -50)
            node = device.get('node', 'unknown')
            
            # Update behavior tracking
            self.update_device_history(mac, signal, node)
            
            # Check if mobile device
            is_mobile, confidence, device_type = self.is_mobile_device(mac)
            
            if is_mobile:
                device_info = {
                    **device,  # Original device data
                    'is_mobile': True,
                    'confidence': confidence,
                    'device_type': device_type,
                    'vendor': device_type.split()[0] if ' ' in device_type else 'Unknown',
                    'filter_reason': 'Mobile Device Detected'
                }
                mobile_devices.append(device_info)
            else:
                # Log filtered out device for debugging
                print(f"🚫 Filtered out: {mac} - {device_type} (confidence: {confidence:.2f})")
        
        return mobile_devices
    
    def get_device_stats(self) -> Dict:
        """Get filtering statistics"""
        total_devices = len(self.device_history)
        mobile_count = sum(1 for mac in self.device_history 
                          if self.is_mobile_device(mac)[0])
        
        return {
            'total_devices_seen': total_devices,
            'mobile_devices': mobile_count,
            'infrastructure_devices': total_devices - mobile_count,
            'filter_efficiency': mobile_count / total_devices if total_devices > 0 else 0
        }

# Example usage function
def demo_mobile_filtering():
    """Demonstrate mobile device filtering"""
    detector = MobilePhoneDetector()
    
    # Simulate detected devices in tunnel
    test_devices = [
        {"mac": "3C:2E:FF:12:34:56", "signal": -45, "node": "entrance"},      # iPhone
        {"mac": "28:39:26:78:9A:BC", "signal": -52, "node": "entrance"},      # Samsung
        {"mac": "B8:27:EB:DE:F0:12", "signal": -30, "node": "entrance"},      # Raspberry Pi
        {"mac": "00:0C:42:34:56:78", "signal": -25, "node": "entrance"},      # Cisco Switch
        {"mac": "04:18:D6:9A:BC:DE", "signal": -40, "node": "entrance"},      # Ubiquiti AP
        {"mac": "A2:11:22:33:44:55", "signal": -48, "node": "middle"},        # Randomized MAC (iPhone)
        {"mac": "5C:51:4F:66:77:88", "signal": -55, "node": "middle"},        # Google Pixel
    ]
    
    print("🔍 Testing Mobile Device Filtering:")
    print("=" * 50)
    
    # Filter devices
    mobile_devices = detector.filter_mobile_devices(test_devices)
    
    print(f"\n✅ Detected Mobile Devices: {len(mobile_devices)}")
    for device in mobile_devices:
        print(f"  📱 {device['mac']} - {device['device_type']} (confidence: {device['confidence']:.2f})")
    
    print(f"\n📊 Filtering Statistics:")
    stats = detector.get_device_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    demo_mobile_filtering() 