#!/bin/bash
# Diagnostic script for SSL/HTTPS issues

echo "=========================================="
echo "Teveclub HTTPS Diagnostic Tool"
echo "=========================================="
echo ""

# 1. Check if Gunicorn is running
echo "1. Checking Gunicorn status..."
if sudo systemctl is-active --quiet teveclub; then
    echo "   ✓ Service is running"
    sudo systemctl status teveclub --no-pager | head -10
else
    echo "   ✗ Service is NOT running"
    echo "   Attempting to start..."
    sudo systemctl start teveclub
    sleep 2
    sudo systemctl status teveclub --no-pager | head -10
fi
echo ""

# 2. Check if port 8000 is listening
echo "2. Checking if port 8000 is listening..."
if sudo ss -tlnp | grep :8000 > /dev/null; then
    echo "   ✓ Port 8000 is listening"
    sudo ss -tlnp | grep :8000
else
    echo "   ✗ Port 8000 is NOT listening"
    echo "   Checking systemd journal logs..."
    sudo journalctl -u teveclub -n 20 --no-pager | sed 's/^/   /'
fi
echo ""

# 3. Test local connection
echo "3. Testing local connection to Gunicorn..."
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000 > /tmp/curl_status.txt 2>&1; then
    STATUS=$(cat /tmp/curl_status.txt)
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ] || [ "$STATUS" = "301" ]; then
        echo "   ✓ Gunicorn is responding (HTTP $STATUS)"
    else
        echo "   ⚠ Gunicorn returned HTTP $STATUS"
    fi
else
    echo "   ✗ Cannot connect to Gunicorn on port 8000"
fi
rm -f /tmp/curl_status.txt
echo ""

# 4. Check Nginx status
echo "4. Checking Nginx status..."
if sudo systemctl is-active --quiet nginx; then
    echo "   ✓ Nginx is running"
    sudo systemctl status nginx --no-pager | head -5
else
    echo "   ✗ Nginx is NOT running"
    echo "   Attempting to start..."
    sudo systemctl start nginx
    sleep 1
fi
echo ""

# 5. Check Nginx configuration
echo "5. Checking Nginx configuration..."
if sudo nginx -t 2>&1 | grep -q "successful"; then
    echo "   ✓ Nginx configuration is valid"
else
    echo "   ✗ Nginx configuration has errors:"
    sudo nginx -t
fi
echo ""

# 6. Check SSL certificate
echo "6. Checking SSL certificate..."
if sudo certbot certificates 2>&1 | grep -q "Certificate Name"; then
    echo "   ✓ SSL certificate found:"
    sudo certbot certificates 2>&1 | grep -A 5 "Certificate Name"
else
    echo "   ✗ No SSL certificate found"
    echo "   Run: sudo certbot --nginx -d yourdomain.com"
fi
echo ""

# 7. Check Django .env file
echo "7. Checking Django configuration..."
if [ -f /home/ubuntu/teveclub/django/.env ]; then
    echo "   ✓ .env file exists"
    echo "   Current settings:"
    grep -E "^(DEBUG|ALLOWED_HOSTS|CSRF_TRUSTED_ORIGINS)" /home/ubuntu/teveclub/django/.env | sed 's/^/   /'
else
    echo "   ✗ .env file NOT found"
fi
echo ""

# 8. Check recent Gunicorn error logs
echo "8. Recent Gunicorn errors (last 20 lines):"
if [ -f /home/ubuntu/teveclub/logs/error.log ]; then
    tail -20 /home/ubuntu/teveclub/logs/error.log | sed 's/^/   /'
else
    echo "   No error log found"
fi
echo ""

# 9. Check Nginx error logs
echo "9. Recent Nginx errors (last 20 lines):"
if [ -f /var/log/nginx/error.log ]; then
    sudo tail -20 /var/log/nginx/error.log | sed 's/^/   /'
else
    echo "   No Nginx error log found"
fi
echo ""

# 10. Port status summary
echo "========================================="
echo "Port Status Summary:"
echo "========================================="
echo "Port 80 (HTTP) - Public:"
sudo netstat -tlnp | grep :80 || echo "   Not listening"
echo ""
echo "Port 443 (HTTPS) - Public:"
sudo netstat -tlnp | grep :443 || echo "   Not listening"
echo ""
echo "Port 8000 (Gunicorn) - Internal Only:"
sudo netstat -tlnp | grep :8000 || echo "   Not listening"
echo ""

echo "=========================================="
echo "Common Issues & Solutions:"
echo "=========================================="
echo "1. If Gunicorn not running:"
echo "   sudo systemctl restart teveclub"
echo ""
echo "2. If Nginx not running:"
echo "   sudo systemctl restart nginx"
echo ""
echo "3. If SSL not working:"
echo "   - Check ALLOWED_HOSTS includes your domain"
echo "   - Check CSRF_TRUSTED_ORIGINS includes https://yourdomain"
echo "   - Verify certbot certificate is valid"
echo ""
echo "4. If still not working, check:"
echo "   sudo journalctl -u teveclub -n 50"
echo "   sudo journalctl -u nginx -n 50"
echo "=========================================="
