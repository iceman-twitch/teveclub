from cx_Freeze import setup, Executable
import sys
import os

# Application base
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # For Windows GUI app

# List of included modules
build_options = {
    "packages": ["tkinter", "teveclub", "icon"],
    "excludes": [],
    "include_files": ["icon.ico"],
}

# Executable configuration
executables = [
    Executable(
        "main.py",
        base=base,
        icon="icon.ico",
        target_name="TeveClub"
    )
]

setup(
    name="TeveClub",
    version="1.0",
    description="Your Application",
    options={"build_exe": build_options},
    executables=executables
)