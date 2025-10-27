# DNS Fix - Hostinger to Oracle Cloud

## Current Problem
- **Domain**: medical.fvzmhd.pro
- **Currently pointing to**: 129.154.41.255 (WRONG!)
- **Should point to**: 68.233.114.185 (YOUR Oracle server)

---

## Step-by-Step Fix

### In Hostinger Dashboard:

1. **Login** to Hostinger
2. Click **"Manage"** next to your domain `fvzmhd.pro`
3. Click **"DNS / Nameservers"** tab
4. Click **"Manage DNS"** or **"Advanced DNS"**

### Find and Fix the Record:

Look for any of these:
- Record type **A** with name **medical**
- Record type **A** with name **@** or **subdomain**
- Any record pointing to **129.154.41.255**

### If Record Exists:

1. Click **"Edit"** (pencil icon)
2. Change **Points to / Value**: `68.233.114.185`
3. Click **"Save"** or **"Update"**

### If Record Doesn't Exist:

1. Click **"Add Record"** or **"Add New"**
2. Fill in:
   - **Type**: A
   - **Name**: `medical`
   - **Points to / Value**: `68.233.114.255`
   - **TTL**: 3600 (or auto)
3. Click **"Add Record"** or **"Save"**

---

## Verify DNS Update

Wait 5 minutes, then check:

**From your Windows computer:**
```cmd
nslookup medical.fvzmhd.pro
```

**Should show**:
```
Name:    medical.fvzmhd.pro
Address: 68.233.114.185
```

**From Oracle server:**
```bash
nslookup medical.fvzmhd.pro
```

---

## After DNS is Fixed

Once DNS points to the correct IP (68.233.114.185), run:

```bash
sudo certbot certonly --standalone -d medical.fvzmhd.pro
```

This should work!

---

## Troubleshooting

### Still showing wrong IP after 30 minutes?
- Clear your DNS cache: `ipconfig /flushdns` (Windows)
- Check online: https://www.whatsmydns.net/#A/medical.fvzmhd.pro
- Wait longer (can take up to 48 hours)

### Need Help?
Share a screenshot of your Hostinger DNS records and I'll help you fix it.

