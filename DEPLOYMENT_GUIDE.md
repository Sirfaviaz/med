# Complete Deployment Guide to Oracle Cloud + Hostinger

## Part 1: Git Setup (5 minutes)

### Step 1: Install Git (if not installed)
- Download: https://git-scm.com/download/win
- Install with default settings

### Step 2: Configure Git (first time only)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 3: Initialize Git Repository
```bash
# In your project directory (D:\Medical)
git init
git add .
git commit -m "Initial commit - Medical Tracker production ready"
```

## Part 2: Push to GitHub (5 minutes)

### Step 1: Create GitHub Account
1. Go to: https://github.com/signup
2. Create free account
3. Verify email

### Step 2: Create New Repository on GitHub
1. Click "+" → "New repository"
2. Name: `medical-tracker`
3. Description: "Medical tracking web application"
4. Choose: **Public** (for free account)
5. DON'T initialize with README
6. Click "Create repository"

### Step 3: Push to GitHub
```bash
# GitHub will show you these commands, use them:
git remote add origin https://github.com/YOUR_USERNAME/medical-tracker.git
git branch -M main
git push -u origin main
```

Enter your GitHub username and password when prompted.

## Part 3: Oracle Cloud Setup (15 minutes)

### Step 1: Sign Up for Oracle Cloud
1. Go to: https://www.oracle.com/cloud/free/
2. Click "Start for Free"
3. Enter your details
4. Create account (need credit card for verification, but it's free)
5. Verify your email

### Step 2: Create Compute Instance
1. Login to Oracle Cloud Console
2. Click "Create a VM Instance"
3. Configure:
   - **Name**: `medical-tracker`
   - **Shape**: Always Free Eligible (VM.Standard.E2.1.Micro)
   - **OS**: Ubuntu 22.04
   - **SSH Key**: Add your SSH key or generate new one
4. Click "Create"

### Step 3: Configure Security (IMPORTANT!)
1. Go to: Networking → Virtual Cloud Networks
2. Click on your VCN
3. Go to: Security Lists
4. Click "Default Security List"
5. Click "Add Ingress Rule":
   - Source: 0.0.0.0/0
   - IP Protocol: TCP
   - Destination Port Range: 5000
   - Description: Medical Tracker App

## Part 4: Deploy to Oracle Cloud (10 minutes)

### Step 1: Connect to Your Instance
```bash
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
```

### Step 2: Install Required Software
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx (for reverse proxy)
sudo apt install nginx -y

# Install Git
sudo apt install git -y
```

### Step 3: Clone Your Repository
```bash
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/medical-tracker.git
cd medical-tracker
```

### Step 4: Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Application
```bash
# Create environment file
nano .env
```

Add these lines:
```
SECRET_KEY='your-very-strong-secret-key-min-32-chars'
FLASK_ENV='production'
DATABASE_URL='sqlite:///medical_app.db'
```

Save: Ctrl+X, then Y, then Enter

```bash
# Create uploads directory
mkdir uploads
```

### Step 6: Create Systemd Service
```bash
sudo nano /etc/systemd/system/medical-tracker.service
```

Add this content:
```ini
[Unit]
Description=Medical Tracker Web Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/medical-tracker
Environment="PATH=/home/ubuntu/medical-tracker/venv/bin"
ExecStart=/home/ubuntu/medical-tracker/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Save and exit, then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable medical-tracker
sudo systemctl start medical-tracker
sudo systemctl status medical-tracker
```

## Part 5: Nginx Configuration (Reverse Proxy)

### Step 1: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/medical-tracker
```

Add this:
```nginx
server {
    listen 80;
    server_name your-subdomain.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Save and create symlink:
```bash
sudo ln -s /etc/nginx/sites-available/medical-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Part 6: Hostinger Domain Setup (5 minutes)

### Step 1: Configure DNS in Hostinger
1. Login to Hostinger control panel
2. Go to **Domains** → Your domain
3. Click **DNS / Nameservers**
4. Add DNS Record:

**Type A Record**:
- Name: `medical` (or your subdomain name)
- Points to: `YOUR_ORACLE_PUBLIC_IP`
- TTL: 3600

### Step 2: Wait for DNS Propagation
- Usually takes 5-30 minutes
- Check at: https://www.whatsmydns.net/

## Part 7: SSL Certificate (Optional but Recommended)

### Install Certbot for HTTPS:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d medical.yourdomain.com
```

Follow the prompts and choose to redirect HTTP to HTTPS.

## Verification Checklist

✅ Code pushed to GitHub  
✅ Oracle Cloud instance running  
✅ Security rules configured (port 5000)  
✅ Application running on instance  
✅ Nginx configured as reverse proxy  
✅ DNS configured in Hostinger  
✅ Domain pointing to server  
✅ SSL certificate installed (optional)  

## Troubleshooting

### Can't connect to instance:
```bash
# Check if server is running
sudo systemctl status medical-tracker

# Check logs
sudo journalctl -u medical-tracker -f
```

### Port not accessible:
```bash
# Check if app is listening
netstat -tuln | grep 5000

# Check Oracle Security Lists
# Make sure port 5000 is open
```

### DNS not working:
- Wait 10-30 minutes
- Clear browser cache
- Try from different network
- Check: https://www.whatsmydns.net/

## Quick Commands Reference

```bash
# Restart app
sudo systemctl restart medical-tracker

# View logs
sudo journalctl -u medical-tracker -f

# Stop app
sudo systemctl stop medical-tracker

# Update app
cd /home/ubuntu/medical-tracker
git pull
sudo systemctl restart medical-tracker
```

