# 🚀 Neste Steg - Tunnel Tracking System
## Fra Utvikling til Produksjon

Dette dokumentet lister prioriterte neste steg for å få systemet i live drift.

## 📋 **Steg 1: End-to-End Testing (ANBEFALT FØRST)**

### **1.1 Firebase Deployment Test**
```bash
# Tid: 2-3 timer
# Mål: Verifiser backend fungerer i produksjon

cd firebase_config

# Deploy Cloud Functions
firebase deploy --only functions

# Deploy hosting for admin dashboard  
cd ../admin_dashboard
flutter build web --release
cd ../firebase_config
firebase deploy --only hosting

# Test API endpoints
curl https://YOUR_PROJECT.cloudfunctions.net/api/health
```

**✅ Success Criteria:**
- Cloud Functions API svarer
- Admin dashboard tilgjengelig på web
- Firebase Firestore mottar data

### **1.2 Local Integration Test**
```bash
# Tid: 3-4 timer
# Mål: Test hele systemet lokalt før Pi deployment

# Start mock Rajant simulation
cd scripts
python3 rajant_integration.py --test-mode

# Åpne admin dashboard i browser
http://localhost:5000  # eller Firebase hosting URL

# Verifiser mobile app kobler til backend
cd mobile_app
flutter run -d chrome
```

**✅ Success Criteria:**
- Mock data flyter til dashboard
- Real-time oppdateringer fungerer
- MAC filtering virker som forventet

### **1.3 Raspberry Pi Setup Test**
```bash
# Tid: 4-6 timer
# Mål: Installer og test Pi uten ekte Rajant noder

# Sett opp Pi med scripts
ssh pi@DIN_PI_IP
cd ~/tunnel-tracking
chmod +x scripts/pi_setup.sh
./scripts/pi_setup.sh

# Test Pi med mock data
sudo systemctl start rajant-integration
journalctl -u rajant-integration -f

# Verifiser Pi sender data til Firebase
curl -X POST https://YOUR_PROJECT.cloudfunctions.net/api/log-position \
  -H "Content-Type: application/json" \
  -d '{"mac_address":"PI:TEST:MAC","node_id":"pi_test"}'
```

**✅ Success Criteria:**
- Pi script kjører stabilt
- Data sendes til Firebase fra Pi
- Admin dashboard viser Pi-genererte data

## 📋 **Steg 2: Fysisk Pilot (Etter Testing)**

### **2.1 Rajant Hardware Setup**
```bash
# Tid: 1-2 dager
# Mål: Konfigurer ekte Rajant mesh

# Rajant Node 1 (Entrance)
ssh admin@192.168.100.10
configure
set management http enable
set wireless radio0 client-tracking enable
set interface ethernet0 ip 192.168.100.10/24
commit
save

# Repeat for Node 2 og 3...
# Test mesh connectivity mellom noder
```

### **2.2 Pi Deployment i Tunnel**
```bash
# Tid: 2-3 timer
# Mål: Installer Pi på tunnellokasjon

# Physical setup:
├── Mount Pi i sikker case
├── Ethernet tilkobling til nettverk
├── Strømforsyning (UPS anbefalt)
└── Test WiFi reach til alle Rajant noder

# Network setup:
├── Verifiser Pi kan nå alle Rajant IPs
├── Test internettilkobling for Firebase
└── Configure firewall/VPN hvis nødvendig
```

### **2.3 Live Testing med Mobile Enheter**
```bash
# Tid: 3-4 timer
# Mål: Test med ekte telefoner i tunnel

# Test scenario:
1. Worker starter mobile app ved inngang
2. Går gjennom tunnel (entrance → middle → exit)
3. Verifiser position updates i admin dashboard
4. Test alerts for uautoriserte enheter
5. Validér MAC filtering (infrastruktur filtreres ut)
```

**✅ Success Criteria:**
- Live position tracking fungerer
- <60 sekunder latency for position updates
- >90% filtering efficiency for non-mobile devices
- Dashboard viser riktige worker posisjoner

## 📋 **Steg 3: Production Security**

### **3.1 Firebase Security Rules**
```javascript
// Firestore security rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Admin only access
    match /admin/{document=**} {
      allow read, write: if request.auth != null && 
        request.auth.token.admin == true;
    }
    
    // Position data - write from Pi, read from admin
    match /positions/{document} {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == "pi-service-account";
    }
    
    // Users collection
    match /users/{userId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == userId;
    }
  }
}
```

### **3.2 Pi Security Hardening**
```bash
# SSH key-only access
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
# PermitRootLogin no

# Firewall config
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow from 192.168.100.0/24  # Rajant network only

# Service account for Firebase
# Generate service account key fra Firebase Console
# Store securely på Pi: /opt/rajant-integration/.credentials/
```

### **3.3 Environment Configuration**
```yaml
# Production config (/opt/rajant-integration/config_prod.yaml)
firebase:
  api_url: "https://PRODUCTION_PROJECT.cloudfunctions.net/api"
  service_account_key: "/opt/rajant-integration/.credentials/service-account.json"
  
rajant:
  network_range: "192.168.100.0/24"
  nodes:
    - ip: "192.168.100.10"
      name: "Tunnel Entrance"
      location: {x: 50, y: 100}
      zone: "entrance"
    - ip: "192.168.100.11"  
      name: "Tunnel Section A"
      location: {x: 200, y: 100}
      zone: "middle"
    - ip: "192.168.100.12"
      name: "Tunnel Exit"
      location: {x: 350, y: 100}
      zone: "exit"

security:
  enable_mac_blocking: true
  auto_block_threshold: 3
  alert_on_unregistered: true
  
logging:
  log_level: "INFO"
  enable_file_logging: true
  log_file: "/var/log/rajant-integration.log"
  max_log_size: "100MB"
```

