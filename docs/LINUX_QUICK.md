# Teveclub Django Web - Complete Linux Deployment Guide

This guide walks you through deploying the Teveclub Django web application from scratch on Ubuntu/Debian Linux with HTTPS support.

## Prerequisites

- Ubuntu 20.04+ or Debian 11+ server
- Root or sudo access
- Domain name pointed to your server's IP address
- Ports 80 and 443 open in firewall/security groups

## Quick Automated Setup

For automated deployment, use the deployment script:

```bash
cd /home/ubuntu
git clone https://github.com/iceman-twitch/teveclub.git
cd teveclub
chmod +x deploy.sh
./deploy.sh
```

The script will prompt for your domain name and handle everything automatically.

## Manual Step-by-Step Setup

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx
```

### 2. Clone the Repository

```bash
cd /home/ubuntu
git clone https://github.com/iceman-twitch/teveclub.git
cd teveclub
```

### 3. Setup Python Virtual Environment

```bash
chmod +x env.sh
./env.sh
```

This creates a virtual environment in `venv/` and installs all Python dependencies.

### 4. Install Additional Dependencies

```bash
source venv/bin/activate
pip install whitenoise gunicorn python-dotenv
deactivate
```

### 5. Configure Django Environment

Create the `.env` file with your domain:

```bash
cd django
cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CSRF_TRUSTED_ORIGINS=http://yourdomain.com,https://yourdomain.com,http://localhost,http://127.0.0.1
EOF
```

Replace `yourdomain.com` with your actual domain.

### 6. Setup Django Database and Static Files

```bash
../venv/bin/python manage.py migrate
../venv/bin/python manage.py collectstatic --noinput
cd ..
```

### 7. Create Logs Directory

```bash
mkdir -p logs
touch logs/access.log logs/error.log
```

### 8. Fix Directory Permissions

**Critical**: Nginx needs to access static files. Set proper permissions:

```bash
sudo chmod 755 /home/ubuntu
sudo chmod 755 /home/ubuntu/teveclub
sudo chmod 755 /home/ubuntu/teveclub/django
sudo chmod -R 755 /home/ubuntu/teveclub/django/staticfiles/
sudo chown -R ubuntu:ubuntu /home/ubuntu/teveclub
```

### 9. Setup Systemd Service

The service file configures Gunicorn to run on port 8000:

```bash
sudo cp teveclub.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable teveclub
sudo systemctl start teveclub
sudo systemctl status teveclub
```

Verify Gunicorn is running:
```bash
sudo ss -tlnp | grep :8000
```

You should see Gunicorn listening on port 8000.

### 10. Configure Nginx

Create Nginx configuration (replace `yourdomain.com`):

```bash
sudo tee /etc/nginx/sites-available/teveclub > /dev/null << 'EOF'
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /home/ubuntu/teveclub/django/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    access_log /var/log/nginx/teveclub_access.log;
    error_log /var/log/nginx/teveclub_error.log;
}
EOF

# Replace yourdomain.com with your actual domain
sudo sed -i 's/yourdomain.com/YOUR_ACTUAL_DOMAIN/g' /etc/nginx/sites-available/teveclub

# Enable the site
sudo ln -sf /etc/nginx/sites-available/teveclub /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### 11. Test HTTP Access

```bash
curl -I http://yourdomain.com
```

You should see `HTTP/1.1 200 OK`. If you get 502 Bad Gateway, check:
- Gunicorn is running: `sudo systemctl status teveclub`
- Port 8000 is listening: `sudo ss -tlnp | grep :8000`
- Logs: `sudo journalctl -u teveclub -n 50`

### 12. Setup HTTPS with Let's Encrypt

```bash
sudo certbot --nginx -d yourdomain.com
```

Follow the prompts:
1. Enter your email address
2. Agree to Terms of Service
3. Choose whether to redirect HTTP to HTTPS (recommended: Yes)

Certbot will:
- Obtain SSL certificate
- Configure Nginx for HTTPS
- Setup automatic renewal

### 13. Verify HTTPS

```bash
curl -I https://yourdomain.com
```

You should see `HTTP/2 200` with SSL information.

## Architecture Overview

```
Internet (port 80/443)
    ↓
Nginx (reverse proxy)
    ↓
Gunicorn (port 8000, localhost only)
    ↓
Django Application
```

**Key Points:**
- **Gunicorn** runs on port 8000 (localhost only, not accessible externally)
- **Nginx** handles ports 80 (HTTP) and 443 (HTTPS)
- Nginx proxies all requests to Gunicorn
- Static files served directly by Nginx (faster)

## Troubleshooting

### Service Won't Start

Check logs:
```bash
sudo journalctl -u teveclub -n 50 --no-pager
tail -50 /home/ubuntu/teveclub/logs/error.log
```

Test Django manually:
```bash
cd /home/ubuntu/teveclub/django
../venv/bin/python manage.py check
```

### 502 Bad Gateway

Gunicorn not running or not on port 8000:
```bash
sudo systemctl restart teveclub
sudo ss -tlnp | grep :8000
```

### Static Files 403 Forbidden

Permission issues:
```bash
sudo chmod 755 /home/ubuntu
sudo chmod 755 /home/ubuntu/teveclub
sudo chmod 755 /home/ubuntu/teveclub/django
sudo chmod -R 755 /home/ubuntu/teveclub/django/staticfiles/
sudo systemctl restart nginx
```

### Redirect Loop (ERR_TOO_MANY_REDIRECTS)

Check Django settings.py has:
```python
SECURE_SSL_REDIRECT = False  # Let Nginx handle HTTPS redirect
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
```

### Port 8000 Already in Use

Kill the process:
```bash
sudo lsof -ti:8000 | xargs sudo kill -9
sudo systemctl restart teveclub
```

## Maintenance Commands

### View Logs
```bash
# Application logs
tail -f /home/ubuntu/teveclub/logs/error.log

# Service logs
sudo journalctl -u teveclub -f

# Nginx logs
sudo tail -f /var/log/nginx/teveclub_error.log
```

### Restart Services
```bash
sudo systemctl restart teveclub
sudo systemctl restart nginx
```

### Update Application
```bash
cd /home/ubuntu/teveclub
git pull
source venv/bin/activate
pip install -r requirements.txt
cd django
python manage.py migrate
python manage.py collectstatic --noinput
cd ..
sudo systemctl restart teveclub
```

### Renew SSL Certificate (manual)
```bash
sudo certbot renew
sudo systemctl restart nginx
```

Note: Certbot sets up automatic renewal, so manual renewal is rarely needed.

## Security Checklist

- [ ] Strong SECRET_KEY generated
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS restricted to your domain
- [ ] Firewall (UFW or Security Groups) configured
- [ ] SSL certificate installed and auto-renewal working
- [ ] Regular system updates: `sudo apt update && sudo apt upgrade`
- [ ] Application updates from git repository

## Support

For issues or questions, check the logs first:
```bash
sudo journalctl -u teveclub -n 100
tail -100 /home/ubuntu/teveclub/logs/error.log
sudo tail -100 /var/log/nginx/error.log
```