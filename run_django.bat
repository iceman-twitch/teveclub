@echo off
echo ================================
echo   Teveclub Django Web Server
echo ================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "env\" (
    echo Creating virtual environment...
    python -m venv env
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call env\Scripts\activate.bat

cd django

REM Install/update requirements
echo Installing requirements...
pip install -r requirements.txt

REM Make migrations
echo Setting up database...
python manage.py makemigrations
python manage.py migrate

REM Start server
echo.
echo ================================
echo   Starting Django server...
echo   Access at: http://127.0.0.1:8080
echo ================================
echo.
python manage.py runserver 8080
call env\Scripts\deactivate
