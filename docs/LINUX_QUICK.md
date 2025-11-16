# Fresh clone
```bash
cd /home/ubuntu
git clone https://github.com/iceman-twitch/teveclub.git
cd teveclub
```
### Run setup as ubuntu user (NO SUDO)
```bash
chmod +x env.sh run.sh stop.sh restart.sh status.sh run_django.sh
./env.sh
```
### Install whitenoise
source venv/bin/activate
pip install whitenoise gunicorn

# Create .env file
```bash
cd django
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=5bpkrvg%*t1q**uo=g=(^-12!)&6h$uc^&2ei_z&4e1@l2y_96
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=http://*,https://*
EOF
```
**Important**: Generate a strong SECRET_KEY:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

# Run Django setup
```bash
python manage.py migrate
python manage.py collectstatic --noinput
cd ..
```
# Setup systemd service
```bash
sudo cp teveclub.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable teveclub
sudo systemctl start teveclub
sudo systemctl status teveclub
```