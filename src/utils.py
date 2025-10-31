"""
Utility functions for the Teveclub Bot
"""
import time
import random
import json
import os
from pathlib import Path
import sys
from src.config import DEFAULT_USER_AGENTS, USER_AGENTS_FILE, ICON_FILE


def get_user_agent():
    """
    Get a random user agent string from the configuration
    First tries to load from JSON file, falls back to defaults
    
    Returns:
        str: A random user agent string
    """
    user_agents = DEFAULT_USER_AGENTS.copy()
    
    # Try to load from JSON file if it exists
    if os.path.exists(USER_AGENTS_FILE):
        try:
            with open(USER_AGENTS_FILE, 'r') as f:
                data = json.load(f)
                # Check if loaded data is a list of strings
                if isinstance(data, list) and all(isinstance(x, str) for x in data):
                    user_agents = data
                # Alternatively check if it's a dict with 'user_agents' key
                elif isinstance(data, dict) and 'user_agents' in data and isinstance(data['user_agents'], list):
                    user_agents = data['user_agents']
        except (json.JSONDecodeError, PermissionError):
            pass  # Fall back to default if there's any error
    
    return random.choice(user_agents)


def do_sleep(lambda_val=0.6, max_sleep=1.0):
    """
    Sleep for a random exponential time to simulate human behavior
    
    Args:
        lambda_val (float): Lambda parameter for exponential distribution
        max_sleep (float): Maximum sleep time in seconds
    """
    time.sleep(min(random.expovariate(lambda_val), max_sleep))


def load_credentials(credentials_file):
    """
    Load saved credentials from JSON file if it exists
    
    Args:
        credentials_file (str): Path to the credentials file
        
    Returns:
        dict or None: Credentials dictionary or None if not found/error
    """
    if os.path.exists(credentials_file):
        try:
            with open(credentials_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError):
            return None
    return None


def save_credentials(credentials_file, username, password):
    """
    Save credentials to JSON file
    
    Args:
        credentials_file (str): Path to the credentials file
        username (str): Username to save
        password (str): Password to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(credentials_file, 'w') as f:
            json.dump({"username": username, "password": password}, f)
        return True
    except (PermissionError, TypeError):
        return False


def get_icon_path():
    """
    Enhanced icon path resolution with multiple fallbacks
    
    Returns:
        str: Path to the icon file
    """
    # Try development location first
    dev_icon = Path(ICON_FILE)
    if dev_icon.exists():
        return str(dev_icon)

    # PyInstaller bundle locations
    if getattr(sys, 'frozen', False):
        # 1. MEIPASS (onefile mode)
        meipass_icon = Path(getattr(sys, '_MEIPASS', '')) / ICON_FILE
        if meipass_icon.exists():
            return str(meipass_icon)
        
        # 2. Executable directory (onedir mode)
        exe_dir_icon = Path(sys.executable).parent / ICON_FILE
        if exe_dir_icon.exists():
            return str(exe_dir_icon)

    # cx_Freeze bundle location
    if hasattr(sys, 'frozen') and not getattr(sys, 'frozen', False):
        lib_icon = Path(sys.executable).parent / "lib" / ICON_FILE
        if lib_icon.exists():
            return str(lib_icon)

    # Final fallback to original behavior
    return ICON_FILE if not getattr(sys, 'frozen', False) else os.path.join(getattr(sys, '_MEIPASS', ''), ICON_FILE)
