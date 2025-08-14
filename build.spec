# -*- mode: python -*-
from PyInstaller.building.build_main import Analysis

block_cipher = None

# MANUALLY list all required modules
required_modules = ['teveclub', 'icon']

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.')],  # Only non-Python files here
    hiddenimports=required_modules,
    hookspath=[],
    excludes=[],
    runtime_hooks=[],
    cipher=block_cipher,
    noarchive=False
)

# Force-include your modules
for module in required_modules:
    a.add_pure_python_module(module)

pyz = a.pure

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TeveClub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico'
)