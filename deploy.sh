#!/bin/bash
# Automated deployment script for Teveclub Django Web Application
# This script sets up everything from scratch: dependencies, Django, Nginx, HTTPS

set -e  # Exit on any error

echo "=========================================="
echo "Teveclub Django Automated Deployment"
echo "=========================================="
echo ""
echo "This script will:"
echo "  1. Install system dependencies"
echo "  2. Setup Python virtual environment"
echo "  3. Configure Django application"
echo "  4. Setup Nginx reverse proxy"
echo "  5. Configure systemd service"
echo "  6. Fix all permissions"
echo "  7. Setup HTTPS with Let's Encrypt"
echo ""

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ]; then
    echo "⚠ Warning: This script is designed to run as the 'ubuntu' user."
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        exit 1
    fi
fi

# Get domain name
read -p "Enter your domain name (e.g., yourdomain.com): " DOMAIN
DOMAIN=$(echo "$DOMAIN" | xargs)  # Trim whitespace

if [ -z "$DOMAIN" ]; then
    echo "Error: Domain name is required"
    exit 1
fi

echo ""
echo "Deploying for domain: $DOMAIN"
echo ""
read -p "Press Enter to continue or Ctrl+C to abort..."

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "=========================================="
echo "Step 1: Installing System Dependencies"
echo "=========================================="
echo ""

if ! command -v nginx &> /dev/null; then
    echo "Installing Nginx..."
    sudo apt update
    sudo apt install -y nginx
else
    echo "✓ Nginx already installed"
fi

if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    sudo apt install -y certbot python3-certbot-nginx
else
    echo "✓ Certbot already installed"
fi

if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    sudo apt install -y python3 python3-pip python3-venv
else
    echo "✓ Python3 already installed"
fi

echo ""
echo "=========================================="
echo "Step 2: Setting Up Virtual Environment"
echo "=========================================="
echo ""

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install whitenoise gunicorn python-dotenv
deactivate
echo "✓ Python dependencies installed"

echo ""
echo "=========================================="
echo "Step 3: Configuring Django"
echo "=========================================="
echo ""

cd django

echo "Creating .env file..."
cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=localhost,127.0.0.1,$DOMAIN
CSRF_TRUSTED_ORIGINS=http://$DOMAIN,https://$DOMAIN,http://localhost,http://127.0.0.1
EOF
echo "✓ .env file created"

echo "Running Django migrations..."
../venv/bin/python manage.py migrate
echo "✓ Migrations completed"

echo "Collecting static files..."
../venv/bin/python manage.py collectstatic --noinput
echo "✓ Static files collected"

echo "Running Django check..."
../venv/bin/python manage.py check
echo "✓ Django configuration valid"

cd ..

echo ""
echo "=========================================="
echo "Step 4: Creating Logs Directory"
echo "=========================================="
echo ""

mkdir -p logs
touch logs/access.log logs/error.log
echo "✓ Logs directory created"

echo ""
echo "=========================================="
echo "Step 5: Fixing Permissions"
echo "=========================================="
echo ""

echo "Setting directory permissions..."
sudo chmod 755 /home/ubuntu
sudo chmod 755 "$SCRIPT_DIR"
sudo chmod 755 "$SCRIPT_DIR/django"
sudo chmod -R 755 "$SCRIPT_DIR/django/staticfiles/"
sudo chown -R ubuntu:ubuntu "$SCRIPT_DIR"
echo "✓ Permissions fixed"

echo ""
echo "=========================================="
echo "Step 6: Configuring Nginx"
echo "=========================================="
echo ""

echo "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/teveclub > /dev/null << 'NGINXCONF'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;

    location /static/ {
        alias SCRIPT_DIR_PLACEHOLDER/django/staticfiles/;
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

# Substitute domain and script directory
sudo sed -i "s|DOMAIN_PLACEHOLDER|$DOMAIN|g" /etc/nginx/sites-available/teveclub
sudo sed -i "s|SCRIPT_DIR_PLACEHOLDER|$SCRIPT_DIR|g" /etc/nginx/sites-available/teveclub

# Enable site
sudo ln -sf /etc/nginx/sites-available/teveclub /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo "Testing Nginx configuration..."
if sudo nginx -t; then
    echo "✓ Nginx configuration valid"
else
    echo "✗ Nginx configuration has errors"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 7: Setting Up Systemd Service"
echo "=========================================="
echo ""

echo "Creating systemd service file..."
sudo tee /etc/systemd/system/teveclub.service > /dev/null << EOF
[Unit]
Description=Teveclub Django Application
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$SCRIPT_DIR/django
Environment="PATH=$SCRIPT_DIR/venv/bin"
Environment="PYTHONPATH=$SCRIPT_DIR/django"
ExecStart=$SCRIPT_DIR/venv/bin/gunicorn teveclub_web.wsgi:application \\
    --bind 0.0.0.0:8000 \\
    --workers 3 \\
    --timeout 60 \\
    --access-logfile $SCRIPT_DIR/logs/access.log \\
    --error-logfile $SCRIPT_DIR/logs/error.log \\
    --log-level info
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling and starting teveclub service..."
sudo systemctl enable teveclub
sudo systemctl restart teveclub
sleep 3

if sudo systemctl is-active --quiet teveclub; then
    echo "✓ Teveclub service is running"
else
    echo "✗ Teveclub service failed to start"
    echo "Checking logs..."
    sudo journalctl -u teveclub -n 30 --no-pager
    exit 1
fi

echo "Restarting Nginx..."
sudo systemctl restart nginx

if sudo systemctl is-active --quiet nginx; then
    echo "✓ Nginx is running"
else
    echo "✗ Nginx failed to start"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 8: Verifying Deployment"
echo "=========================================="
echo ""

echo "Checking if Gunicorn is listening on port 8000..."
sleep 2
if sudo ss -tlnp | grep :8000 > /dev/null; then
    echo "✓ Port 8000 is listening"
else
    echo "✗ Port 8000 is NOT listening"
    echo "Service status:"
    sudo systemctl status teveclub --no-pager -l | tail -20
    exit 1
fi

echo "Testing Gunicorn response..."
GUNICORN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000 2>/dev/null || echo "000")
if [ "$GUNICORN_STATUS" = "200" ] || [ "$GUNICORN_STATUS" = "302" ] || [ "$GUNICORN_STATUS" = "301" ]; then
    echo "✓ Gunicorn is responding (HTTP $GUNICORN_STATUS)"