## 📋 **Steg 4: Monitoring & Alerting**

### **4.1 System Health Monitoring**
```bash
# Lag health check script
cat > /opt/rajant-integration/health_check.sh << 'EOF'
#!/bin/bash
# Health check for tunnel tracking system

echo "🔍 System Health Check - $(date)"
echo "=================================="

# Pi system health
echo "Pi Temperature: $(vcgencmd measure_temp)"
echo "Pi Memory: $(free -h | awk '/^Mem:/ {print $3"/"$2}')"
echo "Pi Disk: $(df -h / | awk '/\// {print $5}' | tail -1)"

# Service status
systemctl is-active rajant-integration --quiet && echo "✅ Service: Running" || echo "❌ Service: Stopped"

# Network connectivity
ping -c 1 192.168.100.10 &>/dev/null && echo "✅ Rajant connectivity" || echo "❌ Rajant unreachable"
ping -c 1 8.8.8.8 &>/dev/null && echo "✅ Internet connectivity" || echo "❌ No internet"

# Firebase API test
response=$(curl -s -o /dev/null -w "%{http_code}" https://YOUR_PROJECT.cloudfunctions.net/api/health)
if [ "$response" = "200" ]; then
    echo "✅ Firebase API: OK"
else
    echo "❌ Firebase API: Error ($response)"
fi

echo ""
EOF

chmod +x /opt/rajant-integration/health_check.sh

# Schedule health checks
crontab -e
# */15 * * * * /opt/rajant-integration/health_check.sh >> /var/log/health_check.log
```

### **4.2 Alert System**
```bash
# Email alerts for critical issues
cat > /opt/rajant-integration/alert_handler.py << 'EOF'
#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
import subprocess
import json

def send_alert(subject, message):
    # Configure SMTP settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email = "tunnel-alerts@yourcompany.com"
    password = "your-app-password"
    
    msg = MIMEText(message)
    msg['Subject'] = f"🚨 Tunnel Alert: {subject}"
    msg['From'] = email
    msg['To'] = "admin@yourcompany.com"
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email, password)
        server.send_message(msg)

# Check for critical issues
def check_system():
    issues = []
    
    # Check service status
    result = subprocess.run(['systemctl', 'is-active', 'rajant-integration'], 
                          capture_output=True, text=True)
    if result.stdout.strip() != 'active':
        issues.append("Rajant integration service is down")
    
    # Check disk space
    result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
    usage = result.stdout.split('\n')[1].split()[4].rstrip('%')
    if int(usage) > 90:
        issues.append(f"Disk usage critical: {usage}%")
    
    return issues

if __name__ == "__main__":
    issues = check_system()
    if issues:
        alert_message = "\n".join(issues)
        send_alert("System Issues Detected", alert_message)
EOF

chmod +x /opt/rajant-integration/alert_handler.py

# Schedule alert checks
# */5 * * * * /opt/rajant-integration/alert_handler.py
```

## 📋 **Steg 5: User Training & Documentation**

### **5.1 Admin Training**
```bash
# Opprett admin veiledning
- Hvordan tolke dashboard data
- Håndtere alerts og varsler
- Troubleshooting vanlige problemer
- Legge til/fjerne autoriserte brukere
- System maintenance rutiner
```

### **5.2 Worker Training**  
```bash
# Opprett worker veiledning
- Installere mobile app
- Logge inn og bruke app
- Personvern og data sikkerhet
- Rapportere tekniske problemer
```

## 📅 **Tidsplan Sammendrag**

| Fase | Oppgaver | Estimert Tid | Prioritet |
|------|----------|--------------|-----------|
| **Testing** | End-to-end validering | 2-3 dager | 🔴 Kritisk |
| **Pilot** | Fysisk installation | 3-5 dager | 🟡 Høy |
| **Security** | Production hardening | 2-3 dager | 🟡 Høy |  
| **Monitoring** | Health & alerts | 1-2 dager | 🟢 Medium |
| **Training** | User documentation | 1-2 dager | 🟢 Medium |

**Total: 9-15 dager til full production deployment**

## ✅ **Success Metrics**

Systemet er produksjonsklar når:

- [ ] **Uptime**: >99% availability
- [ ] **Latency**: <60s position updates
- [ ] **Accuracy**: >95% mobile device detection
- [ ] **Filtering**: >90% infrastructure filtering
- [ ] **Security**: All prod security measures aktive
- [ ] **Monitoring**: Health checks og alerts fungerer
- [ ] **Training**: Admin og workers er opplært

---

## ⚠️ **VIKTIG OPPDATERING: Rajant API**

**Før du starter testing - installer rajant-api biblioteket:**

```bash
# Installer rajant-api Python library (kreves for Rajant integration)
pip install rajant-api

# Test Rajant connectivity før du fortsetter:
cd scripts
python3 test_rajant_api.py --host 192.168.100.10 --username admin --password admin
```

**Rajant noder har IKKE HTTP REST API som opprinnelig antatt - vi bruker rajant-api Python biblioteket i stedet.**

## 🎯 **Anbefalt Neste Handling**

**Steg 0: Verifiser Rajant API Connectivity (NYTT)**

```bash
# Test at du kan koble til Rajant noder:
cd scripts
python3 test_rajant_api.py --host DIN_RAJANT_NODE_IP

# Hvis det fungerer, fortsett med:
```

**Steg 1: Firebase Deployment Test**

Dette gir deg rask validering av at backend fungerer før du investerer tid i fysisk setup.

```bash
# Neste kommando å kjøre:
cd firebase_config
firebase deploy --only functions
```

**Hvor mye av dette vil du angripe først?** 🚀 