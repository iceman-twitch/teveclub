@echo off
echo Activating Python environment...
call env\Scripts\activate

echo Running PyInstaller on form.py...
pyinstaller --onefile --windowed --name "teveclub" --icon="icon.ico" form.py

echo.
echo Build complete! Check the 'dist' folder for your executable.
pause