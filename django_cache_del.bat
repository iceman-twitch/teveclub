@echo off
echo Clearing Django cache...

REM Delete __pycache__ directories
echo Deleting __pycache__ folders...
for /d /r "django" %%d in (__pycache__) do (
    if exist "%%d" (
        echo Deleting: %%d
        rd /s /q "%%d"
    )
)

REM Delete .pyc files
echo Deleting .pyc files...
del /s /q "django\*.pyc" 2>nul

REM Delete Django session files (if using file-based sessions)
if exist "django\sessions" (
    echo Deleting session files...
    rd /s /q "django\sessions"
)

REM Clear Django's database cache (if using database cache)
echo Note: To clear database cache, run: python django\manage.py clear_cache

echo.
echo Django cache cleared successfully!
echo Remember to do a hard refresh in your browser: Ctrl+Shift+R or Ctrl+F5
pause
