# SSL Setup for Medical Tracker - Oracle Cloud

## Your Details
- **Subdomain**: medical.fvzmhd.pro
- **IP Address**: 68.233.114.185

---

## Step 1: Setup DNS in Hostinger

1. **Login to Hostinger**
2. Go to: **Domains** → **fvzmhd.pro** → **DNS** → **Manage DNS**
3. **Add A Record**:
   - **Type**: A
   - **Name**: `medical`
   - **Points to**: `68.233.114.185`
   - **TTL**: `3600`
4. **Save**
5. **Wait 5-30 minutes** for DNS propagation
6. **Test**: Run `ping medical.fvzmhd.pro` - should return 68.233.114.185

---

## Step 2: Setup Nginx + SSL on Oracle Server

**SSH into your Oracle server** and run:

```bash
cd /home/ubuntu/med

# Install Nginx and Certbot
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/medical-tracker
```

**Paste this configuration:**

```nginx
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
```

**Save**: Ctrl+X, Y, Enter

**Enable and test:**

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/medical-tracker /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## Step 3: Get SSL Certificate

**After DNS is propagated** (wait 5-30 minutes), run:

```bash
sudo certbot --nginx -d medical.fvzmhd.pro
```

**Follow the prompts:**
- Enter your email address
- Agree to terms
- Choose to redirect HTTP to HTTPS (option 2)

---

## Step 4: Test Your Site

Access your secure site at:
**https://medical.fvzmhd.pro**

You should see:
- ✅ Green padlock in browser
- ✅ HTTPS in URL
- ✅ Your login page

---

## Step 5: Auto-Renewal

Certbot sets up auto-renewal automatically! Test it:

```bash
# Test renewal
sudo certbot renew --dry-run

# Check when it runs
sudo systemctl status certbot.timer
```

---

## Firewall Configuration

Make sure port 80 and 443 are open in Oracle Cloud:

1. **Oracle Cloud Console** → Your VCN
2. **Security Lists** → **Default Security List**
3. **Add Ingress Rules**:
   - **Port 80** (HTTP)
   - **Port 443** (HTTPS)
   - Both from CIDR: `0.0.0.0/0`

---

## Troubleshooting

### DNS not working?
- Wait longer (up to 48 hours)
- Check: `nslookup medical.fvzmhd.pro`
- Should return: `68.233.114.185`

### Certbot fails?
- Make sure DNS is working first
- Make sure port 80 is open
- Run: `sudo certbot certificates` to see status

### Can't access site?
- Check Nginx: `sudo systemctl status nginx`
- Check logs: `sudo tail -f /var/log/nginx/error.log`
- Check app: `sudo systemctl status medical-tracker`

---

## Success! 🎉

Your app is now secure at: **https://medical.fvzmhd.pro**

