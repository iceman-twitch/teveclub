# Port Configuration Guide

## How Ports Work with Nginx + SSL

### Port Overview

```
Internet (Users)
    ↓
Port 80 (HTTP) ──────→ Nginx ──────→ Port 8000 (Gunicorn - Internal)
Port 443 (HTTPS) ─────→ Nginx ──────→ Port 8000 (Gunicorn - Internal)
```

### Port Roles

| Port | Service | Access | Purpose |
|------|---------|--------|---------|
| **80** | Nginx | **Public** | Standard HTTP (redirects to HTTPS with SSL) |
| **443** | Nginx | **Public** | Standard HTTPS with SSL certificate |
| **8000** | Gunicorn | **Internal Only** | Django application (not exposed to internet) |

### Why This Setup?

1. **Port 80/443** - Standard web ports that browsers use by default
   - Users visit: `http://yourdomain.com` (port 80)
   - Or: `https://yourdomain.com` (port 443)
   - No need to type `:8000` in URL

2. **Port 8000** - Internal application server
   - Gunicorn runs Django on `127.0.0.1:8000` (localhost only)
   - NOT accessible from internet directly
   - Only Nginx can connect to it

3. **Nginx acts as reverse proxy**
   - Receives requests on port 80/443
   - Handles SSL/TLS encryption
   - Forwards to Gunicorn on port 8000
   - Returns response to user

### AWS Security Group Configuration

**Correct Setup:**

| Type | Port | Source | Purpose |
|------|------|--------|---------|
| HTTP | 80 | 0.0.0.0/0 | Allow public HTTP access |
| HTTPS | 443 | 0.0.0.0/0 | Allow public HTTPS access |
| SSH | 22 | Your IP | Remote access |

**DO NOT open port 8000 to 0.0.0.0/0** - It should only be accessible from localhost (127.0.0.1)

### URLs Users Access

✅ **Correct:**
- `http://yourdomain.com` (port 80)
- `https://yourdomain.com` (port 443)

❌ **Wrong:**
- `http://yourdomain.com:8000` (exposes internal port)

### Configuration Files

**Gunicorn binds to localhost only:**
```bash
gunicorn app.wsgi:application --bind 127.0.0.1:8000
```
This means only connections from the same server can reach Gunicorn.

**Nginx proxies to Gunicorn:**
```nginx
server {
    listen 80;  # Public HTTP
    listen 443 ssl;  # Public HTTPS
    
    location / {
        proxy_pass http://127.0.0.1:8000;  # Forward to Gunicorn
    }
}
```

### Testing Ports

```bash
# Check what's listening on each port
sudo netstat -tlnp | grep -E ':(80|443|8000)'

# Port 80 should show: nginx
# Port 443 should show: nginx (if SSL configured)
# Port 8000 should show: gunicorn (listening on 127.0.0.1 only)
```

### Common Mistakes

❌ **Binding Gunicorn to 0.0.0.0:8000**
```bash
gunicorn app.wsgi:application --bind 0.0.0.0:8000  # DON'T DO THIS
```
This exposes port 8000 to the internet.

✅ **Bind to localhost only**
```bash
gunicorn app.wsgi:application --bind 127.0.0.1:8000  # CORRECT
```

### When You Need Port 8000

**Only for local testing WITHOUT Nginx:**
```bash
# Development mode - test directly
python manage.py runserver 0.0.0.0:8000
# Visit: http://your-ip:8000
```

**Production with Nginx - users NEVER see port 8000:**
```bash
# Gunicorn on localhost only
gunicorn app.wsgi:application --bind 127.0.0.1:8000
# Users visit: http://yourdomain.com (port 80/443)
```

## Summary

- **Users access**: Port 80 (HTTP) or 443 (HTTPS)
- **Nginx handles**: SSL, caching, static files, proxying
- **Gunicorn runs**: On port 8000 (internal only)
- **Benefits**: Standard ports, no :8000 in URLs, better security
