#!/bin/bash
# Raspberry Pi Setup for Tunnel Tracking - Rajant Integration
# Optimert for Pi 4 (4GB RAM)

set -e

echo "🍓 Raspberry Pi - Tunnel Tracking Setup"
echo "======================================="

# System info
echo "📊 System informasjon:"
echo "Pi Model: $(cat /proc/device-tree/model)"
echo "OS: $(lsb_release -d | cut -f2)"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Disk: $(df -h / | awk '/\// {print $4}' | tail -1) ledig"
echo ""

# Update system
echo "🔄 Oppdaterer system..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installerer nødvendige pakker..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    curl \
    htop \
    iotop \
    net-tools \
    iputils-ping \
    vim \
    systemd \
    rsyslog \
    logrotate

# Install Python packages optimized for Pi
echo "🐍 Installerer Python dependencies for Pi..."
pip3 install --user \
    requests>=2.28.0 \
    asyncio \
    pyyaml>=6.0 \
    python-dotenv>=1.0.0 \
    psutil>=5.9.0

# Skip heavy packages on Pi (optional for basic functionality)
echo "⚠️  Hopper over tunge pakker (paramiko, scapy) for bedre ytelse"
echo "   Installer disse senere hvis SSH/advanced network scanning trengs"

# Create installation directory
INSTALL_DIR="/opt/rajant-integration"
echo "📁 Oppretter $INSTALL_DIR"
sudo mkdir -p $INSTALL_DIR
sudo chown pi:pi $INSTALL_DIR

# Create Python virtual environment for better isolation
echo "🔧 Setter opp Python virtual environment..."
python3 -m venv $INSTALL_DIR/venv
source $INSTALL_DIR/venv/bin/activate
pip install requests pyyaml python-dotenv psutil

# Copy files
echo "📋 Kopierer filer..."
cp rajant_integration.py $INSTALL_DIR/
cp config.yaml $INSTALL_DIR/
cp requirements.txt $INSTALL_DIR/

# Create Pi-optimized config
echo "⚙️ Lager Pi-optimalisert konfigurasjon..."
cat > $INSTALL_DIR/config_pi.yaml << 'EOF'
# Pi-optimalisert konfigurasjon for Tunnel Tracking

firebase:
  api_url: "https://us-central1-tunnel-tracking-system.cloudfunctions.net/api/api"
  timeout: 15  # Økt timeout for Pi
  retry_attempts: 3

rajant:
  network_range: "192.168.100.0/24"
  default_username: "admin"
  default_password: "admin"  # ENDRE DETTE!
  api_timeout: 10  # Økt timeout for Pi
  
  # Start med disse - legg til dine faktiske IP-er
  nodes:
    - ip: "192.168.100.10"
      name: "Tunnel Entrance"
      location: 
        x: 50
        y: 100
      zone: "entrance"

monitoring:
  scan_interval: 45           # Lengre intervall for Pi (sparer CPU)
  signal_threshold: -75       # Strengere filter
  position_cache_time: 600    # Lengre cache (10 min)
  max_concurrent_nodes: 3     # Færre samtidige for Pi
  log_level: "INFO"
  
  # Pi-optimalisert filtering
  exclude_macs:
    - "00:00:00:00:00:00"
    - "FF:FF:FF:FF:FF:FF"
    - "B8:27:EB:*"            # Raspberry Pi Foundation MACs
  
  exclude_vendors:
    - "Rajant"
    - "Raspberry Pi"

tunnel:
  name: "Pi Tunnel Monitoring"
  coordinate_system: "local"

security:
  enable_mac_blocking: true
  auto_block_threshold: 3     # Lavere threshold på Pi
  alert_on_unregistered: true

logging:
  enable_file_logging: true
  log_file: "/var/log/rajant-integration.log"
  enable_syslog: false        # Spar ressurser på Pi
  max_log_size: "50MB"        # Mindre logs på Pi
  backup_count: 5

development:
  enable_simulation: false
  test_mode: false
  verbose_logging: false      # Spar CPU på Pi
EOF

# Create systemd service for Pi
echo "⚙️ Oppretter systemd service for Pi..."
sudo tee /etc/systemd/system/rajant-integration.service > /dev/null <<EOF
[Unit]
Description=Rajant Tunnel Integration Service (Pi)
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python rajant_integration.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

# Pi-spesifikke innstillinger
Nice=10
CPUAccounting=true
CPUQuota=80%
MemoryAccounting=true
MemoryHigh=500M
MemoryMax=800M

