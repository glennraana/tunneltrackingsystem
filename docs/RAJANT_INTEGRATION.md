# 🔗 Rajant Mesh Integration Guide

Dette dokumentet beskriver hvordan du integrerer Rajant mesh-noder med Tunnel Tracking System for live MAC-adresse sporing.

## 📋 **Forutsetninger**

### Hardware
- **Rajant Noder**: LX5, ES1, eller ME4 modeller anbefales
- **Nettverksinfrastruktur**: Tilgang til Rajant InstaMesh nettverk
- **Server**: Linux/Windows maskin for integrasjons-script
- **Strømforsyning**: PoE+ eller 24V DC for nodene

### Software
- Python 3.8+
- Nettverkstilgang til Rajant nodes
- Firebase prosjekt med Cloud Functions

## 🗺️ **Steg 1: Planlegg Node Plassering**

### Tunnel Layout Mapping
```
Inngang     Seksjon A    Seksjon B    Utgang
   📡----------📡----------📡----------📡
  Node1      Node2       Node3      Node4
(x:50,y:100)(x:200,y:100)(x:350,y:100)(x:500,y:100)
```

### Plassering Guidelines
- **Avstand**: Maks 150m mellom noder for optimal dekning
- **Høyde**: 3-4m over bakken for beste signal
- **Hindringer**: Unngå tykke betongvegger og metallkonstruksjoner
- **Redundans**: Overlappende dekning i kritiske områder

## 🔧 **Steg 2: Konfigurer Rajant Noder**

### 2.1 Initial Node Setup

**Koble til node via ethernet:**
```bash
# Standard Rajant IP range
ssh admin@192.168.100.10

# Default credentials (endres etter første login)
# Username: admin
# Password: admin
```

### 2.2 Grunnleggende Konfigurasjon

**Via Rajant web interface:**
```
1. Åpne http://192.168.100.10 i browser
2. Login med admin/admin
3. Gå til System → Basic Settings
4. Sett:
   - Node Name: "Tunnel-Entrance"
   - Location: GPS koordinater eller tunnelposisjon
   - Time Zone: Europe/Oslo
```

### 2.3 Mesh Network Settings

**Konfigurer InstaMesh:**
```
Network → InstaMesh:
- Network Name: "TunnelMesh"
- Channel: Auto (anbefalt)
- Power: 20 dBm (juster etter behov)
- SSID: "TunnelWorker" (for arbeider-devices)
```

### 2.4 Enable Client Association Logging

**Aktiver MAC logging:**
```
Administration → Logging → System Log:
☑ Log client associations
☑ Log signal strength changes
☑ Log roaming events

Level: Informational
Remote Log Server: 192.168.100.100 (integrasjons-server)
Port: 514
```

### 2.5 API Access Setup

**Enable SSH og API:**
```bash
# Via SSH til node
configure
set management-interface ssh enable
set management-interface http enable  
set management-interface https enable
set api enable
commit
```

## 🖥️ **Steg 3: Installer Integration Software**

### 3.1 Setup Server

**På integrerings-server (Linux/Windows):**
```bash
# Opprett prosjektmappe
mkdir rajant-integration
cd rajant-integration

# Installer Python dependencies
pip install -r requirements.txt

# Kopier integration script
cp ../scripts/rajant_integration.py .
```

### 3.2 Konfigurer Network Discovery

**Rediger `rajant_integration.py` konfigurasjon:**
```python
CONFIG = {
    'firebase_api_url': 'https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/api',
    'rajant_network': '192.168.100.0/24',  # Ditt Rajant nettverk
    'scan_interval': 30,  # Sekunder mellom scans
    'node_discovery_timeout': 5,
    'debug': True,
    
    # Legg til faktiske node IP-er
    'known_nodes': [
        {
            'ip': '192.168.100.10',
            'name': 'Tunnel Entrance',
            'location': {'x': 50, 'y': 100}
        },
        {
            'ip': '192.168.100.11', 
            'name': 'Section A1',
            'location': {'x': 200, 'y': 100}
        },
        {
            'ip': '192.168.100.12',
            'name': 'Section B1', 
            'location': {'x': 350, 'y': 100}
        },
        {
            'ip': '192.168.100.13',
            'name': 'Tunnel Exit',
            'location': {'x': 500, 'y': 100}
        }
    ]
}
```

## 🚀 **Steg 4: Start Integration**

### 4.1 Test Node Discovery

```bash
# Discover og registrer noder
python rajant_integration.py --discover-only
```

**Forventet output:**
```
2024-01-15 10:30:00 - INFO - 🚀 Starting Rajant Integration...
2024-01-15 10:30:01 - INFO - 🔍 Discovering Rajant nodes...
2024-01-15 10:30:02 - INFO - 📡 Found Rajant node: Tunnel Entrance (192.168.100.10)
2024-01-15 10:30:03 - INFO - ✅ Node Tunnel Entrance registered successfully
2024-01-15 10:30:04 - INFO - 📡 Found Rajant node: Section A1 (192.168.100.11)
2024-01-15 10:30:05 - INFO - ✅ Node Section A1 registered successfully
```

### 4.2 Start MAC Monitoring

