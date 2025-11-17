#!/bin/bash
# Quick fix script for HTTPS issues

echo "=========================================="
echo "Teveclub HTTPS Quick Fix"
echo "=========================================="
echo ""

# Get domain name from user
read -p "Enter your domain name (e.g., yourdomain.ddns.net): " DOMAIN

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
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,http://$DOMAIN
EOF

echo "   ✓ .env file updated"
echo ""

# 2. Check and fix Nginx configuration
echo "2. Checking Nginx configuration..."
NGINX_CONF="/etc/nginx/sites-available/teveclub"

if [ ! -f "$NGINX_CONF" ]; then
    echo "   Creating Nginx configuration..."
    sudo tee $NGINX_CONF > /dev/null << 'EOF'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;

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
    sudo sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" $NGINX_CONF
    sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
fi

# Update server_name if file exists
sudo sed -i "s/server_name .*/server_name $DOMAIN;/g" $NGINX_CONF

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

# 4. Restart services
echo "4. Restarting services..."
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
if sudo netstat -tlnp | grep :8000 > /dev/null; then
    echo "   ✓ Port 8000 is listening"
else
    echo "   ✗ Port 8000 is NOT listening"
    echo "   Check Gunicorn logs: tail -50 /home/ubuntu/teveclub/logs/error.log"
    exit 1
fi
echo ""

# 7. Test local connection
echo "7. Testing local connection..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000)
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "301" ]; then
    echo "   ✓ Gunicorn is responding (HTTP $HTTP_STATUS)"
else
    echo "   ⚠ Gunicorn returned HTTP $HTTP_STATUS"
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
echo "      Nginx proxies requests from port 80/443 to Gunicorn"
echo ""
echo "If you still have issues:"
echo "1. Check Gunicorn logs: tail -50 /home/ubuntu/teveclub/logs/error.log"
echo "2. Check Nginx logs: sudo tail -50 /var/log/nginx/error.log"
echo "3. Check service status: sudo systemctl status teveclub nginx"
echo "4. Run diagnostic: ./diagnose.sh"
echo ""
