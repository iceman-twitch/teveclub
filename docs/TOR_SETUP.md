# Tor Hidden Service Setup Guide

Complete guide to host your Teveclub application as a Tor hidden service (.onion site).

---

## What is a Tor Hidden Service?

- **Anonymous hosting**: Server location hidden
- **Free .onion domain**: Automatically generated
- **No DNS/domain needed**: Works without registration
- **Encrypted traffic**: End-to-end encryption built-in
- **Censorship resistant**: Can't be blocked by ISP/government

---

## Prerequisites

- Ubuntu server with Teveclub running
- Root/sudo access
- Port 3000 accessible locally (127.0.0.1:3000)

---

## Installation Steps

### Step 1: Install Tor

```bash
# Update system
sudo apt update

# Install Tor
sudo apt install -y tor

# Verify installation
tor --version
```

### Step 2: Configure Tor Hidden Service

```bash
# Backup original config
sudo cp /etc/tor/torrc /etc/tor/torrc.backup

# Edit Tor configuration
sudo nano /etc/tor/torrc
```

**Add these lines at the end:**

```
# Teveclub Hidden Service
HiddenServiceDir /var/lib/tor/teveclub/
HiddenServicePort 80 127.0.0.1:3000
```

**Explanation:**
- `HiddenServiceDir`: Where Tor stores your .onion keys
- `HiddenServicePort 80`: External port users connect to (always use 80)
- `127.0.0.1:3000`: Your local Django app

**Save and exit:** `Ctrl+X`, `Y`, `Enter`

### Step 3: Restart Tor

```bash
# Restart Tor service
sudo systemctl restart tor

# Check status
sudo systemctl status tor

# Enable on boot
sudo systemctl enable tor
```

### Step 4: Get Your .onion Address

```bash
# Read your onion address
sudo cat /var/lib/tor/teveclub/hostname
```

**Example output:**
```
abcd1234efgh5678.onion
```

**Save this address!** This is your permanent .onion URL.

### Step 5: Update Django Settings

```bash
cd /home/ubuntu/teveclub/django
nano .env
```

**Update ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS:**

```env
DEBUG=False
SECRET_KEY=5bpkrvg%*t1q**uo=g=(^-12!)&6h$uc^&2ei_z&4e1@l2y_96
ALLOWED_HOSTS=*,abcd1234efgh5678.onion
CSRF_TRUSTED_ORIGINS=http://abcd1234efgh5678.onion,http://*
```

**Or more restrictive:**

```env
ALLOWED_HOSTS=localhost,127.0.0.1,abcd1234efgh5678.onion,98.80.73.143
CSRF_TRUSTED_ORIGINS=http://abcd1234efgh5678.onion,http://98.80.73.143:3000
```

### Step 6: Restart Application

```bash
sudo systemctl restart teveclub
```

### Step 7: Test Your Hidden Service

1. **Download Tor Browser**: https://www.torproject.org/download/
2. **Open Tor Browser**
3. **Visit**: `http://abcd1234efgh5678.onion` (your actual address)
4. **Wait**: First load takes 10-30 seconds

---

## Advanced Configuration

### Custom Vanity .onion Address

Generate custom .onion address (e.g., `teveclub*.onion`):

```bash
# Install mkp224o
sudo apt install -y gcc libsodium-dev make autoconf
git clone https://github.com/cathugger/mkp224o.git
cd mkp224o
./autogen.sh
./configure
make

# Generate vanity address (this takes hours/days)
./mkp224o teveclub -d /tmp/onions -n 1

# Example output after ~2 hours:
# teveclub7a2b3c4d.onion found!

# Copy keys to Tor directory
sudo systemctl stop tor
sudo cp -r /tmp/onions/teveclub*.onion /var/lib/tor/teveclub/
sudo chown -R debian-tor:debian-tor /var/lib/tor/teveclub/
sudo chmod 700 /var/lib/tor/teveclub/
sudo systemctl start tor
```

**Note:** More characters = exponentially longer time. `teveclub` (8 chars) can take days.

### Multiple Services on Different Ports

Edit `/etc/tor/torrc`:

```
# Teveclub Main Site
HiddenServiceDir /var/lib/tor/teveclub/
HiddenServicePort 80 127.0.0.1:3000

# Teveclub Admin Panel
HiddenServiceDir /var/lib/tor/teveclub-admin/
HiddenServicePort 80 127.0.0.1:8000
```

