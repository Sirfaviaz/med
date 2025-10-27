# Oracle Cloud Firewall - Complete Setup

## The Problem
Your instance has a Network Security Group (NSG) attached which controls traffic at the instance level.
Security List rules alone won't work - you need NSG rules!

## Step-by-Step Fix

### Step 1: Find Your Network Security Group

In Oracle Cloud Console:

1. **Go to your instance** (`Med`)
2. **Click on "Attached VNICs"**
3. Look for **"Network Security Groups"** section
4. You'll see something like: `ig-quick-action-NSG` or similar
5. **CLICK ON THE NSG NAME**

---

### Step 2: Add Ingress Rules to NSG

In the NSG page:

1. Click **"Add Ingress Rules"**
2. **Fill in for HTTP (Port 80)**:
   ```
   Stateless: No (leave as default)
   Source Type: CIDR
   Source CIDR: 0.0.0.0/0
   IP Protocol: TCP
   Source Port Range: (leave blank)
   Destination Port Range: 80
   Description: Allow HTTP for SSL
   ```
   Click **"Add Ingress Rule"**

3. **Click "Add Ingress Rules" again for HTTPS (Port 443)**:
   ```
   Stateless: No
   Source Type: CIDR
   Source CIDR: 0.0.0.0/0
   IP Protocol: TCP
   Destination Port Range: 443
   Description: Allow HTTPS
   ```
   Click **"Add Ingress Rule"**

---

### Step 3: Wait and Test

Wait 1-2 minutes, then test from Windows:

```bash
# Test HTTP
curl -I http://medical.fvzmhd.pro

# Should see HTTP headers, not timeout
```

---

### Step 4: Run Certbot

Once port 80 is accessible:

```bash
sudo certbot --nginx -d medical.fvzmhd.pro
```

---

## Quick Checklist

- [ ] Find the NSG attached to your instance
- [ ] Add Ingress Rule: Port 80, TCP, 0.0.0.0/0
- [ ] Add Ingress Rule: Port 443, TCP, 0.0.0.0/0
- [ ] Wait 1-2 minutes
- [ ] Test: `curl -I http://medical.fvzmhd.pro`
- [ ] Run: `sudo certbot --nginx -d medical.fvzmhd.pro`

---

## Alternative: Use Existing NSG Rules

You already have:
- `ig-quick-action-NSG` mentioned in your instance

That NSG probably already has port 5000 open. Just add ports 80 and 443 to the same NSG.

