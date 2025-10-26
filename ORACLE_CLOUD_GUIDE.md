# Oracle Cloud Setup - Detailed Step-by-Step Guide

## Part 1: Creating Your Oracle Cloud Account

### Step 1: Sign Up (Free Forever)
1. Go to: **https://www.oracle.com/cloud/free/**
2. Click the big **"Start for Free"** button
3. Fill in your details:
   - Email address
   - Password
   - First and Last name
   - Company name (optional)
   - Phone number (for verification)
4. Select your country
5. Check the terms and conditions
6. Click **"Verify My Email"**

### Step 2: Verify Your Account
1. Check your email for verification link
2. Click the verification link
3. You'll be asked for credit card (for verification only - won't be charged)
4. Oracle needs this to verify you're a real person
5. Complete the verification
6. Wait for account provisioning (usually 5-15 minutes)

### Step 3: First Login
1. Go to: **https://cloud.oracle.com/**
2. Click **"Sign In"**
3. Enter your email and password
4. Accept any terms that appear

---

## Part 2: Creating Your First Virtual Machine

### Step 1: Navigate to Compute
1. After logging in, you'll see the **Oracle Cloud Console Dashboard**
2. Look at the top menu bar, click **"☰" (Hamburger menu)** on the top left
3. Scroll down to **"Compute"**
4. Click **"Compute"** → **"Instances"**

### Step 2: Start Creating Your VM
1. You'll see a page with **"Create Instance"** button (big orange button)
2. Click **"Create Instance"**

### Step 3: Fill in the Details

#### 3.1: Basic Information
- **Name**: Type `medical-tracker` (or any name you like)
- **Placement**: Keep default (Fault Domain)

#### 3.2: Image and Shape (THIS IS CRITICAL!)

**Image Section:**
- Click "Edit" or "Change image"
- Select **"Canonical Ubuntu"**
- Choose **"Ubuntu 22.04"** or latest version

**Shape Section:**
- Click "Edit" or "Change shape"
- Look for **"Ampere A1 Compute (VM)"** or **"VM.Standard.E2.1.Micro"**
- These are the **FREE** options
- Select one of them
- Click "Select Shape"

**IMPORTANT**: Always Free means:
- 4 ARM-based cores (Ampere)
- OR 1 AMD-based core
- 24 GB memory
- Choose the ARM-based one (Ampere) for better performance

#### 3.3: Configure Networking
- Keep defaults (it will create a VCN for you)
- **Virtual Cloud Network**: Keep default
- **Subnet**: Keep default
- **Assign Public IP**: **YES** (This is IMPORTANT!)

#### 3.4: Add SSH Keys

**Option 1: If you have a Windows computer, create a new key:**

