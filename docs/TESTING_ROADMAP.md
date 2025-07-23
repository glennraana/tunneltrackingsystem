# 🧪 Testing Roadmap - Tunnel Tracking System
## Steg-for-Steg Testing Plan

Dette er din komplette guide for å teste systemet - forberedelser i dag og live testing i morgen.

## 📅 **I DAG (Før Rajant Hardware)**

### **🎯 Mål:** Få alt klart så du kun trenger å koble til Rajant nodene i morgen

---

## **FASE 1: Firebase Backend Setup (30-45 min)**

### **Steg 1.1: Firebase Prosjekt**
```bash
# 1. Opprett Firebase prosjekt
Gå til: https://console.firebase.google.com/
- Klikk "Create a project"
- Navn: "tunnel-tracking-system"
- Aktiver Google Analytics (valgfritt)
- Region: europe-west1

# 2. Aktiver tjenester
Firebase Console → Authentication → Sign-in method → Enable "Anonymous"
Firebase Console → Firestore Database → Create database → Start in test mode
Firebase Console → Functions → Get started → Upgrade to Blaze plan

# 3. Installer Firebase CLI
brew install firebase-cli        # macOS
# eller: npm install -g firebase-tools

firebase login
```

### **Steg 1.2: Deploy Backend**
```bash
# I ditt prosjekt directory:
cd firebase_config

# Konfigurer Firebase
firebase init
# Velg: Functions, Firestore, Hosting
# Velg eksisterende prosjekt: tunnel-tracking-system

# Deploy Cloud Functions
firebase deploy --only functions

# Deploy admin dashboard hosting
cd ../admin_dashboard
flutter build web --release
cd ../firebase_config
firebase deploy --only hosting

# Test at alt fungerer
curl https://YOUR_PROJECT_ID.cloudfunctions.net/api/health
```

**✅ Success Criteria:**
- Cloud Functions API svarer med 200 OK
- Admin dashboard tilgjengelig på web
- Firebase projekt konfigurert

---

## **FASE 2: Raspberry Pi Setup (45-60 min)**

### **Steg 2.1: Pi OS Installation**
```bash
# Flash Raspberry Pi OS
1. Last ned Raspberry Pi Imager
2. Flash "Raspberry Pi OS Lite (64-bit)" til SD-kort
3. I imager under "Advanced options":
   - Enable SSH
   - Set username: pi
   - Set password: [ditt-passord]
   - Configure WiFi (ditt nettverk)
   - Set locale: Norway

# Boot Pi og test SSH tilgang
ssh pi@[PI_IP_ADDRESS]
```

### **Steg 2.2: Pi System Setup**
```bash
# På Pi via SSH:
# Oppdater system
sudo apt update && sudo apt upgrade -y

# Sett timezone
sudo timedatectl set-timezone Europe/Oslo

# Installer grunnleggende pakker
sudo apt install -y python3-pip python3-venv git curl htop vim

# Sjekk Pi status
cat /proc/device-tree/model
free -h
df -h
ip addr show
```

### **Steg 2.3: Kopier Scripts til Pi**
```bash
# Fra utviklingsmaskinen:
# Pakk alle scripts i en tar fil
tar -czf tunnel-tracking-scripts.tar.gz scripts/ docs/

# Kopier til Pi
scp tunnel-tracking-scripts.tar.gz pi@[PI_IP]:/home/pi/

# På Pi: Pakk ut
ssh pi@[PI_IP]
cd /home/pi
tar -xzf tunnel-tracking-scripts.tar.gz
```

### **Steg 2.4: Pi Dependencies Setup**
```bash
# På Pi: Installer Python dependencies
cd /home/pi/scripts

# Opprett virtual environment
python3 -m venv venv
source venv/bin/activate

# Installer packages
pip install -r requirements.txt

# Test at alt er installert
python3 -c "import requests, yaml, psutil; print('✅ Basic packages OK')"

# Test rajant-api (vil feile til i morgen, men sjekk at pakken er installert)
python3 -c "from rajant_api import RajantAPI; print('✅ rajant-api installed')"
```

