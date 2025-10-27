# Fix Oracle Cloud Firewall - Network Security Group (NSG)

## The Issue
Port 80 is accessible locally but blocked from the internet because your instance uses a **Network Security Group (NSG)** that needs separate firewall rules.

---

## Step-by-Step: Add Port 80 & 443 to NSG

### Step 1: Identify the NSG Attached to Your Instance

1. **Go to Oracle Cloud Console** → Log in
2. **Navigate to**: Compute → Instances
3. **Click on your instance**: "Med"
4. **Scroll down to "Network Security Groups"** section
5. **Note the NSG name** (e.g., `ig-quick-action-NSG`)

---

### Step 2: Open the Network Security Group

**Option A: From Instance Page**
- In the "Network Security Groups" section, click on the NSG name

**Option B: Direct Navigation**
1. Go to: **Networking** → **Network Security Groups**
2. Find and click on the NSG name you noted

---

### Step 3: Add Ingress Rule for Port 80 (HTTP)

1. In the NSG page, click **"Add Ingress Rules"** button
2. Fill in the form:
   - **Stateless**: `No` (use stateful rules - default)
   - **Source Type**: `CIDR`
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: `TCP`
   - **Source Port Range**: (leave blank or "All")
   - **Destination Port Range**: `80`
   - **Description**: `Allow HTTP for SSL certificate`
3. Click **"Add Ingress Rules"**

---

### Step 4: Add Ingress Rule for Port 443 (HTTPS)

1. Click **"Add Ingress Rules"** again
2. Fill in:
   - **Stateless**: `No`
   - **Source Type**: `CIDR`
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: `TCP`
   - **Destination Port Range**: `443`
   - **Description**: `Allow HTTPS`
3. Click **"Add Ingress Rules"**

---

### Step 5: Wait and Test

Wait 1-2 minutes for the rules to propagate.

**Test from Windows CMD:**
```bash
curl -I http://medical.fvzmhd.pro
```

You should see HTTP headers, not a timeout error.

---

### Step 6: Run Certbot

Once port 80 is accessible:

```bash
sudo certbot --nginx -d medical.fvzmhd.pro
```

Follow the prompts:
- Enter your email
- Agree to terms
- Optionally redirect HTTP to HTTPS

---

## Troubleshooting

### If port 80 still times out:

Check both places:
1. **Network Security Group (NSG)** - for instance-level rules
2. **Security List** - for subnet-level rules (add rules here too if needed)

**Add to Security List as well:**
1. Go to: **Networking** → **Virtual Cloud Networks** → `vcn-20251027-0415`
2. Click **"Security Lists"** → **Default Security List**
3. Add Ingress Rules for ports 80 and 443 (same settings as NSG)

### Check if rules are applied:

From Oracle server:
```bash
# Test locally
curl -I http://localhost:80

# Check iptables (might block even with NSG rules)
sudo iptables -L -n -v

# If iptables is blocking, flush rules
sudo iptables -F
```

---

## Oracle Cloud Documentation References

- [Network Security Groups](https://docs.oracle.com/iaas/Content/Network/Concepts/networksecuritygroups.htm)
- [Security Rules](https://docs.oracle.com/iaas/Content/Network/Concepts/securityrules.htm)
- [Adding an Ingress Rule to an NSG](https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/managingNSGs.htm#Creating_Inbound_Rules)

---

## Quick Checklist

- [ ] Find NSG attached to "Med" instance
- [ ] Open the NSG
- [ ] Add Ingress Rule: Port 80, TCP, 0.0.0.0/0
- [ ] Add Ingress Rule: Port 443, TCP, 0.0.0.0/0
- [ ] Wait 2 minutes
- [ ] Test: `curl -I http://medical.fvzmhd.pro`
- [ ] Run: `sudo certbot --nginx -d medical.fvzmhd.pro`

