# 🐪 Teveclub Django Web Application

A web-based interface for the Teveclub bot with modern JavaScript frontend and Django REST API backend.

## 📁 Project Structure

```
django/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── run_server.bat           # Quick start script for Windows
├── teveclub_web/            # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── bot_api/                 # Bot API application
│   ├── views.py            # API endpoints
│   ├── urls.py             # API routes
│   └── apps.py
├── templates/
│   └── index.html          # Main frontend HTML
└── static/
    ├── css/
    │   └── style.css       # Brownish rounded theme
    └── js/
        └── app.js          # Frontend API client
```

## 🚀 Quick Start

### Option 1: Use the batch script (Recommended)
```bash
cd django
run_server.bat
```

### Option 2: Manual setup
```bash
cd django

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Run server
python manage.py runserver
```

## 🌐 Access the Application

Once the server is running, open your browser to:
```
http://127.0.0.1:8000
```

## 📡 API Endpoints

All API endpoints are prefixed with `/api/`:

- **POST** `/api/login/` - Authenticate user
  - Body: `{"username": "...", "password": "..."}`
  - Returns: `{"success": true/false, "message": "..."}`

- **POST** `/api/feed/` - Feed the pet (requires session)
  - Returns: `{"success": true/false, "message": "..."}`

- **POST** `/api/learn/` - Learn tricks (requires session)
  - Returns: `{"success": true/false, "message": "..."}`

- **POST** `/api/guess/` - Play guess game (requires session)
  - Returns: `{"success": true/false, "message": "..."}`

- **POST** `/api/logout/` - Logout user
  - Returns: `{"success": true/false, "message": "..."}`

## 🎨 Features

- **Modern UI Design**: Brownish rounded theme matching Teveclub.hu
- **Responsive Layout**: Works on desktop and mobile devices
- **Real-time Feedback**: Loading spinners and status updates
- **Session Management**: Secure cookie-based authentication
- **Error Handling**: User-friendly error messages
- **RESTful API**: Clean JSON-based communication

## 🔧 Configuration

Edit `teveclub_web/settings.py` to configure:
- Database settings
- Static files location
- Session timeout
- Allowed hosts for production

## 🛠 Development

### Adding New Features

1. **Backend**: Add new views in `bot_api/views.py`
2. **Routes**: Register URLs in `bot_api/urls.py`
3. **Frontend**: Update `static/js/app.js` with new API calls
4. **UI**: Modify `templates/index.html` for new interface elements

### Styling

Edit `static/css/style.css` to customize:
- Color scheme
- Button styles
- Layout
- Animations

## 📦 Dependencies

- **Django**: Web framework
- **requests**: HTTP library for external requests
- **beautifulsoup4**: HTML parsing
- **Pillow**: Image processing

## 🔐 Security Notes

- Change `SECRET_KEY` in production
- Enable HTTPS for production deployment
- Set `DEBUG = False` in production
- Configure proper `ALLOWED_HOSTS`

## 📝 Notes

- Sessions stored in Django database
- Bot instances managed per session
- CSRF protection enabled for all POST requests
- Frontend uses fetch API for AJAX calls

## 🐛 Troubleshooting

**Server won't start:**
- Check if port 8000 is available
- Ensure Python 3.9+ is installed
- Verify virtual environment activation

**CSS/JS not loading:**
- Run `python manage.py collectstatic`
- Check `STATIC_URL` and `STATICFILES_DIRS` in settings

**API errors:**
- Check Django console for error messages
- Verify CSRF token in browser console
- Ensure proper JSON content-type headers

## 📄 License

Same as parent Teveclub project