1. **Open PowerShell** (on your Windows machine - D:\Medical)
2. Run this command:
```powershell
ssh-keygen -t rsa -b 4096 -f oracle_key
```
3. Press Enter 3 times (no passphrase needed for simplicity)
4. This creates two files:
   - `oracle_key` (private key - KEEP SECRET)
   - `oracle_key.pub` (public key - this is what we'll use)

5. **Open the public key file:**
```powershell
Get-Content oracle_key.pub
```

6. **Copy the entire output** (starts with ssh-rsa...)

7. Back in Oracle Cloud, select **"Paste Public Keys"**
8. Paste the key you copied
9. It should look like: `ssh-rsa AAAAB3NzaC1yc2EAA... your-email@example.com`

**Option 2: Let Oracle create one for you**
- Select "Generate a new key pair for me"
- Oracle will create and download it
- **SAVE THIS FILE** - you'll need it to connect!

#### 3.5: Review and Create
1. Scroll down and review your settings
2. Make sure everything looks correct
3. Click the green **"Create"** button
4. Wait 1-2 minutes for the VM to be created

---

## Part 3: Configuring Security (Firewall Rules)

### Step 1: Get Your Public IP
1. After VM is created, go to **"Instance Details"** page
2. Look for **"Public IP Address"** 
3. **COPY THIS IP** - you'll need it later!
   - Something like: `132.145.123.45`

### Step 2: Configure Firewall (CRITICAL!)

Your app runs on port 5000, but it's blocked by default. We need to open it:

1. On the same page, scroll down to **"Primary VCN"**
2. Click the **VCN name** (blue link)
3. You're now in the VCN details page
4. On the left sidebar, click **"Security Lists"**
5. Click **"Default Security List"** (or the first one)
6. Find **"Ingress Rules"** section
7. Click **"Add Ingress Rules"**

**Fill in the form:**
- **CIDR**: `0.0.0.0/0` (allows all IPs - we'll secure later)
- **Source Type**: `CIDR`
- **IP Protocol**: `TCP`
- **Destination Port Range**: `5000`
- **Description**: `Medical Tracker App`
- Click **"Add Ingress Rule"**

8. **Do the same for port 80 and 443 (for future HTTPS):**
   - Add another rule for port `80`
   - Add another rule for port `443`

### Step 3: Note Your Details
Before closing, note down:
- **Public IP**: `________________`
- **Username**: `ubuntu` (usually)
- **Port 22**: Already open (for SSH)

---

## Part 4: Connecting to Your Server

### Step 1: Open PowerShell/Terminal
On your Windows machine, open PowerShell in your Medical folder.

### Step 2: Connect via SSH
```bash
# If you generated your own key:
ssh -i oracle_key ubuntu@YOUR_PUBLIC_IP

# If Oracle generated the key:
ssh -i path/to/downloaded_key ubuntu@YOUR_PUBLIC_IP
```

**Example:**
```bash
ssh -i oracle_key ubuntu@132.145.123.45
```

### Step 3: First Connection
First time connecting, you'll see:
```
The authenticity of host '132.145.123.45' can't be established.
RSA key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```
Type: `yes`

### Step 4: You're In!
You should now see:
```
Welcome to Ubuntu 22.04 LTS
ubuntu@medical-tracker:~
```

---

## Part 5: Installing Required Software

Copy and paste these commands one by one:

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python and Tools
```bash
sudo apt install -y python3 python3-pip python3-venv
```

### 3. Install Git
```bash
sudo apt install -y git
```

### 4. Install Nginx (for reverse proxy later)
```bash
sudo apt install -y nginx
```

### 5. Verify Installations
```bash
python3 --version  # Should show Python 3.10+
git --version      # Should show git version
```

---

## Part 6: Deploying Your Application

### Step 1: Clone Your Repository
```bash
cd /home/ubuntu
git clone https://github.com/Sirfaviaz/med.git
cd med
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your prompt.

### Step 3: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Create Upload Directory
```bash
mkdir uploads
```

### Step 5: Set Environment Variables
```bash
nano .env
```

Paste this:
```
SECRET_KEY='generate-a-strong-random-key-here-use-crypto'
FLASK_ENV='production'
```

To save: Press `Ctrl+X`, then `Y`, then `Enter`

### Step 6: Test Run
```bash
python app.py
```

You should see:
```
INFO:werkzeug: * Running on all addresses (0.0.0.0)
INFO:werkzeug: * Running on http://0.0.0.0:5000
```

Press `Ctrl+C` to stop it.

---

## Part 7: Running in Background (Systemd Service)

### Step 1: Create Service File
```bash
sudo nano /etc/systemd/system/medical-tracker.service
```

### Step 2: Paste This Config
```ini
[Unit]
Description=Medical Tracker Web Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/med
Environment="PATH=/home/ubuntu/med/venv/bin"
Environment="SECRET_KEY=your-secret-key-here"
Environment="FLASK_ENV=production"
ExecStart=/home/ubuntu/med/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 3: Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable medical-tracker
sudo systemctl start medical-tracker
```

### Step 4: Check Status
```bash
sudo systemctl status medical-tracker
```

You should see: **"active (running)"** in green.

### Step 5: Check Logs
```bash
sudo journalctl -u medical-tracker -f
```

Press `Ctrl+C` to exit.

---

## Part 8: Access Your Application

### Test Locally on Server
```bash
curl http://localhost:5000
```

### Test from Browser
Go to: **http://YOUR_PUBLIC_IP:5000**

Example: `http://132.145.123.45:5000`

You should see the login page!

---

## Troubleshooting

### Can't SSH into server
- Check if you copied the SSH key correctly
- Verify public IP is correct
- Wait 5 minutes after creating the VM

### Can't access the website
- Check firewall rules (ports 5000, 80, 443)
- Verify service is running: `sudo systemctl status medical-tracker`
- Check app logs: `sudo journalctl -u medical-tracker -f`

### Service won't start
- Check logs: `sudo journalctl -u medical-tracker -f`
- Verify all dependencies installed: `pip list`
- Check if uploads folder exists: `ls uploads/`

### Port already in use
```bash
sudo netstat -tuln | grep 5000
sudo killall python
sudo systemctl restart medical-tracker
```

---

## Quick Commands Reference

```bash
# Start app
sudo systemctl start medical-tracker

# Stop app
sudo systemctl stop medical-tracker

# Restart app
sudo systemctl restart medical-tracker

# View status
sudo systemctl status medical-tracker

# View logs
sudo journalctl -u medical-tracker -f

# View last 100 lines
sudo journalctl -u medical-tracker -n 100
```

---

## Next: Configure Hostinger Domain

Once your app is running at `http://YOUR_IP:5000`, you need to:

1. Login to Hostinger
2. Go to **Domains** → Your domain → **DNS**
3. Add **A Record**:
   - Name: `medical`
   - Points to: `YOUR_ORACLE_PUBLIC_IP`
   - TTL: `3600`
4. Wait 5-30 minutes
5. Access at: `http://medical.yourdomain.com:5000`

---

## Optional: Configure Nginx (Remove Port from URL)

Instead of `http://medical.yourdomain.com:5000`, you want `http://medical.yourdomain.com`

### Create Nginx Config
```bash
sudo nano /etc/nginx/sites-available/medical-tracker
```

Paste:
```nginx
server {
    listen 80;
    server_name medical.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Enable and Restart
```bash
sudo ln -s /etc/nginx/sites-available/medical-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Now you can access without the `:5000` port!

---

## Success Checklist

- [ ] Oracle Cloud account created
- [ ] VM instance created (Always Free shape)
- [ ] Firewall rules configured (ports 5000, 80, 443)
- [ ] SSH connection working
- [ ] Software installed (Python, Git, Nginx)
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Service created and running
- [ ] Application accessible via IP
- [ ] Hostinger DNS configured
- [ ] Domain working
- [ ] Nginx configured (optional)

**Congratulations! Your app is live! 🎉**

