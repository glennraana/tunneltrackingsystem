#!/bin/bash
# Quick Start Script for Tunnel Tracking System
# Raspberry Pi Setup

set -e

echo "🚀 Tunnel Tracking System - Raspberry Pi Setup"
echo "==============================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Don't run as root. Use regular user with sudo access."
   exit 1
fi

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
   echo "❌ Please run this from the scripts/ directory"
   echo "   cd tunneltrackingsystem/scripts"
   exit 1
fi

echo "📦 Installing system dependencies..."
sudo apt update -qq
sudo apt install -y python3-pip python3-venv python3-dev nmap curl

echo "🐍 Setting up Python virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
fi

echo "📋 Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🔍 Testing basic connectivity..."

# Test internet
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "✅ Internet connection OK"
else
    echo "❌ No internet connection"
    exit 1
fi

# Test Firebase API
echo "🔥 Testing Firebase API..."
API_URL="https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/health"
if curl -s --max-time 5 $API_URL | grep -q "OK"; then
    echo "✅ Firebase API is accessible"
else
    echo "⚠️  Firebase API not responding (this is OK for now)"
fi

# Check for Rajant nodes (optional)
echo "📡 Scanning for Rajant nodes..."
echo "   (This will scan common IP ranges)"

found_nodes=()
for ip in 192.168.{1,100,0}.{1..20}; do
    if ping -c 1 -W 1 $ip &> /dev/null; then
        if nmap -p 22 $ip 2>/dev/null | grep -q "open"; then
            found_nodes+=($ip)
        fi
    fi
done

if [[ ${#found_nodes[@]} -gt 0 ]]; then
    echo "✅ Found potential Rajant nodes:"
    for node in "${found_nodes[@]}"; do
        echo "   - $node"
    done
    echo "   Update config.yaml with these IP addresses"
else
    echo "⚠️  No Rajant nodes found (they might be on different network)"
fi

# Create log directory
mkdir -p logs

echo ""
echo "🎯 NEXT STEPS:"
echo "1. Edit config.yaml with your Rajant node IP addresses:"
echo "   nano config.yaml"
echo ""
echo "2. Test Rajant API connectivity:"
echo "   source venv/bin/activate"
echo "   python3 test_rajant_api.py --config config.yaml"
echo ""
echo "3. Start live monitoring:"
echo "   python3 rajant_integration.py"
echo ""
echo "✅ Raspberry Pi setup completed!"
echo "   For help: see README.md or docs/ directory" 