**✅ Success Criteria:**
- Pi booter og SSH fungerer
- Python dependencies installert
- Scripts kopiert til Pi
- Virtual environment konfigurert

---

## **FASE 3: Admin Dashboard Test (30 min)**

### **Steg 3.1: Local Dashboard Test**
```bash
# På utviklingsmaskinen:
cd admin_dashboard

# Sjekk Flutter setup
flutter doctor

# Installer dependencies
flutter pub get

# Test på desktop
flutter run -d chrome
# eller flutter run -d macos

# Verifiser at dashboard starter og kobler til Firebase
```

### **Steg 3.2: Web Dashboard Test**
```bash
# Test deployed web dashboard
Åpne browser til: https://YOUR_PROJECT_ID.web.app

# Sjekk at:
- Dashboard laster
- Ingen console errors
- Kan navigere mellom tabs
- Firebase connection fungerer
```

**✅ Success Criteria:**
- Dashboard kjører lokalt
- Web deployment fungerer  
- Firebase integration OK

---

## **FASE 4: Mobile App Test (20 min)**

### **Steg 4.1: Mobile App Setup**
```bash
cd mobile_app

# Installer dependencies
flutter pub get

# Test på simulator/chrome
flutter run -d chrome

# Verifiser:
- App starter
- Anonymous login fungerer
- Kan sende test position data
```

**✅ Success Criteria:**
- Mobile app kjører
- Firebase connection fungerer
- Test data kan sendes

---

## **FASE 5: Test Scripts Forberedelse (15 min)**

### **Steg 5.1: Mock Test av Integration Script**
```bash
# På Pi: Test mock mode
cd /home/pi/scripts
source venv/bin/activate

# Test integration script i mock mode
python3 rajant_integration.py --discover-only

# Test MAC filtering
python3 mac_filtering.py

# Test Firebase API connection
curl -X POST [DIN_FIREBASE_URL]/api/log-position \
  -H "Content-Type: application/json" \
  -d '{"mac_address":"TEST:MAC","node_id":"test"}'
```

**✅ Success Criteria:**
- Integration script kjører uten errors (selv uten Rajant)
- MAC filtering fungerer
- Firebase API mottar test data

---

## **DAGENS SLUTTSJEKK**

**Alt skal være ✅ før du går hjem:**

- [ ] **Firebase**: Backend deployed og API fungerer
- [ ] **Admin Dashboard**: Web-versjon tilgjengelig og fungerer
- [ ] **Mobile App**: Kjører og kan sende data til Firebase
- [ ] **Raspberry Pi**: Setup med scripts og dependencies
- [ ] **Test Scripts**: Klargjort for Rajant testing
- [ ] **Network**: Pi på samme nettverk som Rajant nodene vil være

---

## 📅 **I MORGEN (Med Rajant Hardware)**

### **🎯 Mål:** Koble til Rajant noder og teste hele systemet live

---

## **FASE 6: Rajant Noder Setup (45-60 min)**

### **Steg 6.1: Physical Setup**
```bash
# 1. Strøm til alle 3 Rajant noder
# 2. Ethernet til første node (for initial setup)
# 3. Vent 5-10 min på oppstart

# Find Rajant IP-er
nmap -sn 192.168.100.0/24
# eller scan ditt nettverk range

# Test ping
ping 192.168.100.10
ping 192.168.100.11  
ping 192.168.100.12
```

