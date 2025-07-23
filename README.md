# 🚇 Tunnel Tracking System

Tunnel worker tracking system using Rajant mesh network, Raspberry Pi, and Firebase.

## 📁 Repository Structure

```
tunneltrackingsystem/
├── scripts/                    # Pi integration scripts
│   ├── rajant_integration.py   # Main monitoring script
│   ├── test_rajant_api.py     # Rajant API testing
│   ├── config.yaml            # Configuration
│   ├── requirements.txt       # Python dependencies
│   └── quick_start.sh         # Quick setup script
├── mobile_app/                # Flutter mobile app
├── admin_dashboard/           # Flutter web dashboard  
├── cloud_functions/           # Firebase functions
├── docs/                      # Documentation
└── README.md                  # This file
```

## 🚀 Quick Start for Raspberry Pi

### 1. Clone Repository on Pi
```bash
git clone https://github.com/yourusername/tunneltrackingsystem.git
cd tunneltrackingsystem/scripts
```

### 2. Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Rajant Nodes
```bash
# Edit config.yaml with your Rajant node IP addresses
nano config.yaml

# Test connectivity
python3 test_rajant_api.py --config config.yaml
```

### 4. Start Monitoring
```bash
# Test run
python3 rajant_integration.py

# Or install as service
sudo bash quick_start.sh
```

## 🔧 Configuration

Update `scripts/config.yaml` with:
- Your Rajant node IP addresses
- Firebase project details
- Tunnel layout coordinates
- Security settings

## 📱 Apps

- **Mobile App**: Flutter app for workers
- **Admin Dashboard**: Web interface for monitoring
- **Firebase Backend**: Already deployed and working

## 🧪 Testing

1. **Pi Setup**: Run `quick_start.sh` 
2. **Rajant API**: Run `test_rajant_api.py`
3. **Live Integration**: Run `rajant_integration.py`
4. **End-to-End**: Test with mobile devices

## 📞 Support

- Check `docs/` for detailed documentation
- Firebase console: https://console.firebase.google.com/project/tunnel-tracking-system
- Admin dashboard: https://tunnel-tracking-system.web.app

---

**🎯 Next Steps:** Follow `docs/TESTING_ROADMAP_UPDATED.md` for step-by-step setup! 