Each gets a unique .onion address.

### Enable v3 Onion Addresses (Recommended)

V3 addresses are longer but more secure (56 characters):

```
# In /etc/tor/torrc
HiddenServiceVersion 3
HiddenServiceDir /var/lib/tor/teveclub/
HiddenServicePort 80 127.0.0.1:3000
```

Restart Tor to generate new v3 address.

### Client Authentication (Private Hidden Service)

Only allow specific clients to access:

```bash
# Generate client keys
sudo tor --keygen

# In /etc/tor/torrc
HiddenServiceDir /var/lib/tor/teveclub/
HiddenServicePort 80 127.0.0.1:3000
HiddenServiceAuthorizeClient stealth client1,client2
```

Share client keys with authorized users only.

---

## Security Hardening

### 1. Disable Direct Access (Clearnet)

Block access to port 3000 from public internet:

```bash
# AWS Security Group: Remove 0.0.0.0/0 from port 3000
# Only allow 127.0.0.1 (localhost)
```

Or use firewall:

```bash
# Allow only localhost
sudo ufw deny 3000
sudo ufw allow from 127.0.0.1 to any port 3000
```

### 2. Disable Server Headers

In Django settings.py:

```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 3. Rate Limiting

Install django-ratelimit:

```bash
source /home/ubuntu/teveclub/venv/bin/activate
pip install django-ratelimit
```

In views:

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m')
def my_view(request):
    pass
```

### 4. Monitor Logs

```bash
# Tor logs
sudo journalctl -u tor -f

# Application logs
tail -f /home/ubuntu/teveclub/logs/error.log
```

---

## Tor + HTTPS (Onion Services v3)

Tor provides encryption, but you can add HTTPS:

### Option 1: Self-Signed Certificate

```bash
# Generate certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/teveclub-onion.key \
  -out /etc/ssl/certs/teveclub-onion.crt

# Configure Nginx (if using)
sudo nano /etc/nginx/sites-available/teveclub-onion
```

```nginx
server {
    listen 127.0.0.1:3000 ssl;
    
    ssl_certificate /etc/ssl/certs/teveclub-onion.crt;
    ssl_certificate_key /etc/ssl/private/teveclub-onion.key;
    
    location / {
        proxy_pass http://127.0.0.1:3001;
    }
}
```

### Option 2: Use HTTP (Recommended for .onion)

Tor already encrypts all traffic. HTTPS is redundant and causes browser warnings.

---

## Troubleshooting

### Hidden Service Not Working

1. **Check Tor status:**
   ```bash
   sudo systemctl status tor
   sudo journalctl -u tor -n 50
   ```

2. **Verify hostname exists:**
   ```bash
   sudo cat /var/lib/tor/teveclub/hostname
   ```

3. **Check permissions:**
   ```bash
   sudo ls -la /var/lib/tor/teveclub/
   # Should be owned by debian-tor
   ```

4. **Fix permissions:**
   ```bash
   sudo chown -R debian-tor:debian-tor /var/lib/tor/teveclub/
   sudo chmod 700 /var/lib/tor/teveclub/
   sudo systemctl restart tor
   ```

### Slow Connection

- First connection takes 30-60 seconds (normal)
- Tor routes through 3+ nodes (slower than clearnet)
- Use `KeepAlive` in Django settings to maintain connections

### Can't Access from Tor Browser

1. **Check Django is running:**
   ```bash
   curl http://127.0.0.1:3000
   ```

2. **Check ALLOWED_HOSTS:**
   ```bash
   cd /home/ubuntu/teveclub/django
   cat .env | grep ALLOWED_HOSTS
   ```

3. **Check Tor config:**
   ```bash
   sudo cat /etc/tor/torrc | grep HiddenService
   ```

### Address Changes After Restart

If your .onion address changes, you deleted keys:

```bash
# Never delete /var/lib/tor/teveclub/ directory!
# Backup keys:
sudo cp -r /var/lib/tor/teveclub/ ~/teveclub-onion-backup/
```

---

## Complete Setup Script

Run this for automated setup:

