# 🧪 Oppdatert Testing Plan
## Kun Det Som Faktisk Mangler

**Firebase og apps fungerer allerede!** Denne planen fokuserer kun på det som gjenstår.

## ✅ **Allerede Ferdig (Fra Tidligere)**
- Firebase prosjekt "tunnel-tracking-system" ✅
- Cloud Functions API deployed og fungerer ✅  
- Admin dashboard web-versjon fungerer perfekt ✅
- Mobile app kjører på Chrome ✅
- Firebase Authentication og Firestore konfigurert ✅

---

## 📅 **I DAG - Kun Pi Setup (45 min)**

### **FASE 1: Raspberry Pi Forberedelse**

#### **Steg 1.1: Pi Basic Setup (20 min)**
```bash
# 1. Flash Pi OS (hvis ikke gjort)
# - Raspberry Pi Imager
# - Enable SSH, sett bruker/passord
# - WiFi konfigurasjon

# 2. Test SSH tilgang
ssh pi@[DIN_PI_IP]

# 3. Basic system setup
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git curl htop
sudo timedatectl set-timezone Europe/Oslo
```

#### **Steg 1.2: Scripts og Dependencies (25 min)**
```bash
# På Pi:
cd /home/pi

# Opprett working directory
mkdir tunnel-tracking
cd tunnel-tracking

# Kopier scripts fra utviklingsmaskin (velg en metode):

# Metode A: SCP
# Fra utviklingsmaskin: scp -r scripts/ pi@[PI_IP]:/home/pi/tunnel-tracking/

# Metode B: Git clone (hvis du har repository)
# git clone https://github.com/your-repo/tunnel-tracking.git .

# Metode C: Manual copy via USB/wget

# Install Python dependencies
cd scripts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verifiser installasjon
python3 -c "from rajant_api import RajantAPI; print('✅ rajant-api ready')"
python3 -c "import requests, yaml; print('✅ Basic packages ready')"
```

**✅ Success Criteria for I DAG:**
- [ ] Pi SSH tilgang fungerer
- [ ] Scripts kopiert til Pi
- [ ] Virtual environment opprettet  
- [ ] rajant-api og dependencies installert
- [ ] Pi klar for Rajant testing

---

## 📅 **I MORGEN - Live Rajant Testing (2-3 timer)**

### **FASE 2: Rajant Hardware Setup (60 min)**

#### **Steg 2.1: Physical Rajant Setup**
```bash
# 1. Koble strøm til alle 3 Rajant noder
# 2. Vent 5-10 minutter på oppstart
# 3. Find Rajant IP-adresser:

# Fra Pi eller laptop på samme nettverk:
nmap -sn 192.168.0.0/24    # Scan ditt nettverk
# eller: nmap -sn 10.0.0.0/24

# Test ping til nodene:
ping [RAJANT_NODE_1_IP]
ping [RAJANT_NODE_2_IP]  
ping [RAJANT_NODE_3_IP]
```

#### **Steg 2.2: Rajant Node Konfigurering**
```bash
# SSH til hver Rajant node:
ssh admin@[RAJANT_NODE_IP]
# Standard passord: "admin" (endre dette!)

# På hver node - aktiver API og client tracking:
configure
set management api enable
set management ssh enable
set wireless radio0 client-tracking enable
set wireless radio0 client-table enable

# (Valgfritt) Sett opp WiFi for mobile enheter:
set wireless radio0 ssid "TunnelNet"
set wireless radio0 security-mode open
set wireless radio0 enable

commit
save
exit

# Gjenta for alle 3 noder
```

### **FASE 3: API Integration Testing (30 min)**

#### **Steg 3.1: Test rajant-api Connectivity**
```bash
# På Pi:
cd /home/pi/tunnel-tracking/scripts
source venv/bin/activate

# Test single node først:
python3 test_rajant_api.py --host [RAJANT_NODE_1_IP] --username admin --password admin

# Hvis OK, test alle noder:
# Oppdater config.yaml med faktiske IP-er først
nano config.yaml

# Test alle noder:
python3 test_rajant_api.py --config config.yaml
```

**Forventet output hvis OK:**
```
🧪 Rajant API Test Suite
========================

📡 Test 1: Basic Connectivity ✅
🔐 Test 2: Authentication ✅  
📊 Test 3: Node Information ✅
📱 Test 4: Wireless Clients ✅

🎉 All tests completed successfully!
```

