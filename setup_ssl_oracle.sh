#!/bin/bash
# SSL Setup Script for Oracle Cloud with Nginx + Let's Encrypt

echo "==========================================="
echo "Setting up SSL for Medical Tracker"
echo "Subdomain: medical.fvzmhd.pro"
echo "==========================================="

# Install Nginx and Certbot
echo "Step 1: Installing Nginx and Certbot..."
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

echo "Step 2: Creating Nginx configuration..."

# Create Nginx config
sudo tee /etc/nginx/sites-available/medical-tracker > /dev/null << 'EOF'
server {
    listen 80;
    server_name medical.fvzmhd.pro;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

echo "Step 3: Enabling site..."
sudo ln -s /etc/nginx/sites-available/medical-tracker /etc/nginx/sites-enabled/

echo "Step 4: Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "Nginx config is valid!"
    sudo systemctl restart nginx
else
    echo "Nginx config has errors!"
    exit 1
fi

echo ""
echo "==========================================="
echo "Nginx configured!"
echo "==========================================="
echo ""
echo "NEXT STEPS:"
echo "1. Configure DNS in Hostinger:"
echo "   - Type: A"
echo "   - Name: medical"
echo "   - Points to: 68.233.114.185"
echo "   - TTL: 3600"
echo ""
echo "2. Wait 5-30 minutes for DNS propagation"
echo ""
echo "3. Run this command to get SSL certificate:"
echo "   sudo certbot --nginx -d medical.fvzmhd.pro"
echo ""
echo "==========================================="

