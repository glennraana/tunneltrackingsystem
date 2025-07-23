# 🍓 Raspberry Pi Installation Guide
## Tunnel Tracking System - Edge Server

Denne veiledningen viser hvordan du setter opp en Raspberry Pi som tunnel server for live MAC-adresse tracking.

## 🎯 **Arkitektur Oversikt**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Rajant Nodes  │────│  Raspberry Pi   │────│  Firebase Cloud │
│   (i tunnelen)  │    │  (Edge Server)  │    │   (Backend)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
   MAC Detection          Processing &              Admin Dashboard
   WiFi Associations      Data Filtering            & Mobile App
   Signal Strength        API Calls                 Live Updates
```

## 🛠️ **Hardware Anbefaling**

### **Anbefalt Setup:**
- **Raspberry Pi 4 (4GB RAM)** - optimal for 3-8 Rajant noder
- **SanDisk Ultra 32GB microSD** - høy hastighet for logging
- **Pi Case med vifte** - viktig for tunnelmiljø 
- **PoE HAT** (valgfritt) - strøm via ethernet
- **Ethernet kabel** - stabil nettverkstilkobling

### **Minimum Setup:**
- **Raspberry Pi 3B+** - fungerer for <3 noder
- **16GB microSD** - minimum lagring
- **Standard Pi strømadapter**

## 📦 **Steg 1: Raspberry Pi OS Setup**

### 1.1 Installer Raspberry Pi OS
```bash
# Last ned Raspberry Pi Imager
# https://www.raspberrypi.org/software/

# Flash Raspberry Pi OS Lite (64-bit) til SD-kort
# Aktiver SSH under avanserte innstillinger
# Sett bruker: pi
# Sett passord: ditt-sichere-passord
```

### 1.2 Første oppstart
```bash
# Koble Pi til nettverk via ethernet
# Boot Pi og logg inn

# Oppdater system
sudo apt update && sudo apt upgrade -y

# Sett timezone
sudo timedatectl set-timezone Europe/Oslo

# Sjekk systeminfo
cat /proc/device-tree/model
free -h
df -h
```

## 🔧 **Steg 2: Installer Tunnel Tracking**

### 2.1 Last ned scripts til Pi
```bash
# På Pi: Opprett arbeidsmappe
mkdir ~/tunnel-tracking
cd ~/tunnel-tracking

# Kopier filer fra utviklingsmaskin via SCP eller USB
# Alternativt: Last ned fra git repository
```

### 2.2 Kjør Pi-spesifikk installasjon
```bash
cd ~/tunnel-tracking/scripts
chmod +x pi_setup.sh
./pi_setup.sh
```

**Scriptet gjør automatisk:**
- ✅ Installerer Python og dependencies  
- ✅ Lager virtual environment
- ✅ Setter opp systemd service
- ✅ Optimaliserer for Pi ytelse
- ✅ Konfigurerer logging
- ✅ Aktiverer SSH for remote tilgang

### 2.3 Konfigurer for ditt tunnelprosjekt
```bash
# Rediger Pi-optimalisert config
sudo nano /opt/rajant-integration/config_pi.yaml

# Oppdater med dine Rajant node IP-er:
rajant:
  nodes:
    - ip: "DIN_RAJANT_NODE_1_IP"
      name: "Tunnel Inngang"
      location: {x: 50, y: 100}
    - ip: "DIN_RAJANT_NODE_2_IP"  
      name: "Tunnel Midt"
      location: {x: 200, y: 100}
    # ... legg til alle nodene
```

## 🚀 **Steg 3: Start Live Monitoring**

### 3.1 Aktivér og start tjenesten
```bash
# Aktivér auto-start ved boot
sudo systemctl enable rajant-integration

# Start tjenesten nå
sudo systemctl start rajant-integration

# Sjekk status
sudo systemctl status rajant-integration
```

### 3.2 Overvåk live logs
```bash
# Live logs
journalctl -u rajant-integration -f

# Pi ressursmonitor
/opt/rajant-integration/pi_monitor.sh
```

**Forventet output:**
```
🍓 Pi Resource Status:
=====================
Uptime: up 2 days, 14:32
CPU Temp: temp=45.7'C
CPU Usage: 15.2%
Memory: Used: 1.2G / 3.8G (31.6%)
Disk: Used: 8.5G / 29G (30%)

🔗 Rajant Service Status:
✅ Service Running

📊 Last 5 log entries:
2024-01-15 10:30:05 - INFO - 📍 MAC AA:BB:CC:DD:EE:FF detected at Tunnel Entrance
```

## 🔍 **Steg 4: Verifiser Integrasjon**

### 4.1 Test Rajant tilkobling
```bash
# Test ping til Rajant noder
ping 192.168.100.10
ping 192.168.100.11

