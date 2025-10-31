@echo off
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Activating Python environment...
call env\Scripts\activate

echo Running PyInstaller on main.py...
pyinstaller --onefile --windowed --name "teveclub" --icon="icon.ico" main.py

echo.
echo Build complete! Check the 'dist' folder for your executable.
pause