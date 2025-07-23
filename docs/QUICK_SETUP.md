# 🚀 Quick Setup Guide

**For Raspberry Pi - Get Running in 10 Minutes!**

## ✅ Prerequisites

- Raspberry Pi with internet connection
- SSH access or direct terminal access
- GitHub access from Pi

## 📋 Step-by-Step Setup

### 1. Clone Repository on Pi
```bash
# SSH to your Pi or use direct terminal
cd /home/pi

# Clone the repository
git clone https://github.com/yourusername/tunneltrackingsystem.git
cd tunneltrackingsystem/scripts
```

### 2. Run Quick Setup
```bash
# Make script executable
chmod +x quick_start.sh

# Run setup (this installs everything)
./quick_start.sh
```

**Expected output:**
```
🚀 Tunnel Tracking System - Raspberry Pi Setup
===============================================
📦 Installing system dependencies...
🐍 Setting up Python virtual environment...
📋 Installing Python packages...
🔍 Testing basic connectivity...
✅ Internet connection OK
✅ Firebase API is accessible
📡 Scanning for Rajant nodes...
✅ Raspberry Pi setup completed!
```

### 3. Configure Rajant Nodes
```bash
# Edit config file with your actual Rajant IP addresses
nano config.yaml

# Find the rajant.nodes section and update:
rajant:
  nodes:
    - ip: "192.168.1.100"    # YOUR ACTUAL IP
      name: "Node 1"
    - ip: "192.168.1.101"    # YOUR ACTUAL IP  
      name: "Node 2"
    - ip: "192.168.1.102"    # YOUR ACTUAL IP
      name: "Node 3"
```

### 4. Test Rajant Connectivity
```bash
# Activate Python environment
source venv/bin/activate

# Test single node
python3 test_rajant_api.py --host 192.168.1.100

# Test all nodes from config
python3 test_rajant_api.py --config config.yaml
```

### 5. Start Live Monitoring
```bash
# Still in venv
python3 rajant_integration.py

# You should see:
# 🚀 Starting Rajant Integration...
# 📡 Discovered X Rajant nodes
# 🔍 Monitoring for mobile devices...
```

## 🧪 Testing with Mobile Device

1. **Connect phone** to Rajant WiFi or same network
2. **Walk near Rajant nodes** (within WiFi range)
3. **Check Pi logs** for device detection
4. **Open admin dashboard**: https://tunnel-tracking-system.web.app
5. **Verify live position updates**

## 🚨 Common Issues

### Issue: "rajant-api not found"
```bash
source venv/bin/activate
pip install rajant-api
```

### Issue: "Can't reach Rajant nodes"
```bash
# Scan your network for devices
nmap -sn 192.168.1.0/24

# Test specific IP
ping 192.168.1.100
telnet 192.168.1.100 22
```

### Issue: "Firebase API not responding"
```bash
# Test internet
ping 8.8.8.8

# Test API directly
curl https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/health
```

## 📱 Access Points

- **Admin Dashboard**: https://tunnel-tracking-system.web.app
- **Firebase Console**: https://console.firebase.google.com/project/tunnel-tracking-system
- **Pi Logs**: `tail -f rajant_integration.log`

## ✅ Success Criteria

You should see:
- [ ] Pi connects to internet ✅
- [ ] Python environment created ✅
- [ ] Rajant nodes accessible ✅
- [ ] Mobile devices detected ✅
- [ ] Data appears in admin dashboard ✅

---

**🎯 Total setup time: ~10 minutes**  
**🔧 Troubleshooting: See docs/TROUBLESHOOTING.md** 