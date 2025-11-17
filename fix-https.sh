#!/bin/bash
# Quick fix script for HTTPS issues

echo "=========================================="
echo "Teveclub HTTPS Quick Fix"
echo "=========================================="
echo ""

# Get domain name from user
read -p "Enter your domain name (e.g., yourdomain.ddns.net): " DOMAIN

# Trim whitespace
DOMAIN=$(echo "$DOMAIN" | xargs)

if [ -z "$DOMAIN" ]; then
    echo "Error: Domain name is required"
    exit 1
fi

echo ""
echo "Fixing configuration for: $DOMAIN"
echo ""

# 1. Update Django .env file
echo "1. Updating Django .env file..."
cd /home/ubuntu/teveclub/django

cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=localhost,127.0.0.1,$DOMAIN
CSRF_TRUSTED_ORIGINS=http://$DOMAIN,https://$DOMAIN,http://localhost,http://127.0.0.1
EOF

echo "   ✓ .env file updated"
echo ""

# 2. Check and fix Nginx configuration
echo "2. Checking Nginx configuration..."
NGINX_CONF="/etc/nginx/sites-available/teveclub"

# Always recreate the configuration to ensure it's correct
echo "   Creating/updating Nginx configuration..."
sudo tee $NGINX_CONF > /dev/null << 'NGINXCONF'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;

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
NGINXCONF

echo "   Substituting domain name: $DOMAIN"
sudo sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" $NGINX_CONF

# Verify the configuration
echo "   Verifying Nginx configuration..."
if grep -q "server_name $DOMAIN" $NGINX_CONF; then
    echo "   ✓ Domain correctly set in config"
else
    echo "   ✗ Domain substitution failed!"
    echo "   Config file contents:"
    sudo cat $NGINX_CONF | head -10
    exit 1
fi

sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/teveclub
sudo rm -f /etc/nginx/sites-enabled/default

echo "   ✓ Nginx configuration updated"
echo ""

# 3. Test Nginx configuration
echo "3. Testing Nginx configuration..."
if sudo nginx -t; then
    echo "   ✓ Nginx configuration is valid"
else
    echo "   ✗ Nginx configuration has errors"
    exit 1
fi
echo ""

# 3.5. Check and fix firewall
echo "3.5. Checking firewall settings..."
if command -v ufw &> /dev/null; then
    echo "   Checking UFW status..."
    if sudo ufw status | grep -q "Status: active"; then
        echo "   UFW is active, checking port rules..."
        if ! sudo ufw status | grep -q "80.*ALLOW"; then
            echo "   Opening port 80..."
            sudo ufw allow 80/tcp
        else
            echo "   ✓ Port 80 is open"
        fi
        if ! sudo ufw status | grep -q "443.*ALLOW"; then
            echo "   Opening port 443..."
            sudo ufw allow 443/tcp
        else
            echo "   ✓ Port 443 is open"
        fi
    else
        echo "   UFW is not active"
    fi
else
    echo "   UFW not installed, checking iptables..."
    sudo iptables -L -n | grep -E "80|443" || echo "   Manual firewall check needed"
fi
echo ""

# 4. Update systemd service file
echo "4. Updating systemd service file..."
sudo tee /etc/systemd/system/teveclub.service > /dev/null << 'EOF'
[Unit]
Description=Teveclub Django Application
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/teveclub/django
Environment="PATH=/home/ubuntu/teveclub/venv/bin"
Environment="PYTHONPATH=/home/ubuntu/teveclub/django"
ExecStart=/home/ubuntu/teveclub/venv/bin/gunicorn teveclub_web.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 60 \
    --access-logfile /home/ubuntu/teveclub/logs/access.log \
    --error-logfile /home/ubuntu/teveclub/logs/error.log \
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF
echo "   ✓ Service file updated"
echo ""

# 5. Reload systemd and restart services
echo "5. Reloading systemd and restarting services..."
sudo systemctl daemon-reload
sudo systemctl restart teveclub
sleep 2
sudo systemctl restart nginx
echo "   ✓ Services restarted"
echo ""

# 5. Check service status
echo "5. Checking service status..."
if sudo systemctl is-active --quiet teveclub; then
    echo "   ✓ Teveclub service is running"
else
    echo "   ✗ Teveclub service failed to start"
    echo "   Check logs: sudo journalctl -u teveclub -n 50"
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    echo "   ✓ Nginx is running"
else
    echo "   ✗ Nginx failed to start"
    exit 1
fi
echo ""

# 6. Verify port 8000 is listening
echo "6. Verifying Gunicorn is listening on port 8000..."
sleep 2
if sudo ss -tlnp | grep :8000 > /dev/null; then
    echo "   ✓ Port 8000 is listening"
