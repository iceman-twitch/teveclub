# HTTPS Setup Guide for AWS EC2

Complete guide to enable HTTPS with SSL certificate for your Teveclub application on AWS.

---

## Free Domain Options

### No-IP (Free Dynamic DNS Hostname)

**Best for:** Quick setup without buying a domain

1. **Sign up**: https://www.noip.com (free account)
2. **Create Hostname**:
   - Dynamic DNS → No-IP Hostnames → Create Hostname
   - Hostname: `teveclub`
   - Domain: `.ddns.net`, `.hopto.org`, or other options
   - IPv4 Address: `YOUR_EC2_PUBLIC_IP` (your EC2 IP)
3. **Result**: `teveclub.ddns.net` (or your chosen domain)

**Important**: Free accounts require monthly email confirmation or hostname expires.

**Update Django Settings**:
```bash
cd /home/ubuntu/teveclub/django
nano .env
```

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=*,your-noip-hostname.ddns.net,YOUR_EC2_PUBLIC_IP
CSRF_TRUSTED_ORIGINS=http://your-noip-hostname.ddns.net,http://YOUR_EC2_PUBLIC_IP
```

**Restart**: `sudo systemctl restart teveclub`

**Access**: `http://your-noip-hostname.ddns.net`

**⚠️ Important Note**: No-IP subdomains (`.ddns.net`, `.hopto.org`, etc.) **cannot be added to Cloudflare** because you don't own the root domain. See options below:

#### Option A: Use Let's Encrypt with No-IP (Recommended)

Get free HTTPS directly without Cloudflare:

```bash
# Install Nginx and Certbot
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# Configure Nginx for your No-IP hostname
sudo tee /etc/nginx/sites-available/teveclub > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-noip-hostname.ddns.net;

    location /static/ {
        alias /home/ubuntu/teveclub/django/staticfiles/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/teveclub /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Get free SSL certificate
sudo certbot --nginx -d your-noip-hostname.ddns.net

# Update Django settings
cd /home/ubuntu/teveclub/django
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-noip-hostname.ddns.net
CSRF_TRUSTED_ORIGINS=https://your-noip-hostname.ddns.net
EOF

# Restart application
sudo systemctl restart teveclub
```

**Result**: Visit `https://your-noip-hostname.ddns.net` (port 80/443) with free SSL! ✅

#### Option B: Get a Real Domain for Cloudflare

If you want Cloudflare features (DDoS protection, CDN):

1. Get free `.tk` domain: https://www.freenom.com
2. Register `teveclub.tk` (or similar)
3. Add to Cloudflare (see Option 1 below)
4. Get free SSL through Cloudflare

### Other Free Options

- **DuckDNS**: https://www.duckdns.org - Easy, no email confirmation needed
- **Freenom**: https://www.freenom.com - Free `.tk`, `.ml`, `.ga` domains (works with Cloudflare)
- **Afraid.org**: https://freedns.afraid.org - Multiple free subdomains

---

## Option 1: Using Cloudflare (Easiest - Free SSL)

### Prerequisites
- Domain name (you own or can configure) - can use Freenom free domains
- Cloudflare account (free)

### Steps

1. **Add Domain to Cloudflare**
   - Go to https://cloudflare.com
   - Click "Add a Site"
   - Enter your domain name
   - Choose Free plan

2. **Update Nameservers**
   - Cloudflare will show you 2 nameservers
   - Go to your domain registrar (GoDaddy, Namecheap, etc.)
   - Replace existing nameservers with Cloudflare's nameservers
   - Wait 5-60 minutes for DNS propagation

3. **Add DNS Record**
   - In Cloudflare Dashboard → DNS → Records
   - Add A record:
     - Type: `A`
     - Name: `@` (or subdomain like `app`)
     - IPv4 address: `YOUR_EC2_PUBLIC_IP` (your EC2 IP)
     - Proxy status: **Proxied** (orange cloud)
   - Click Save

4. **Configure SSL/TLS**
   - Go to SSL/TLS → Overview
   - Select **Full** or **Flexible** mode
   - **Flexible**: Cloudflare to user (HTTPS), Cloudflare to server (HTTP)
   - **Full**: Requires self-signed cert on server (more secure)

5. **Update Django Settings**
   ```bash
   # On your server
   cd /home/ubuntu/teveclub/django
   nano .env
   ```
   
   Update:
   ```env
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_EC2_PUBLIC_IP
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

6. **Restart Application**
   ```bash
   sudo systemctl restart teveclub
   ```

7. **Test**
   - Visit `https://yourdomain.com`
   - Should see valid SSL certificate
   - No browser warnings

### Benefits of Cloudflare
- ✅ Free SSL certificate (automatic renewal)
- ✅ DDoS protection
- ✅ CDN for faster loading
- ✅ Hides your real server IP
- ✅ No server configuration needed

---

## Option 2: Let's Encrypt with Nginx (Free, Self-Hosted)