[Install]
WantedBy=multi-user.target
EOF

# Setup log directory with Pi permissions
echo "📊 Setter opp logging..."
sudo mkdir -p /var/log/rajant
sudo chown pi:pi /var/log/rajant

# Pi performance optimization
echo "🚀 Pi ytelse-optimalisering..."

# Disable unnecessary services on Pi
sudo systemctl disable bluetooth.service
sudo systemctl disable hciuart.service

# Enable SSH for remote management
sudo systemctl enable ssh

# Memory split optimization (less GPU memory for headless)
echo "gpu_mem=16" | sudo tee -a /boot/config.txt

# Create monitoring script for Pi
cat > $INSTALL_DIR/pi_monitor.sh << 'EOF'
#!/bin/bash
# Pi Resource Monitor for Tunnel Tracking

echo "🍓 Pi Resource Status:"
echo "====================="
echo "Uptime: $(uptime)"
echo "CPU Temp: $(vcgencmd measure_temp)"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory: $(free -h | awk '/^Mem:/ {printf "Used: %s / %s (%.1f%%)\n", $3, $2, $3*100/$2}')"
echo "Disk: $(df -h / | awk '/\// {printf "Used: %s / %s (%s)\n", $3, $2, $5}' | tail -1)"
echo ""
echo "🔗 Rajant Service Status:"
systemctl is-active rajant-integration --quiet && echo "✅ Service Running" || echo "❌ Service Stopped"
echo ""
echo "📊 Last 5 log entries:"
tail -5 /var/log/rajant-integration.log 2>/dev/null || echo "No logs yet"
EOF

chmod +x $INSTALL_DIR/pi_monitor.sh

# Network connectivity test
echo "🔍 Tester nettverksoppsett..."
echo "Pi IP: $(hostname -I | awk '{print $1}')"

# Test if we can reach common Rajant IP
if ping -c 1 -W 3 192.168.100.10 &> /dev/null; then
    echo "✅ Kan nå Rajant node 192.168.100.10"
else
    echo "⚠️  Kan ikke nå Rajant node 192.168.100.10"
    echo "   Dette er normalt hvis nodene ikke er satt opp ennå"
fi

# Test internet connectivity for Firebase
if ping -c 1 -W 3 8.8.8.8 &> /dev/null; then
    echo "✅ Internettilkobling OK"
else
    echo "❌ Ingen internettilkobling - kreves for Firebase API"
fi

# Create update script
cat > $INSTALL_DIR/update_system.sh << 'EOF'
#!/bin/bash
# System Update Script for Pi

echo "🔄 Oppdaterer Pi system..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Oppdaterer Python packages..."
source /opt/rajant-integration/venv/bin/activate
pip install --upgrade pip
pip install --upgrade requests pyyaml python-dotenv psutil

echo "🔄 Restarter tjeneste..."
sudo systemctl restart rajant-integration

echo "✅ System oppdatert!"
EOF

chmod +x $INSTALL_DIR/update_system.sh

# Final setup information
echo ""
echo "✅ Raspberry Pi setup fullført!"
echo ""
echo "📝 Neste steg:"
echo "1. Rediger konfigurasjon: nano $INSTALL_DIR/config_pi.yaml"
echo "2. Legg til dine Rajant node IP-adresser"
echo "3. Start tjenesten: sudo systemctl enable rajant-integration"
echo "4. Test systemet: sudo systemctl start rajant-integration"
echo ""
echo "🔧 Nyttige kommandoer på Pi:"
echo "Status:    sudo systemctl status rajant-integration"
echo "Logs:      journalctl -u rajant-integration -f"
echo "Monitor:   $INSTALL_DIR/pi_monitor.sh"
echo "Update:    $INSTALL_DIR/update_system.sh"
echo "SSH:       ssh pi@$(hostname -I | awk '{print $1}')"
echo ""
echo "📊 Pi-spesifikke tips:"
echo "- Bruk 'pi_monitor.sh' for å sjekke ressursbruk"
echo "- Service restarter automatisk ved feil"
echo "- CPU/Memory limits er satt for stabil drift"
echo "- Remote SSH tilgang er aktivert"

# Optional reboot
read -p "Vil du restarte Pi nå for å aktivere alle endringer? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Restarter Pi i 5 sekunder..."
    sleep 5
    sudo reboot
fi 