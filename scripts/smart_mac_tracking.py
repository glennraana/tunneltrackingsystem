#!/usr/bin/env python3
"""
Smart MAC Tracking System
========================

Handles MAC address randomization and provides intelligent device tracking
using multiple identification methods beyond just MAC addresses.

Features:
- MAC randomization detection
- Device fingerprinting
- Signal pattern analysis
- Behavioral tracking
- Multi-factor device identification
"""

import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class DeviceFingerprint:
    """Device identification based on multiple factors."""
    current_mac: str
    signal_strength: int
    signal_pattern: List[int]
    connection_time: datetime
    movement_pattern: List[str]
    device_capabilities: Dict
    vendor_info: str
    
class SmartMACTracker:
    """Enhanced MAC tracking with randomization handling."""
    
    def __init__(self):
        self.mac_history = defaultdict(list)
        self.device_fingerprints = {}
        self.known_users = {}  # registered users
        self.potential_matches = defaultdict(list)
        self.randomization_patterns = {}
        
    def register_user(self, name: str, mac_address: str) -> bool:
        """Register a user with their MAC address."""
        try:
            # Store user registration
            self.known_users[mac_address] = {
                'name': name,
                'registered_at': datetime.now(),
                'mac_history': [mac_address],
                'is_randomized': self.detect_randomized_mac(mac_address)
            }
            
            print(f"✅ User registered: {name} with MAC {mac_address}")
            
            # Check if MAC appears randomized
            if self.detect_randomized_mac(mac_address):
                print(f"⚠️ Warning: {name}'s MAC appears randomized. Consider disabling MAC randomization.")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ User registration failed: {e}")
            return False
    
    def detect_randomized_mac(self, mac_address: str) -> bool:
        """Detect if a MAC address is likely randomized."""
        # Remove colons and convert to uppercase
        mac_clean = mac_address.replace(':', '').upper()
        
        # Check for randomized MAC patterns
        randomized_indicators = [
            # Locally administered bit set (2nd bit of first octet)
            lambda mac: int(mac[1], 16) & 0x2 != 0,
            
            # Common randomized prefixes
            lambda mac: mac.startswith(('02', '06', '0A', '0E')),
            
            # Apple randomized MAC patterns
            lambda mac: mac.startswith(('DA', 'DE', 'D6', 'D2')),
            
            # Pattern analysis (too random)
            lambda mac: self._analyze_randomness(mac)
        ]
        
        return any(indicator(mac_clean) for indicator in randomized_indicators)
    
    def _analyze_randomness(self, mac_clean: str) -> bool:
        """Analyze if MAC appears too random vs. manufacturer pattern."""
        # Check for manufacturer OUI patterns
        oui = mac_clean[:6]
        
        # Known manufacturer OUIs (first 3 octets)
        known_ouis = {
            'Apple': ['001EC2', '0050E4', '001D4F', '002608', '0023DF'],
            'Samsung': ['001377', '002566', '001AA0', '0021FB'],
            'Google': ['DA0E14', 'F4F5E8', '3C5AB4'],
            # Add more as needed
        }
        
        # If OUI is unknown and follows certain patterns, likely randomized
        if not any(oui in ouis for ouis in known_ouis.values()):
            # Additional randomness checks
            return True
            
        return False
    
    def create_device_fingerprint(self, mac: str, signal: int, 
                                node_id: str, capabilities: Dict = None) -> DeviceFingerprint:
        """Create device fingerprint for identification."""
        
        # Get or initialize signal pattern
        if mac not in self.mac_history:
            self.mac_history[mac] = []
        
        self.mac_history[mac].append({
            'signal': signal,
            'node': node_id,
            'timestamp': datetime.now()
        })
        
        # Limit history size
        if len(self.mac_history[mac]) > 50:
            self.mac_history[mac] = self.mac_history[mac][-50:]
        
        # Create signal pattern
        signal_pattern = [entry['signal'] for entry in self.mac_history[mac][-10:]]
        movement_pattern = [entry['node'] for entry in self.mac_history[mac][-5:]]
        
        return DeviceFingerprint(
            current_mac=mac,
            signal_strength=signal,
            signal_pattern=signal_pattern,
            connection_time=datetime.now(),
            movement_pattern=movement_pattern,
            device_capabilities=capabilities or {},
            vendor_info=self._get_vendor_info(mac)
        )
    
    def _get_vendor_info(self, mac: str) -> str:
        """Get vendor information from MAC OUI."""
        oui = mac.replace(':', '')[:6].upper()
        
        # Simplified vendor mapping
        vendor_map = {
            '001EC2': 'Apple',
            '002608': 'Apple', 
            'DA0E14': 'Google',
            '001377': 'Samsung',
            # Add more vendors
        }
        
        return vendor_map.get(oui, 'Unknown')
    
    def find_potential_user_match(self, fingerprint: DeviceFingerprint) -> Optional[str]:
        """Find potential user match using multiple factors."""
        
        # Direct MAC match (best case)
        if fingerprint.current_mac in self.known_users:
            return self.known_users[fingerprint.current_mac]['name']
        
        # Check for recently disconnected user with similar patterns
        best_match = None
        best_score = 0
        
        for mac, user_data in self.known_users.items():
            if user_data.get('is_randomized', False):
                # Calculate similarity score
                score = self._calculate_similarity_score(fingerprint, mac, user_data)
                
                if score > best_score and score > 0.7:  # Threshold for match
                    best_match = user_data['name']
                    best_score = score
        
        return best_match
    
    def _calculate_similarity_score(self, fingerprint: DeviceFingerprint, 
                                  stored_mac: str, user_data: Dict) -> float:
        """Calculate similarity score between device fingerprint and stored user."""
        score = 0.0
        factors = 0
        
        # Vendor similarity
        stored_vendor = self._get_vendor_info(stored_mac)
        if stored_vendor == fingerprint.vendor_info and stored_vendor != 'Unknown':
            score += 0.3
        factors += 1
        
        # Signal pattern similarity (if available)
        if stored_mac in self.mac_history and len(self.mac_history[stored_mac]) > 5:
            stored_signals = [entry['signal'] for entry in self.mac_history[stored_mac][-10:]]
            if self._signal_pattern_similarity(fingerprint.signal_pattern, stored_signals) > 0.8:
                score += 0.4
        factors += 1
        
        # Movement pattern similarity
        if stored_mac in self.mac_history:
            stored_movement = [entry['node'] for entry in self.mac_history[stored_mac][-5:]]
            if self._movement_pattern_similarity(fingerprint.movement_pattern, stored_movement) > 0.6:
                score += 0.3
        factors += 1
        
        return score / factors if factors > 0 else 0.0
    
    def _signal_pattern_similarity(self, pattern1: List[int], pattern2: List[int]) -> float:
        """Calculate similarity between signal patterns."""
        if not pattern1 or not pattern2:
            return 0.0
        
        # Simple correlation calculation
        min_len = min(len(pattern1), len(pattern2))
        if min_len < 3:
            return 0.0
        
        p1 = pattern1[-min_len:]
        p2 = pattern2[-min_len:]
        
        # Calculate variance similarity
        diff_sum = sum(abs(a - b) for a, b in zip(p1, p2))
        max_diff = min_len * 100  # Assume max signal diff is 100dB
        
        return max(0, 1 - (diff_sum / max_diff))
    
    def _movement_pattern_similarity(self, pattern1: List[str], pattern2: List[str]) -> float:
        """Calculate similarity between movement patterns."""
        if not pattern1 or not pattern2:
            return 0.0
        
        # Check for common movement sequences
        common_sequences = 0
        total_sequences = max(len(pattern1), len(pattern2))
        
        for i in range(min(len(pattern1), len(pattern2))):
            if pattern1[-(i+1)] == pattern2[-(i+1)]:
                common_sequences += 1
        
        return common_sequences / total_sequences if total_sequences > 0 else 0.0
    
    def track_device(self, mac: str, signal: int, node_id: str, 
                    capabilities: Dict = None) -> Dict:
        """Main tracking method with smart identification."""
        
        # Create device fingerprint
        fingerprint = self.create_device_fingerprint(mac, signal, node_id, capabilities)
        
        # Try to identify user
        identified_user = self.find_potential_user_match(fingerprint)
        
        # Detect if this is a randomized MAC
        is_randomized = self.detect_randomized_mac(mac)
        
        result = {
            'mac_address': mac,
            'identified_user': identified_user,
            'is_randomized': is_randomized,
            'signal_strength': signal,
            'node_id': node_id,
            'timestamp': datetime.now().isoformat(),
            'confidence': 1.0 if identified_user and not is_randomized else 0.5,
            'fingerprint': fingerprint
        }
        
        # Log results
        if identified_user:
            confidence_str = "HIGH" if result['confidence'] > 0.8 else "MEDIUM"
            print(f"✅ Identified user: {identified_user} (MAC: {mac}, Confidence: {confidence_str})")
            
            if is_randomized:
                print(f"⚠️ Note: {identified_user} is using randomized MAC - consider providing guidance")
        else:
            print(f"❓ Unknown device: {mac} at {node_id}")
            if is_randomized:
                print(f"🔄 Device appears to use MAC randomization")
        
        return result

# Helper function for integration
def create_smart_tracker() -> SmartMACTracker:
    """Create and initialize smart MAC tracker."""
    return SmartMACTracker()

if __name__ == "__main__":
    # Test the system
    tracker = SmartMACTracker()
    
    # Test user registration
    tracker.register_user("Glenn", "AA:BB:CC:DD:EE:FF")
    
    # Test device tracking
    result = tracker.track_device("AA:BB:CC:DD:EE:FF", -45, "node_001")
    print(f"Tracking result: {result}")
    
    # Test randomized MAC
    random_mac = "DA:0E:14:12:34:56"  # Apple randomized pattern
    result2 = tracker.track_device(random_mac, -50, "node_002")
    print(f"Randomized MAC result: {result2}") 