# Oracle Cloud Deployment - Step by Step

## Your Server Details
- **Public IP**: 68.233.114.185
- **Private IP**: 10.0.0.254
- **Username**: ubuntu

---

## Step 1: Configure Firewall (Open Port 5000)

### In Oracle Cloud Console:

1. **Go to VCN**
   - Click ☰ Menu → **Networking** → **Virtual Cloud Networks**
   - Click: `vcn-20251027-0415`

2. **Open Security Lists**
   - Click: **"Security Lists"** (left sidebar)
   - Click: **"Default Security List"**

3. **Add Ingress Rule**
   - Scroll to **"Ingress Rules"**
   - Click: **"Add Ingress Rule"**
   - Fill in:
     ```
     CIDR: 0.0.0.0/0
     Source Type: CIDR
     IP Protocol: TCP
     Destination Port Range: 5000
     Description: Medical Tracker App
     ```
   - Click: **"Add Ingress Rules"**

---

## Step 2: Connect to Your Server

### Option A: Using Windows PowerShell

Open PowerShell and run:

```powershell
# Set permissions for the key
$keyPath = "D:\Downloads\ssh-key-2025-10-26.key"
icacls $keyPath /inheritance:r
icacls $keyPath /grant "$env:USERNAME:R"

# Connect
ssh -i "D:\Downloads\ssh-key-2025-10-26.key" ubuntu@68.233.114.185
```

### Option B: Using PuTTY (Recommended for Windows)

1. Download PuTTY: https://www.putty.org/
2. Open PuTTY
3. Enter:
   - Host: `68.233.114.185`
   - Port: `22`
   - Connection Type: `SSH`
4. Click: **"Auth"** → **"Credentials"**
5. Browse: Select `ssh-key-2025-10-26.key`
6. Click: **"Open"**
7. Login as: `ubuntu`

---

## Step 3: Deploy the Application

Once connected to the server, copy and paste these commands **ONE BY ONE**:

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv git nginx

# 3. Clone your repository
cd /home/ubuntu
git clone https://github.com/Sirfaviaz/med.git
cd med

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# 6. Create uploads directory
mkdir uploads

# 7. Create environment file
cat > .env << 'EOF'
SECRET_KEY='medical-tracker-secret-key-2025-change-this'
FLASK_ENV='production'
DATABASE_URL='sqlite:///medical_app.db'
EOF

# 8. Test run (will run in background)
python app.py &

# 9. Wait 3 seconds
sleep 3

# 10. Check if running
curl http://localhost:5000
```

**Expected Output**: You should see HTML output from the Flask app.

---

## Step 4: Create System Service (Run in Background)

```bash
# Create service file
sudo nano /etc/systemd/system/medical-tracker.service
```

**Copy and paste this entire block:**

```ini
[Unit]
Description=Medical Tracker Web Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/med
Environment="PATH=/home/ubuntu/med/venv/bin"
ExecStart=/home/ubuntu/med/venv/bin/python /home/ubuntu/med/app.py
Restart=always
Environment="SECRET_KEY=medical-tracker-secret-key-2025"
Environment="FLASK_ENV=production"

[Install]
WantedBy=multi-user.target
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

**Enable and start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable medical-tracker
sudo systemctl start medical-tracker
```

**Check status:**

```bash
sudo systemctl status medical-tracker
```

You should see: **"active (running)"** in green.

---

## Step 5: Access Your Application

Open your web browser and go to:

**http://68.233.114.185:5000**

You should see the login page!

---

## Step 6: View Logs (If Needed)

```bash
# View live logs
sudo journalctl -u medical-tracker -f

# View last 100 lines
sudo journalctl -u medical-tracker -n 100

# Restart the service
sudo systemctl restart medical-tracker
```

---

## Troubleshooting

### Can't connect via SSH
- Check if key permissions are correct
- Try using PuTTY instead of PowerShell

### Can't access the website
- Check if port 5000 is open in Oracle Cloud firewall
- Verify service is running: `sudo systemctl status medical-tracker`
- Check logs: `sudo journalctl -u medical-tracker -f`

### App won't start
- Check Python is installed: `python3 --version`
- Check virtual environment: `source venv/bin/activate && python --version`
- Check logs: `sudo journalctl -u medical-tracker -f`

---

## Quick Commands Reference

```bash
# Start service
sudo systemctl start medical-tracker

# Stop service
sudo systemctl stop medical-tracker

# Restart service
sudo systemctl restart medical-tracker

# View status
sudo systemctl status medical-tracker

# View logs
sudo journalctl -u medical-tracker -f

# Update app
cd /home/ubuntu/med
git pull
sudo systemctl restart medical-tracker
```

---

## Next: Configure Hostinger DNS

1. Login to Hostinger
2. Go to Domains → Your Domain → DNS
3. Add A Record:
   - Name: `medical`
   - Points to: `68.233.114.185`
   - TTL: `3600`
4. Wait 5-30 minutes
5. Access at: `http://medical.yourdomain.com:5000`

---

## Success! 🎉

Your medical tracker is now live at: **http://68.233.114.185:5000**

