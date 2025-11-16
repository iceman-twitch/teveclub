# Teveclub Django - AWS Linux Deployment Guide

Complete guide for deploying the Teveclub Django application on Amazon AWS EC2 with Amazon Linux 2023.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [EC2 Instance Setup](#ec2-instance-setup)
3. [Initial Server Configuration](#initial-server-configuration)
4. [Application Deployment](#application-deployment)
5. [Systemd Service Setup](#systemd-service-setup)
6. [Nginx Configuration](#nginx-configuration)
7. [SSL/HTTPS Setup (Optional)](#ssl-https-setup)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- AWS Account
- SSH key pair for EC2 access
- Domain name (optional, but recommended)
- Basic knowledge of Linux command line

---

## EC2 Instance Setup

### 1. Launch EC2 Instance

1. Log in to AWS Console
2. Navigate to EC2 Dashboard
3. Click "Launch Instance"
4. Configure instance:
   - **Name**: `teveclub-server`
   - **AMI**: Ubuntu Server 22.04 LTS or Ubuntu Server 24.04 LTS
   - **Instance Type**: t2.micro (free tier) or t2.small (recommended)
   - **Key Pair**: Select or create a new key pair
   - **Network Settings**:
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere
     - Allow HTTPS (port 443) from anywhere (if using SSL)
   - **Storage**: 8-20 GB gp3 SSD

5. Launch the instance

### 2. Connect to Instance

```bash
# Make key file private
chmod 400 your-key.pem

# Connect via SSH (use 'ubuntu' for Ubuntu AMI)
ssh -i your-key.pem ubuntu@<your-instance-public-ip>
```

---

## Initial Server Configuration

### 1. Update System

```bash
# Update package list
sudo apt update

# Upgrade all packages
sudo apt upgrade -y

# Install system utilities
sudo apt install -y git wget curl vim
```

### 2. Install Python 3

```bash
# Install Python 3 and pip (Ubuntu 22.04 has Python 3.10, Ubuntu 24.04 has Python 3.12)
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verify installation
python3 --version
pip3 --version
```

### 3. Install Development Tools

```bash
# Install build tools
sudo apt install -y build-essential

# Install additional dependencies
sudo apt install -y libxml2-dev libxslt1-dev
```

---

## Application Deployment

### 1. Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/yourusername/teveclub.git
# OR upload files via SCP:
# scp -i your-key.pem -r teveclub ubuntu@<ip>:~/

cd teveclub
```

### 2. Run Setup Script

```bash
# Make scripts executable
chmod +x env.sh run.sh stop.sh restart.sh status.sh run_django.sh

# Run setup
./env.sh
```

### 3. Configure Environment Variables

```bash
# Create .env file in django directory
cd django
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=your-very-secret-key-change-this-in-production
ALLOWED_HOSTS=your-domain.com,<your-ec2-ip>
CSRF_TRUSTED_ORIGINS=http://your-domain.com,https://your-domain.com
EOF
```
```bash
# Create .env file in django directory
cd django
cat > .env << 'EOF'
DEBUG=False
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=http://*,https://*
EOF
```


**Important**: Generate a strong SECRET_KEY:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Run Migrations and Collect Static Files

```bash
# Activate virtual environment
source ~/teveclub/venv/bin/activate

# Navigate to Django directory
cd ~/teveclub/django

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (optional)
python manage.py createsuperuser
```

### 5. Test the Application

```bash
# Test development server
python manage.py runserver 0.0.0.0:3000

# Test in browser: http://<your-ec2-ip>:3000
# Press Ctrl+C to stop
```

### 6. Application Management Scripts

The application includes convenient management scripts:

```bash
# Start application in background
./run.sh

# Check application status
./status.sh

# Stop application
./stop.sh

# Restart application
./restart.sh
```

These scripts manage Gunicorn processes and handle PID files automatically.

---

## Systemd Service Setup

### 1. Install Gunicorn

```bash
source ~/teveclub/venv/bin/activate
pip install gunicorn
```

### 2. Copy Service File

```bash
# Copy service file to systemd
sudo cp ~/teveclub/teveclub.service /etc/systemd/system/

# Edit paths if needed
sudo vim /etc/systemd/system/teveclub.service
# Change User from 'ec2-user' to 'ubuntu' and update paths:
# User=ubuntu
# Group=ubuntu
# WorkingDirectory=/home/ubuntu/teveclub/django
# All paths: /home/ubuntu/teveclub/...
```

### 3. Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable teveclub

# Start the service
sudo systemctl start teveclub

# Check status
sudo systemctl status teveclub
```

### 4. Service Management Commands

```bash
# Start service
sudo systemctl start teveclub

# Stop service
sudo systemctl stop teveclub

# Restart service
sudo systemctl restart teveclub

# Check status
sudo systemctl status teveclub

# View logs
sudo journalctl -u teveclub -f
```

---

## Nginx Configuration

### 1. Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. Configure Nginx

```bash
# Copy nginx configuration
sudo cp ~/teveclub/nginx.conf /etc/nginx/conf.d/teveclub.conf

# Edit configuration
sudo vim /etc/nginx/conf.d/teveclub.conf
# Change 'your-domain.com' to your actual domain or EC2 IP

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 3. Configure Firewall (if enabled)

```bash
# Check firewall status (Ubuntu uses ufw)
sudo ufw status

# If firewall is active, allow HTTP/HTTPS
sudo ufw allow 'Nginx Full'
sudo ufw allow 3000/tcp
sudo ufw allow OpenSSH

# Enable firewall (if not already enabled)
# sudo ufw enable
```

---

## SSL/HTTPS Setup (Optional but Recommended)

### Using Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts and select option 2 (redirect HTTP to HTTPS)

# Test automatic renewal
sudo certbot renew --dry-run

# Renewal is automatic via cron/timer
```

---

## Monitoring and Maintenance

### 1. View Application Logs

```bash
# Gunicorn access logs
tail -f ~/teveclub/logs/access.log

# Gunicorn error logs
tail -f ~/teveclub/logs/error.log

# Nginx logs
sudo tail -f /var/log/nginx/teveclub_access.log
sudo tail -f /var/log/nginx/teveclub_error.log

# Systemd service logs
sudo journalctl -u teveclub -f
```

### 2. Update Application

**If using management scripts:**
```bash
cd ~/teveclub
git pull

# If you have local changes and want to discard them:
# git reset --hard HEAD
# git pull

# Activate venv and update dependencies
source venv/bin/activate
pip install -r requirements-linux.txt

# Run migrations
cd django
python manage.py migrate
python manage.py collectstatic --noinput
cd ..

# Restart application
./restart.sh
```

**If using systemd service:**
```bash
cd ~/teveclub
git pull

# If you have local changes and want to discard them:
# git reset --hard HEAD
# git pull

# Activate venv and update dependencies
source venv/bin/activate
pip install -r requirements-linux.txt

# Run migrations
cd django
python manage.py migrate
python manage.py collectstatic --noinput

# Restart service
sudo systemctl restart teveclub
```

### 2a. Force Update (Discard All Local Changes)

If you want to completely reset to the latest version from GitHub:

```bash
cd ~/teveclub

# Discard ALL local changes (be careful!)
git fetch origin
git reset --hard origin/main

# Or if on a different branch:
# git reset --hard origin/your-branch-name

# Update dependencies
source venv/bin/activate
pip install -r requirements-linux.txt

# Run migrations and collect static
cd django
python manage.py migrate
python manage.py collectstatic --noinput
cd ..

# Restart
./restart.sh  # or: sudo systemctl restart teveclub
```

**Common git commands:**
```bash
# Check current status
git status

# See what changed
git diff

# Discard changes in specific file
git checkout -- filename

# Discard all local changes
git reset --hard HEAD

# Update to latest from GitHub
git pull

# Force update (discard everything)
git fetch origin
git reset --hard origin/main

# See commit history
git log --oneline -10

# Clean untracked files (be careful!)
git clean -fd

# Ignore local changes to env/venv folders
# (These should already be in .gitignore)
git update-index --assume-unchanged venv/
git update-index --assume-unchanged env/
```

**Reset specific folders (if needed):**
```bash
# If venv or env folders got tracked by mistake
git rm -r --cached env/
git rm -r --cached venv/

# Make sure .gitignore contains:
# env/
# venv/
# *.pyc
# __pycache__/
# db.sqlite3
# .env
# logs/
```

### 3. Backup Database (if using SQLite)

```bash
# Create backup
cp ~/teveclub/django/db.sqlite3 ~/teveclub/django/db.sqlite3.backup.$(date +%Y%m%d)

# For regular backups, add to crontab:
crontab -e
# Add: 0 2 * * * cp ~/teveclub/django/db.sqlite3 ~/teveclub/django/db.sqlite3.backup.$(date +\%Y\%m\%d)
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status teveclub

# View detailed logs
sudo journalctl -u teveclub -n 50 --no-pager

# Check if port 3000 is in use
sudo netstat -tlnp | grep 3000

# Check file permissions
ls -la ~/teveclub/django
```

### Static Files Not Loading

```bash
# Verify static files are collected
ls -la ~/teveclub/django/staticfiles/

# Check Nginx configuration
sudo nginx -t

# Check file permissions
sudo chown -R ubuntu:ubuntu ~/teveclub/django/staticfiles/
sudo chmod -R 755 ~/teveclub/django/staticfiles/
```

### Permission Denied Errors

```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu ~/teveclub

# Fix log directory
mkdir -p ~/teveclub/logs
chmod 755 ~/teveclub/logs
```

### Can't Connect to Application

```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Check if Nginx is running
sudo systemctl status nginx

# Check AWS Security Group allows HTTP/HTTPS
# Go to EC2 console > Security Groups > Inbound Rules

# Check firewall
sudo ufw status
```

### High Memory Usage

```bash
# Check memory
free -h

# Reduce Gunicorn workers in teveclub.service
sudo vim /etc/systemd/system/teveclub.service
# Change --workers 3 to --workers 2

# Restart
sudo systemctl daemon-reload
sudo systemctl restart teveclub
```

---

## Performance Optimization

### 1. Enable Caching

Add to Django settings:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

### 2. Enable Gzip Compression in Nginx

Add to `/etc/nginx/nginx.conf`:
```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

---

## Security Checklist

- [ ] Changed DEBUG=False in production
- [ ] Set strong SECRET_KEY
- [ ] Configured ALLOWED_HOSTS
- [ ] Enabled HTTPS with SSL certificate
- [ ] Configured firewall rules
- [ ] Regular system updates (`sudo apt update && sudo apt upgrade`)
- [ ] Regular application backups
- [ ] Monitoring logs for suspicious activity
- [ ] Keep SSH key secure
- [ ] Disable password authentication for SSH

---

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)

---

## Support

For issues or questions:
1. Check application logs: `~/teveclub/logs/`
2. Check system logs: `sudo journalctl -u teveclub`
3. Review this documentation
4. Check AWS Security Group settings

---

**Last Updated**: November 2025