### **Steg 6.2: Rajant Node Konfigurasjon**
```bash
# SSH til hver node og konfigurer
ssh admin@192.168.100.10

# På hver node:
configure
set management api enable
set management ssh enable
set management http enable

# Sett statiske IP-er
set interface ethernet0 ip 192.168.100.10/24  # Node 1
# set interface ethernet0 ip 192.168.100.11/24  # Node 2  
# set interface ethernet0 ip 192.168.100.12/24  # Node 3

# Aktiver client tracking
set wireless radio0 client-tracking enable
set wireless radio0 client-table enable

# WiFi SSID for mobile enheter
set wireless radio0 ssid "TunnelNet"
set wireless radio0 security-mode open
set wireless radio0 enable

commit
save
exit

# Repeat for alle 3 noder
```

### **Steg 6.3: Mesh Network Verifisering**
```bash
# Fra Pi: Test connectivity til alle noder
ssh pi@[PI_IP]

ping 192.168.100.10
ping 192.168.100.11
ping 192.168.100.12

# Test SSH til alle noder fra Pi
ssh admin@192.168.100.10 "show version"
ssh admin@192.168.100.11 "show version"  
ssh admin@192.168.100.12 "show version"
```

**✅ Success Criteria:**
- 3 Rajant noder online
- Mesh network etablert
- Pi kan nå alle noder
- Client tracking aktivert

---

## **FASE 7: Rajant API Testing (30 min)**

### **Steg 7.1: Test rajant-api Library**
```bash
# På Pi:
cd /home/pi/scripts
source venv/bin/activate

# Test single node
python3 test_rajant_api.py --host 192.168.100.10 --username admin --password admin

# Test alle noder
python3 test_rajant_api.py --config config.yaml
```

**Forventet Output:**
```
🧪 Rajant API Test Suite
========================

🔍 Testing Rajant Node: 192.168.100.10
==================================================

📡 Test 1: Basic Connectivity
   ✅ Connection established

🔐 Test 2: Authentication  
   ✅ Authenticated as user: admin

📊 Test 3: Node Information
   📋 Hostname: Tunnel-Node-01
   📋 Model: LX5
   ✅ Node information retrieved successfully

📱 Test 4: Wireless Clients
   ✅ Wireless client data retrieved successfully

🎉 All tests completed successfully!
```

### **Steg 7.2: Hvis Test Feiler - Troubleshooting**
```bash
# Problem 1: Connection timeout
ping 192.168.100.10
telnet 192.168.100.10 22

# Problem 2: Authentication failed
ssh admin@192.168.100.10
# Sjekk at du kan logge inn manuelt

# Problem 3: No wireless clients
ssh admin@192.168.100.10
show wireless clients
show wireless radio0 status
```

**✅ Success Criteria:**
- rajant-api kan koble til alle 3 noder
- Node information kan hentes
- Wireless client tracking fungerer

---

## **FASE 8: Live Mobile Device Testing (45 min)**

### **Steg 8.1: Mobile Device Setup**
```bash
# 1. Koble telefon til "TunnelNet" WiFi (Rajant)
# 2. Åpne mobile app på telefonen
# 3. Logger inn (anonymous)
# 4. Hold telefonen ved første Rajant node
```

### **Steg 8.2: Start Pi Integration**
```bash
# På Pi: Start live monitoring
cd /home/pi/scripts
source venv/bin/activate

# Start integration med alle noder
python3 rajant_integration.py

# Følg logs live
tail -f rajant_integration.log
```

**Forventet Output:**
```
2024-01-15 10:30:05 - INFO - ✅ Smart MAC filtering enabled
2024-01-15 10:30:05 - INFO - ✅ Rajant API library available
2024-01-15 10:30:06 - INFO - 🔍 Starting MAC address monitoring...
2024-01-15 10:30:15 - INFO - 📡 Retrieved 1 clients from Tunnel Entrance
2024-01-15 10:30:15 - INFO - 📱 Mobile device 3C:2E:FF:12:34:56 (Apple iPhone) detected at Tunnel Entrance (Signal: -45 dBm, Confidence: 0.95)
```

