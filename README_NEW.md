# Teveclub Bot - Restructured

A Python bot for automating interactions with Teveclub.hu game.

## Project Structure

```
teveclub/
├── src/                    # Source code directory
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration and constants
│   ├── utils.py           # Utility functions
│   ├── bot_core.py        # Main bot logic
│   └── gui.py             # GUI interface
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── credentials.json       # Saved credentials (auto-generated)
├── icon.ico              # Application icon
└── README_NEW.md         # This file
```

## New Features

### Improved Food System
- **Smart feeding**: The bot now checks if your pet actually needs food before feeding
- **Automatic stopping**: Stops feeding when the pet is full, rather than always feeding 10 times
- **Better feedback**: Reports how many times the pet was fed

### Better Code Organization
- **Separated concerns**: Bot logic, GUI, utilities, and config are in separate modules
- **Easier to maintain**: Each file has a single responsibility
- **Better imports**: Cleaner dependency management

## Usage

### GUI Mode (Default)
```bash
python main.py
```

### CLI Mode
```bash
env\Scripts\activate
python main.py <username> <password>
```

## Running the Application

1. **Set up the virtual environment (first time only):**
   ```bash
   env.bat
   ```

2. **Run the application:**
   ```bash
   test.bat
   ```
   
   Or manually:
   ```bash
   env\Scripts\activate
   python main.py
   ```

## Module Description

### `src/config.py`
Contains all configuration constants:
- API URLs
- File paths
- Default settings
- User agent configurations

### `src/utils.py`
Utility functions:
- `get_user_agent()`: Get random user agent
- `do_sleep()`: Random sleep for human-like behavior
- `load_credentials()` / `save_credentials()`: Credential management
- `get_icon_path()`: Icon path resolution for packaged apps

### `src/bot_core.py`
Main bot class `TeveClub`:
- `login()`: Authenticate with the website
- `feed()`: Smart feeding system (IMPROVED)
- `learn()`: Learn new tricks
- `guess()`: Play the guessing game
- `run_bot()`: Execute all actions in sequence

### `src/gui.py`
GUI interface using tkinter:
- Login panel
- Main control panel with action buttons
- Status feedback
- Credential saving/loading

### `main.py`
Entry point that supports both GUI and CLI modes

## Migration from Old Structure

The old files (`teveclub.py` and `form.py`) are still present but the new structure is in the `src/` directory. You can safely use the new structure by running `main.py`.

### Key Improvements:
1. **Fixed Food Method**: No longer feeds to max every time - checks if feeding is needed
2. **Modular Design**: Code is organized into logical modules
3. **Better Error Handling**: More informative error messages
4. **Dual Mode**: Supports both GUI and command-line usage

## Building Executable

To build a standalone executable:

```bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico;." main.py
```

## License

Copyright (c) ICEMAN 2025