#### **Steg 3.2: Troubleshoot hvis Test Feiler**
```bash
# Vanlige problemer og løsninger:

# Problem 1: Connection refused
ping [RAJANT_IP]              # Test basic connectivity
telnet [RAJANT_IP] 22         # Test SSH port

# Problem 2: Authentication failed  
ssh admin@[RAJANT_IP]         # Test manual SSH login
# Sjekk default passord eller endre det

# Problem 3: No wireless clients
ssh admin@[RAJANT_IP]
show wireless radio0 status   # Sjekk at radio er enabled
show wireless clients         # Sjekk client table manually
```

### **FASE 4: Live System Testing (60 min)**

#### **Steg 4.1: Start Full Integration**
```bash
# På Pi:
cd /home/pi/tunnel-tracking/scripts
source venv/bin/activate

# Start live monitoring (dette er hovedtesten!)
python3 rajant_integration.py

# I separat terminal - følg logs:
tail -f rajant_integration.log
```

#### **Steg 4.2: Mobile Device Testing**
```bash
# 1. Koble telefon til Rajant WiFi "TunnelNet" (hvis konfigurert)
#    eller være på samme nettverk som Rajant nodene

# 2. Åpne mobile app på telefonen (fra tidligere testing)

# 3. Gå til første Rajant node og vent 2-3 minutter

# 4. Sjekk Pi logs for detection:
# Forventet: "📱 Mobile device XX:XX:XX:XX:XX:XX detected..."

# 5. Flytt telefon til neste node og vent
# Forventet: Position update i logs og dashboard
```

#### **Steg 4.3: Verifiser End-to-End**
```bash
# Sjekk data flow:

# 1. Pi logs viser mobile detection ✅
tail -f /home/pi/tunnel-tracking/scripts/rajant_integration.log

# 2. Firebase Console viser data ✅  
# Gå til: https://console.firebase.google.com/
# Project: tunnel-tracking-system → Firestore → positions collection

# 3. Admin dashboard viser live data ✅
# Åpne: https://tunnel-tracking-system.web.app
# Sjekk at worker posisjoner oppdateres live
```

**✅ Success Criteria for I MORGEN:**
- [ ] Alle 3 Rajant noder online og API tilgjengelig
- [ ] rajant-api kan koble til alle noder  
- [ ] Mobile enheter detekteres på Rajant noder
- [ ] Pi sender data til Firebase (existing system)
- [ ] Admin dashboard viser live posisjoner
- [ ] Movement detection fungerer mellan noder

---

## 🚨 **Hvis Problemer Oppstår**

### **Problem: rajant-api library ikke funnet**
```bash
# På Pi:
pip install rajant-api

# Hvis det feiler:
pip3 install rajant-api
# eller: python3 -m pip install rajant-api
```

### **Problem: Kan ikke nå Rajant noder**
```bash
# Sjekk nettverk:
ip route                    # Se Pi routing table  
ping [RAJANT_IP]           # Test basic connectivity
nmap -p 22 [RAJANT_IP]     # Test SSH port specifically

# Sjekk at Pi og Rajant er på samme nettverk
```

### **Problem: Wireless clients ikke detektert**
```bash
# SSH til Rajant node og sjekk manuelt:
ssh admin@[RAJANT_IP]
show wireless radio0 status
show wireless clients

# Aktiver client tracking hvis disabled:
configure
set wireless radio0 client-tracking enable
commit
```

### **Problem: Firebase connection issues**
```bash
# Test Firebase API fra Pi:
curl -X POST https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/log-position \
  -H "Content-Type: application/json" \
  -d '{"mac_address":"TEST:MAC","node_id":"pi_test"}'

# Sjekk internet connectivity:
ping 8.8.8.8
```

---

## 📱 **Quick Commands Reference**

### **I dag (Pi setup):**
```bash
ssh pi@[PI_IP]
cd /home/pi/tunnel-tracking/scripts
source venv/bin/activate
python3 -c "from rajant_api import RajantAPI; print('Ready!')"
```

### **I morgen (Testing):**
```bash
# Test Rajant connectivity:
python3 test_rajant_api.py --host [RAJANT_IP]

# Start live monitoring:
python3 rajant_integration.py

# Follow logs:
tail -f rajant_integration.log
```

### **Check existing Firebase:**
```bash
# Admin dashboard (already working):
https://tunnel-tracking-system.web.app

# Firebase console:
https://console.firebase.google.com/project/tunnel-tracking-system
```

---

## 🎯 **Sammendrag**

**I DAG:** Kun Pi setup (45 min)
**I MORGEN:** Rajant testing og live integration (2-3 timer)

**Firebase, admin dashboard og mobile app fungerer allerede!** 🎉

Vi trenger bare å:
1. Få Pi klar med scripts
2. Koble til Rajant noder  
3. Test live integration

**Mye lettere enn jeg først tenkte! 🚀** 