### Prerequisites
- Domain name pointing to your EC2 IP
- Port 80 and 443 open in AWS Security Group

### Step 1: Install Nginx

```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 2: Configure Nginx

```bash
sudo tee /etc/nginx/sites-available/teveclub > /dev/null << 'EOF'
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 100M;

    location /static/ {
        alias /home/ubuntu/teveclub/django/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/ubuntu/teveclub/django/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/teveclub /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Step 3: Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Step 4: Get SSL Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Follow prompts:**
1. Enter email address
2. Agree to Terms of Service
3. Choose whether to share email (optional)
4. Select option 2: **Redirect HTTP to HTTPS** (recommended)

### Step 5: Update Django Settings

```bash
cd /home/ubuntu/teveclub/django
nano .env
```

Update:
```env
DEBUG=False
SECRET_KEY=5bpkrvg%*t1q**uo=g=(^-12!)&6h$uc^&2ei_z&4e1@l2y_96
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Step 6: Restart Services

```bash
sudo systemctl restart teveclub
sudo systemctl restart nginx
```

### Step 7: Test Auto-Renewal

```bash
sudo certbot renew --dry-run
```

If successful, certificates will auto-renew every 60 days.

### Step 8: Test HTTPS

Visit `https://yourdomain.com` (port 80/443)

### Benefits of Let's Encrypt
- ✅ Free SSL certificate
- ✅ Auto-renewal
- ✅ Full control over server
- ✅ Standard port 443
- ❌ Requires Nginx setup
- ❌ More complex configuration

---

## Option 3: AWS Certificate Manager + Load Balancer

### Prerequisites
- Domain in Route 53 or ability to validate domain
- Application Load Balancer (costs ~$16/month)

### Steps

1. **Request Certificate**
   - AWS Console → Certificate Manager
   - Request public certificate
   - Enter domain name: `yourdomain.com`, `*.yourdomain.com`
   - DNS validation (recommended)
   - Add CNAME records to your DNS

2. **Create Application Load Balancer**
   - EC2 Console → Load Balancers → Create
   - Type: Application Load Balancer
   - Scheme: Internet-facing
   - Listeners: HTTP (80), HTTPS (443)
   - Select your VPC and subnets (at least 2)

3. **Configure Target Group**
   - Target type: Instances
   - Protocol: HTTP
   - Port: 8000
   - Health check path: `/`
   - Register your EC2 instance

4. **Add SSL Certificate**
   - Listener: HTTPS:443
   - Default action: Forward to target group
   - Security policy: ELBSecurityPolicy-TLS13-1-2-2021-06
   - Default SSL certificate: Select your ACM certificate

5. **Configure Security Groups**
   - Load Balancer SG: Allow 80, 443 from 0.0.0.0/0
   - EC2 Instance SG: Allow 8000 from Load Balancer SG only

6. **Update DNS**
   - Point your domain to Load Balancer DNS name (CNAME or A record alias)

### Benefits of AWS ALB
- ✅ Managed SSL certificates (auto-renewal)
- ✅ High availability (multi-AZ)
- ✅ AWS WAF integration
- ✅ Health checks and auto-scaling ready
- ❌ Costs money (~$16/month minimum)
- ❌ More complex setup

---

## Recommended Approach

**For Development/Testing:**
- Use Cloudflare (Option 1) - Easiest, free, instant

**For Production (Small Budget):**
- Use Let's Encrypt + Nginx (Option 2) - Free, professional

**For Production (Enterprise):**
- Use AWS ALB + ACM (Option 3) - Scalable, managed

---

## Troubleshooting

### Certificate Not Working

1. **Check DNS propagation:**
   ```bash
   nslookup yourdomain.com
   dig yourdomain.com
   ```

2. **Check AWS Security Group:**
   - Port 80 (HTTP): 0.0.0.0/0
   - Port 443 (HTTPS): 0.0.0.0/0

3. **Check Nginx status:**
   ```bash
   sudo systemctl status nginx
   sudo nginx -t
   ```

4. **Check certificate:**
   ```bash
   sudo certbot certificates
   ```

### Mixed Content Errors

Add to Django settings.py:
```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Application Port Still Accessible

If using Nginx, block direct access to application port:
```bash
# AWS Security Group: Remove application port from public access
# Allow application port only from 127.0.0.1 (localhost)
```

---

## Quick Setup - Cloudflare (5 minutes)

```bash
# 1. Add domain to Cloudflare (web interface)
# 2. Update nameservers at registrar
# 3. Add DNS A record: @ → YOUR_EC2_PUBLIC_IP (proxied)
# 4. SSL/TLS → Full mode

# 5. Update Django settings
cd /home/ubuntu/teveclub/django
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EOF

# 6. Restart
sudo systemctl restart teveclub

# 7. Visit https://yourdomain.com
```

Done! ✅

---

**Last Updated**: November 2025