### **Steg 8.3: Test Movement Detection**
```bash
# Test scenario:
1. Start med telefon ved Node 1 (entrance)
2. Vent 2-3 minutter (se at Pi detekterer)
3. Gå til Node 2 (middle) 
4. Vent 2-3 minutter (se posisjon endrer seg)
5. Gå til Node 3 (exit)
6. Vent og verifiser

# Følg live i logs og admin dashboard
```

**✅ Success Criteria:**
- Pi detekterer mobiltelefon på Rajant noder
- MAC filtering fungerer (kun mobile enheter)
- Position updates sendes til Firebase
- Admin dashboard viser live posisjon

---

## **FASE 9: End-to-End Validation (30 min)**

### **Steg 9.1: Complete System Test**
```bash
# 1. Mobile app på telefon
# 2. Pi monitoring kjører
# 3. Admin dashboard åpen på PC
# 4. Test hele flyten:

Telefon på Rajant → Pi detekterer → Firebase lagrer → Dashboard viser
```

### **Steg 9.2: Verifiser Data Flow**
```bash
# Sjekk Firebase Console:
https://console.firebase.google.com/
- Firestore → positions collection → Se live data

# Sjekk admin dashboard:
- Live kart med worker posisjoner
- Statistics panel oppdateres
- Alerts hvis relevant

# Sjekk Pi logs:
tail -f /home/pi/scripts/rajant_integration.log
```

### **Steg 9.3: Test MAC Filtering**
```bash
# Koble til andre enheter på Rajant nettverk:
- Laptop/PC
- Printer/IoT device
- Tablet

# Verifiser at Pi logger:
📱 Mobile device XX:XX:XX:XX:XX:XX (Apple iPhone) detected...
🚫 Filtered out: YY:YY:YY:YY:YY:YY - Cisco Router/Switch

# Kun mobile enheter skal vises i dashboard
```

**✅ Success Criteria:**
- Hele systemet fungerer end-to-end
- Live posisjon tracking fungerer
- MAC filtering virker korrekt
- Admin dashboard viser riktige data
- <60 sekunder latency fra bevegelse til dashboard

---

## **🎯 FINALE: System Ready Checklist**

**Når alle disse er ✅ er systemet produksjonsklar:**

### **Backend:**
- [ ] Firebase Cloud Functions API svarer
- [ ] Firestore database mottar data
- [ ] Admin dashboard tilgjengelig på web

### **Raspberry Pi:**
- [ ] Pi kjører stabilt med integration script
- [ ] Kan koble til alle 3 Rajant noder
- [ ] MAC filtering fungerer korrekt
- [ ] Sender data til Firebase

### **Rajant Network:**
- [ ] 3 noder online og mesh etablert
- [ ] Client tracking aktivert
- [ ] WiFi tilgjengelig for mobile enheter
- [ ] rajant-api connectivity fungerer

### **Mobile & Dashboard:**
- [ ] Mobile app kobler til Rajant WiFi
- [ ] Live position tracking fungerer
- [ ] Admin dashboard viser real-time data
- [ ] Movement detection fungerer

### **Performance:**
- [ ] <60 sekunder latency for position updates
- [ ] >90% MAC filtering efficiency
- [ ] Stabil drift over flere timer

---

## **📱 Quick Commands Reference**

### **For i dag:**
```bash
# Firebase deploy
firebase deploy --only functions,hosting

# Pi setup
ssh pi@[PI_IP]
cd /home/pi/scripts && source venv/bin/activate

# Test admin dashboard
flutter run -d chrome
```

### **For i morgen:**
```bash
# Test Rajant connectivity
python3 test_rajant_api.py --host 192.168.100.10

# Start live monitoring
python3 rajant_integration.py

# Follow logs
tail -f rajant_integration.log
```

---

## 🚀 **Ready for Tomorrow!**

**Du har nå en komplett plan for testing. Lykke til! 🎯**

**Hint:** Start tidlig i morgen - first Rajant node connection kan ta litt tid å få riktig konfigurert. Men når den første fungerer, vil de andre gå raskt! 📡✨ 