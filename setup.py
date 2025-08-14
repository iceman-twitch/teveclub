from cx_Freeze import setup, Executable
import sys
import os

# Application base
base = "Win32GUI" if sys.platform == "win32" else None

build_options = {
    "packages": ["tkinter", "requests", "bs4", "json", "pathlib", "time", "random"],
    "includes": ["teveclub", "icon"],  # Explicitly include your custom modules
    "include_files": [
        "icon.ico",
        ("teveclub.py", "lib/teveclub.py"),  # Force include with destination path
        ("icon.py", "lib/icon.py")
    ],
    "excludes": [],
    "optimize": 2,
}

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
    description="TeveClub Application",
    options={"build_exe": build_options},
    executables=executables
)