else
    echo "   ✗ Port 8000 is NOT listening"
    echo ""
    echo "   Checking service status..."
    sudo systemctl status teveclub --no-pager -l | tail -30
    echo ""
    echo "   Recent systemd journal logs:"
    sudo journalctl -u teveclub -n 30 --no-pager
    echo ""
    echo "   Troubleshooting steps:"
    echo "   1. Check if Django app is working: cd django && ../env/bin/python manage.py check"
    echo "   2. Check logs: tail -50 /home/ubuntu/teveclub/logs/error.log"
    echo "   3. Check service logs: sudo journalctl -u teveclub -n 100"
    echo "   4. Try manual start: cd django && ../env/bin/gunicorn teveclub_web.wsgi:application --bind 0.0.0.0:8000"
    exit 1
fi
echo ""

# 7. Test local connections
echo "7. Testing connections..."

# Test Gunicorn directly on port 8000
echo "   Testing Gunicorn on port 8000..."
GUNICORN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000 2>/dev/null || echo "000")
if [ "$GUNICORN_STATUS" = "200" ] || [ "$GUNICORN_STATUS" = "302" ] || [ "$GUNICORN_STATUS" = "301" ]; then
    echo "   ✓ Gunicorn is responding (HTTP $GUNICORN_STATUS)"
else
    echo "   ✗ Gunicorn is NOT responding properly (HTTP $GUNICORN_STATUS)"
    echo "   This means Gunicorn is running but Django has issues"
    echo "   Check Django settings and database"
fi

# Test Nginx proxy on port 80
echo "   Testing Nginx proxy on port 80..."
NGINX_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1 2>/dev/null || echo "000")
if [ "$NGINX_STATUS" = "200" ] || [ "$NGINX_STATUS" = "302" ] || [ "$NGINX_STATUS" = "301" ]; then
    echo "   ✓ Nginx proxy is working (HTTP $NGINX_STATUS)"
else
    echo "   ✗ Nginx proxy is NOT working (HTTP $NGINX_STATUS)"
    echo "   Check Nginx configuration and logs"
fi

# Test external domain
echo "   Testing external domain..."
DOMAIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
if [ "$DOMAIN_STATUS" = "200" ] || [ "$DOMAIN_STATUS" = "302" ] || [ "$DOMAIN_STATUS" = "301" ]; then
    echo "   ✓ Domain $DOMAIN is accessible (HTTP $DOMAIN_STATUS)"
elif [ "$DOMAIN_STATUS" = "000" ]; then
    echo "   ✗ Cannot reach $DOMAIN externally"
    echo "   This means the server is NOT accessible from the internet"
    echo ""
    echo "   Checking firewall and ports..."
    echo "   Port 80 status:"
    sudo ufw status | grep 80 || echo "   UFW may not be enabled"
    echo "   Port 443 status:"
    sudo ufw status | grep 443 || echo "   UFW may not be enabled"
    echo ""
    echo "   Checking if Nginx is listening on all interfaces:"
    sudo ss -tlnp | grep -E ':(80|443)' || echo "   Nginx not listening on expected ports"
    echo ""
    echo "   ACTION REQUIRED:"
    echo "   1. Check firewall: sudo ufw allow 80/tcp && sudo ufw allow 443/tcp"
    echo "   2. Check AWS Security Group: Allow inbound TCP 80 and 443 from 0.0.0.0/0"
    echo "   3. Check DNS: nslookup $DOMAIN (should point to this server's public IP)"
    echo "   4. This server's public IP: curl -s ifconfig.me"
else
    echo "   ⚠ Domain returned HTTP $DOMAIN_STATUS"
fi
echo ""

# 8. Check if SSL certificate exists
echo "8. Checking SSL certificate..."
if sudo certbot certificates 2>&1 | grep -q "$DOMAIN"; then
    echo "   ✓ SSL certificate exists for $DOMAIN"
else
    echo "   ⚠ No SSL certificate found for $DOMAIN"
    echo ""
    read -p "Do you want to obtain SSL certificate now? (y/n): " INSTALL_SSL
    if [ "$INSTALL_SSL" = "y" ] || [ "$INSTALL_SSL" = "Y" ]; then
        echo "   Installing SSL certificate..."
        sudo certbot --nginx -d $DOMAIN
    fi
fi
echo ""

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Your site is accessible at:"
echo "  HTTP:  http://$DOMAIN (port 80)"
echo "  HTTPS: https://$DOMAIN (port 443, if SSL installed)"
echo ""
echo "Note: Gunicorn runs on port 8000 internally (localhost only)"
echo "      Nginx proxies requests from port 80/443 to Gunicorn on port 8000"
echo ""
echo "IMPORTANT: Make sure settings.py has these lines to prevent redirect loops:"
echo "  SECURE_SSL_REDIRECT = False"
echo "  SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')"
echo "  USE_X_FORWARDED_HOST = True"
echo "  USE_X_FORWARDED_PORT = True"
echo ""
echo "If you still have issues:"
echo "1. Check Gunicorn logs: tail -50 /home/ubuntu/teveclub/logs/error.log"
echo "2. Check Nginx logs: sudo tail -50 /var/log/nginx/error.log"
echo "3. Check service status: sudo systemctl status teveclub nginx"
echo "4. Run diagnostic: ./diagnose.sh"
echo "5. Clear browser cookies for $DOMAIN"
echo ""