else
    echo "✗ Gunicorn is NOT responding properly (HTTP $GUNICORN_STATUS)"
fi

echo "Testing Nginx proxy..."
NGINX_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1 2>/dev/null || echo "000")
if [ "$NGINX_STATUS" = "200" ] || [ "$NGINX_STATUS" = "302" ] || [ "$NGINX_STATUS" = "301" ]; then
    echo "✓ Nginx proxy is working (HTTP $NGINX_STATUS)"
else
    echo "✗ Nginx proxy is NOT working (HTTP $NGINX_STATUS)"
fi

echo "Testing external domain access..."
DOMAIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null || echo "000")
if [ "$DOMAIN_STATUS" = "200" ] || [ "$DOMAIN_STATUS" = "302" ] || [ "$DOMAIN_STATUS" = "301" ]; then
    echo "✓ Domain $DOMAIN is accessible (HTTP $DOMAIN_STATUS)"
elif [ "$DOMAIN_STATUS" = "000" ]; then
    echo "⚠ Cannot reach $DOMAIN externally"
    echo "  This may be a DNS or firewall issue"
    echo "  - Check DNS: nslookup $DOMAIN"
    echo "  - Check firewall/security groups: ports 80 and 443 must be open"
else
    echo "⚠ Domain returned HTTP $DOMAIN_STATUS"
fi

echo ""
echo "=========================================="
echo "Step 9: Setting Up HTTPS"
echo "=========================================="
echo ""

if sudo certbot certificates 2>&1 | grep -q "$DOMAIN"; then
    echo "SSL certificate already exists for $DOMAIN"
    read -p "Do you want to renew it? (y/n): " RENEW_SSL
    if [ "$RENEW_SSL" = "y" ] || [ "$RENEW_SSL" = "Y" ]; then
        echo "Renewing certificate..."
        sudo certbot --nginx -d $DOMAIN --force-renewal
    fi
else
    echo "No SSL certificate found for $DOMAIN"
    read -p "Do you want to obtain SSL certificate now? (y/n): " INSTALL_SSL
    if [ "$INSTALL_SSL" = "y" ] || [ "$INSTALL_SSL" = "Y" ]; then
        echo ""
        echo "Installing SSL certificate..."
        echo "Follow the prompts from Certbot:"
        echo "  1. Enter your email address"
        echo "  2. Agree to Terms of Service (Y)"
        echo "  3. Choose whether to redirect HTTP to HTTPS (recommended: 2 for redirect)"
        echo ""
        sudo certbot --nginx -d $DOMAIN
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✓ SSL certificate installed successfully!"
        else
            echo ""
            echo "⚠ SSL certificate installation failed"
            echo "  You can try again later with: sudo certbot --nginx -d $DOMAIN"
        fi
    else
        echo "Skipping SSL certificate installation"
        echo "You can install it later with: sudo certbot --nginx -d $DOMAIN"
    fi
fi

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Your Teveclub Django application is now running!"
echo ""
echo "Access your site at:"
echo "  HTTP:  http://$DOMAIN"
if sudo certbot certificates 2>&1 | grep -q "$DOMAIN"; then
    echo "  HTTPS: https://$DOMAIN"
fi
echo ""
echo "Application Details:"
echo "  - Gunicorn runs on port 8000 (localhost only)"
echo "  - Nginx proxies requests from port 80/443 to Gunicorn"
echo "  - Static files served by Nginx from: $SCRIPT_DIR/django/staticfiles/"
echo ""
echo "Useful Commands:"
echo "  - View logs: tail -f $SCRIPT_DIR/logs/error.log"
echo "  - Service status: sudo systemctl status teveclub"
echo "  - Restart app: sudo systemctl restart teveclub"
echo "  - Restart Nginx: sudo systemctl restart nginx"
echo "  - View service logs: sudo journalctl -u teveclub -f"
echo ""
echo "Troubleshooting:"
echo "  - If site not accessible, check firewall/security groups"
echo "  - If static files not loading, check permissions"
echo "  - Run: sudo chmod 755 /home/ubuntu"
echo "  - Full guide: $SCRIPT_DIR/docs/LINUX_QUICK.md"
echo ""