# SSH til Rajant node (hvis mulig)
ssh admin@192.168.100.10
show clients  # Vis tilkoblede enheter
exit
```

### 4.2 Test Firebase API
```bash
# Test API call
curl -X POST \
  https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/api/log-position \
  -H "Content-Type: application/json" \
  -d '{"mac_address":"PI:TEST:MAC","node_id":"pi_test"}'
```

### 4.3 Sjekk Admin Dashboard
```bash
# På utviklingsmaskin: Start admin dashboard
cd admin_dashboard
flutter run -d chrome

# Sjekk "Noder" tab for Rajant noder
# Sjekk "Dashboard" for live data
```

## 🛡️ **Steg 5: Produksjon & Sikkerhet**

### 5.1 Sikkerhetskonfigurasjon
```bash
# Endre standard passord
passwd

# Sett opp SSH key-basert innlogging
ssh-keygen -t ed25519
# Kopier public key til ~/.ssh/authorized_keys

# Deaktiver passord-login (valgfritt)
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
sudo systemctl restart ssh
```

### 5.2 Fysisk plassering i tunnel
```
Plassering av Pi:
- 📍 Sentralt i tunnelen for best WiFi dekning til Rajant noder
- 🌡️ Unngå høy temperatur (>70°C CPU temp)
- 💧 Beskytt mot fuktighet (IP-rated case)
- 🔌 Stabil strømforsyning (UPS anbefales)
- 📶 Ethernet tilkobling til hovednettverk
```

### 5.3 Remote monitoring setup
```bash
# Sett opp cron job for status rapporter
crontab -e

# Legg til: Send status hver time
0 * * * * /opt/rajant-integration/pi_monitor.sh | mail -s "Pi Status" din@email.no
```

## 📊 **Performance Guidelines**

### **Pi 4 (4GB) Kapasitet:**
- ✅ **1-8 Rajant noder**: Optimal ytelse
- ✅ **Scan interval**: 30-60 sekunder
- ✅ **50+ samtidige MAC-er**: Ingen problem
- ✅ **24/7 drift**: Stabil med god kjøling

### **Pi 3B+ Kapasitet:**
- ⚠️ **1-3 Rajant noder**: Akseptabel ytelse  
- ⚠️ **Scan interval**: 60-120 sekunder
- ⚠️ **<20 samtidige MAC-er**: Anbefalt limit

### **Resource Optimization:**
```yaml
# I config_pi.yaml - juster for ditt Pi-oppsett
monitoring:
  scan_interval: 45          # Pi 4: 30-60s, Pi 3: 60-120s
  max_concurrent_nodes: 3    # Pi 4: 5-8, Pi 3: 2-3
  position_cache_time: 600   # Lengre cache på Pi
```

## 🚨 **Troubleshooting**

### **Problem: Høy CPU bruk**
```bash
# Sjekk prosesser
htop
# Øk scan_interval i config
# Reduser max_concurrent_nodes
```

### **Problem: Memory leakage**
```bash
# Restart service
sudo systemctl restart rajant-integration
# Sjekk memory limits i service config
```

### **Problem: Rajant tilkobling**
```bash
# Sjekk network
ip route
ping 192.168.100.10
# Verifiser Pi er på riktig VLAN/subnet
```

### **Problem: Firebase API timeout**
```bash
# Test internettilkobling
ping 8.8.8.8
# Øk timeout i config_pi.yaml
# Sjekk firewall rules
```

## 📞 **Remote Management**

### **SSH tilgang:**
```bash
# Fra hvor som helst:
ssh pi@DIN_PI_IP_ADRESSE

# Nyttige kommandoer:
sudo systemctl status rajant-integration  # Service status
/opt/rajant-integration/pi_monitor.sh     # Resource monitor
journalctl -u rajant-integration -f       # Live logs
sudo systemctl restart rajant-integration # Restart service
```

### **File transfer:**
```bash
# Kopier config fra utviklingsmaskin:
scp config_pi.yaml pi@PI_IP:/opt/rajant-integration/

# Last ned logs til analyse:
scp pi@PI_IP:/var/log/rajant-integration.log ./
```

---

## ✅ **Final Checklist**

Efter vellykket installasjon skal du ha:

- [x] **Pi kjører stabilt** i tunnelmiljø
- [x] **Rajant noder oppdaget** og registrert i Firebase
- [x] **Live MAC tracking** fungerer
- [x] **Admin dashboard** viser tunnel data
- [x] **Remote SSH tilgang** for vedlikehold
- [x] **Automatisk restart** ved feil
- [x] **Resource monitoring** aktivt

**Pi er nå din edge server for live tunnel tracking! 🍓🚇** 