```bash
# Start kontinuerlig MAC monitoring
python rajant_integration.py --monitor-only
```

### 4.3 Full Integration

```bash
# Kjør både discovery og monitoring
python rajant_integration.py
```

## 📊 **Steg 5: Verifiser Integration**

### 5.1 Sjekk Admin Dashboard

1. Åpne admin dashboard: `flutter run -d chrome` i `admin_dashboard/`
2. Gå til **"Noder"** tab
3. Verifiser at Rajant noder vises som aktive
4. Sjekk **"Dashboard"** for live statistikk

### 5.2 Test MAC Detection

**Med en mobil enhet:**
```bash
# Koble mobil til "TunnelWorker" WiFi
# Beveg deg mellom forskjellige noder
# Sjekk live tracking i dashboard
```

## 🔄 **Steg 6: Production Setup**

### 6.1 Lag Service for Auto-start

**Linux systemd service:**
```bash
# Opprett /etc/systemd/system/rajant-integration.service
[Unit]
Description=Rajant Tunnel Integration
After=network.target

[Service]
Type=simple
User=rajant
WorkingDirectory=/opt/rajant-integration
ExecStart=/usr/bin/python3 rajant_integration.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl enable rajant-integration
sudo systemctl start rajant-integration
sudo systemctl status rajant-integration
```

### 6.2 Logging og Monitoring

**Sett opp log rotation:**
```bash
# /etc/logrotate.d/rajant-integration
/var/log/rajant-integration.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload rajant-integration
    endscript
}
```

## 🔧 **Advanced: Rajant API Integration**

For **ekte** Rajant API integrasjon (erstatt simulerte data):

### 6.3 Rajant API Credentials

```python
# Legg til i CONFIG
'rajant_auth': {
    'username': 'api_user',
    'password': 'your_api_password',
    'api_version': 'v1'
}
```

### 6.4 Real API Implementation

**Erstatt `_get_associated_devices()` metode:**
```python
async def _get_associated_devices(self, node: Dict) -> List[Dict]:
    """Get real device associations from Rajant API."""
    try:
        # Rajant API endpoint for associated clients
        api_url = f"http://{node['ip_address']}/api/v1/clients"
        
        auth = (CONFIG['rajant_auth']['username'], 
                CONFIG['rajant_auth']['password'])
        
        response = requests.get(api_url, auth=auth, timeout=5)
        
        if response.status_code == 200:
            clients_data = response.json()
            
            # Parse Rajant client data
            associated_devices = []
            for client in clients_data.get('clients', []):
                device_info = {
                    'mac_address': client['mac_address'],
                    'signal_strength': client['rssi'],
                    'association_time': client['connect_time'],
                    'device_type': client.get('device_type', 'unknown'),
                    'tx_rate': client.get('tx_rate'),
                    'rx_rate': client.get('rx_rate')
                }
                associated_devices.append(device_info)
            
            return associated_devices
        
    except Exception as e:
        logger.error(f"Error getting real device data: {e}")
        return []
```

## 📈 **Performance Tuning**

### Node Optimization
- **Scan Interval**: Juster basert på bevegelseshastighet (10-60 sekunder)
- **Signal Threshold**: Sett minimum signal styrke (-80 dBm typisk)
- **Duplicate Filtering**: Unngå spam fra samme MAC

### Network Optimization
```python
# Optimalisert CONFIG for produksjon
CONFIG = {
    'scan_interval': 15,  # Raskere for aktive tunneler
    'signal_threshold': -75,  # Ignorer svake signaler
    'position_cache_time': 300,  # 5 min cache
    'max_concurrent_nodes': 10,
    'api_timeout': 5,
    'retry_attempts': 3
}
```

## 🚨 **Troubleshooting**

### Vanlige Problemer

**Problem**: Noder ikke oppdaget
```bash
# Sjekk nettverkstilkobling
ping 192.168.100.10

# Sjekk Rajant node status
ssh admin@192.168.100.10
show system status
```

**Problem**: MAC addresses ikke logget
```bash
# Sjekk client associations på node
ssh admin@192.168.100.10
show clients

# Verifiser syslog konfiguration
show configuration management syslog
```

**Problem**: Firebase API feil
```bash
# Test API manuelt
curl -X POST \
  https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/api/log-position \
  -H "Content-Type: application/json" \
  -d '{"mac_address":"TEST:MAC","node_id":"test_node"}'
```

## 🔐 **Security Considerations**

### Network Security
- Bruk WPA3 på worker WiFi
- Isoler management network
- Implement VPN for remote access

### API Security  
- Roter API credentials regelmessig
- Begrens API access til specific IP ranges
- Monitor for suspiciøs API calls

## 📞 **Support**

For teknisk support:
- **Rajant Support**: support@rajant.com
- **System Issues**: Sjekk logs i `/var/log/rajant-integration.log`
- **Firebase Debugging**: Firebase Console > Functions > Logs

---

**✅ Etter vellykket setup vil du ha:**
- Live MAC-adresse tracking i tunnelen
- Automatisk posisjonering basert på node-association  
- Real-time dashboard med bruker-bevegelser
- Sikkerhetsvarsler for uregistrerte enheter
- Historisk data for rapporter 