```bash
#!/bin/bash

# Install Tor
sudo apt update
sudo apt install -y tor

# Configure Hidden Service
sudo tee -a /etc/tor/torrc > /dev/null << 'EOF'

# Teveclub Hidden Service
HiddenServiceDir /var/lib/tor/teveclub/
HiddenServicePort 80 127.0.0.1:3000
EOF

# Restart Tor
sudo systemctl restart tor
sudo systemctl enable tor

# Wait for key generation
sleep 5

# Get onion address
ONION_ADDR=$(sudo cat /var/lib/tor/teveclub/hostname)

echo "======================================"
echo "Your .onion address is:"
echo "http://$ONION_ADDR"
echo "======================================"

# Update Django settings
cd /home/ubuntu/teveclub/django
cp .env .env.backup

# Add onion address to ALLOWED_HOSTS
sed -i "s/ALLOWED_HOSTS=\*/ALLOWED_HOSTS=*,$ONION_ADDR/" .env
sed -i "s|CSRF_TRUSTED_ORIGINS=http://\*,https://\*|CSRF_TRUSTED_ORIGINS=http://*,https://*,http://$ONION_ADDR|" .env

# Restart application
sudo systemctl restart teveclub

echo "Setup complete!"
echo "Visit: http://$ONION_ADDR (using Tor Browser)"
```

Save as `setup_tor.sh`, then run:

```bash
chmod +x setup_tor.sh
./setup_tor.sh
```

---

## Tor + Cloudflare + Clearnet (Triple Access)

Run your app on all three:

1. **Clearnet**: http://98.80.73.143:3000
2. **HTTPS**: https://yourdomain.com (via Cloudflare)
3. **Tor**: http://abcd1234efgh5678.onion

**Django .env:**

```env
ALLOWED_HOSTS=*,yourdomain.com,98.80.73.143,abcd1234efgh5678.onion
CSRF_TRUSTED_ORIGINS=http://*,https://*,http://abcd1234efgh5678.onion,https://yourdomain.com
```

All three work simultaneously!

---

## Performance Tips

### 1. Enable Tor Circuit Building Optimization

Edit `/etc/tor/torrc`:

```
# Faster circuit building
CircuitBuildTimeout 30
LearnCircuitBuildTimeout 1

# More circuits
NumEntryGuards 8
```

### 2. Use Tor with Nginx Caching

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=tor_cache:10m;

server {
    listen 127.0.0.1:3000;
    
    location / {
        proxy_cache tor_cache;
        proxy_pass http://127.0.0.1:3001;
    }
}
```

### 3. Enable Compression

In Django settings.py:

```python
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    # ... other middleware
]
```

---

## Monitoring Your Hidden Service

### Check Visitor Count

```bash
# Tor doesn't log visitors by default (privacy)
# But you can check Django logs
tail -f /home/ubuntu/teveclub/logs/access.log | grep "GET /"
```

### Monitor Tor Circuit Health

```bash
# Install tor monitoring tools
sudo apt install -y nyx

# Run monitor
sudo -u debian-tor nyx
```

### Uptime Monitoring

```bash
# Check if .onion is reachable
curl --socks5-hostname 127.0.0.1:9050 http://your-onion-address.onion
```

---

## Legal Considerations

✅ **Legal Uses:**
- Privacy-focused services
- Whistleblower platforms
- Censorship circumvention
- Anonymous forums

⚠️ **Responsibility:**
- You are responsible for content hosted
- Follow local laws
- Don't host illegal content
- Consider Terms of Service

---

## Backup Your Keys

**CRITICAL**: Backup your .onion keys or lose your address forever!

```bash
# Backup keys
sudo tar -czf teveclub-onion-keys-backup.tar.gz /var/lib/tor/teveclub/

# Store safely (offline USB, encrypted drive)
cp teveclub-onion-keys-backup.tar.gz /path/to/safe/location/

# Restore keys (if needed)
sudo systemctl stop tor
sudo tar -xzf teveclub-onion-keys-backup.tar.gz -C /
sudo chown -R debian-tor:debian-tor /var/lib/tor/teveclub/
sudo systemctl start tor
```

---

## Quick Start (5 minutes)

```bash
# 1. Install Tor
sudo apt install -y tor

# 2. Add to config
echo -e "\nHiddenServiceDir /var/lib/tor/teveclub/\nHiddenServicePort 80 127.0.0.1:3000" | sudo tee -a /etc/tor/torrc

# 3. Restart Tor
sudo systemctl restart tor

# 4. Get address
sudo cat /var/lib/tor/teveclub/hostname

# 5. Update Django .env with your .onion address
# 6. Restart: sudo systemctl restart teveclub
# 7. Test in Tor Browser!
```

Done! ✅

---

**Last Updated**: November 2025
