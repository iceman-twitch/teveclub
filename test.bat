@echo off
REM Teveclub Bot - Test/Run Script
REM Activates virtual environment and runs the application

echo ========================================
echo Teveclub Bot Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "env\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run env.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Activate the virtual environment
echo Activating virtual environment...
call env\Scripts\activate

REM Check if activation was successful
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment!
    pause
    exit /b 1
)

echo Virtual environment activated.
echo.

REM Run the main application
echo Starting Teveclub Bot...
echo.
python main.py

REM Deactivate when done
call env\Scripts\deactivate

echo.
echo ========================================
echo Application closed.
echo ========================================
pause
