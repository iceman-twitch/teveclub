"""
Utility functions for the Teveclub Bot
"""
import time
import random
import json
import os
from pathlib import Path
import sys
import ctypes
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
    Save credentials to JSON file with better error handling and permissions
    
    Args:
        credentials_file (str): Path to the credentials file
        username (str): Username to save
        password (str): Password to save
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        # Get the absolute path to ensure we're writing to the correct location
        abs_path = os.path.abspath(credentials_file)
        directory = os.path.dirname(abs_path)
        
        # Create directory if it doesn't exist
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                return False, f"Cannot create directory: {str(e)}"
        
        # Check if we have write permissions
        if os.path.exists(abs_path):
            # File exists, check if writable
            if not os.access(abs_path, os.W_OK):
                return False, f"No write permission for: {abs_path}"
        else:
            # File doesn't exist, check if directory is writable
            if directory and not os.access(directory, os.W_OK):
                return False, f"No write permission in directory: {directory}"
        
        # Try to write the file
        with open(abs_path, 'w', encoding='utf-8') as f:
            json.dump({"username": username, "password": password}, f, indent=2)
        
        # Verify the file was created
        if not os.path.exists(abs_path):
            return False, "File was not created"
        
        return True, None
        
    except PermissionError as e:
        return False, f"Permission denied: {str(e)}"
    except OSError as e:
        return False, f"OS error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


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


def is_admin():
    """
    Check if the script is running with administrator privileges
    
    Returns:
        bool: True if running as admin, False otherwise
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_writable_path(filename):
    """
    Get a writable path for storing files
    Tries current directory first, falls back to user's AppData if needed
    
    Args:
        filename (str): Name of the file to create
        
    Returns:
        str: Full path where the file can be written
    """
    # Try current directory first
    current_dir_path = os.path.abspath(filename)
    current_dir = os.path.dirname(current_dir_path) if os.path.dirname(current_dir_path) else '.'
    
    if os.access(current_dir, os.W_OK):
        return current_dir_path
    
    # Fallback to user's AppData\Local folder (always writable)
    try:
        appdata = os.environ.get('LOCALAPPDATA')
        if appdata:
            app_folder = os.path.join(appdata, 'TeveClub')
            os.makedirs(app_folder, exist_ok=True)
            return os.path.join(app_folder, filename)
    except:
        pass
    
    # Last resort: temp directory
    import tempfile
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, 'TeveClub', filename)
