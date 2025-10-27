#!/bin/bash
# Setup systemd service for Oracle Cloud deployment

echo "Creating systemd service..."

sudo tee /etc/systemd/system/medical-tracker.service > /dev/null << 'EOF'
[Unit]
Description=Medical Tracker Web Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/med
Environment="PATH=/home/ubuntu/med/venv/bin"
Environment="PORT=5000"
ExecStart=/home/ubuntu/med/venv/bin/python /home/ubuntu/med/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable medical-tracker
sudo systemctl start medical-tracker

echo "Checking status..."
sudo systemctl status medical-tracker

echo ""
echo "========================================="
echo "Service created and started!"
echo "========================================="
echo ""
echo "Useful commands:"
echo "  sudo systemctl status medical-tracker  # Check status"
echo "  sudo systemctl restart medical-tracker # Restart"
echo "  sudo systemctl stop medical-tracker    # Stop"
echo "  sudo journalctl -u medical-tracker -f   # View logs"
echo ""

