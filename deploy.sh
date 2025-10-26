#!/bin/bash
# Medical Tracker - Oracle Cloud Deployment Script

echo "=========================================="
echo "Medical Tracker - Deployment Script"
echo "=========================================="

# Update system
echo "Step 1: Updating system..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "Step 2: Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv git nginx

# Clone repository
echo "Step 3: Cloning repository..."
cd /home/ubuntu
git clone https://github.com/Sirfaviaz/med.git
cd med

# Create virtual environment
echo "Step 4: Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Step 5: Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create uploads directory
echo "Step 6: Creating uploads directory..."
mkdir uploads

# Create environment file
echo "Step 7: Creating environment configuration..."
cat > .env << EOF
SECRET_KEY='medical-tracker-secret-key-2025-change-this-in-production'
FLASK_ENV='production'
DATABASE_URL='sqlite:///medical_app.db'
EOF

echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo "Testing the application..."
python app.py &

sleep 5
echo ""
echo "=========================================="
echo "Application is running on:"
echo "http://68.233.114.185:5000"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure firewall rule for port 5000 in Oracle Cloud"
echo "2. Test: http://68.233.114.185:5000"
echo "3. Press Ctrl+C to stop"
echo "=========================================="

