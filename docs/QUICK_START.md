# Quick Start Guide

## For Immediate Use

### Step 1: First Time Setup
```bash
env.bat
```
**Run this ONCE to set up your Python environment.**

### Step 2: Run the Bot
```bash
test.bat
```
**Run this every time you want to use the bot.**

---

## Detailed Instructions

### Option 1: Run with GUI (Recommended)
```bash
test.bat
```
- Opens a graphical interface
- Login with your credentials
- Click buttons to perform actions
- Credentials are saved automatically

### Option 2: Run from Command Line (Manual)
```bash
env\Scripts\activate
python main.py your_username your_password
```
- Runs all actions automatically
- Login → Feed → Learn → Guess
- Good for automation/scheduling

## What Changed?

### FIXED: Smart Feeding
**Before:** Always fed 10 times (wasteful)  
**Now:** Checks if pet needs food, stops when full

### Better Organization
**Before:** All code in 2 large files  
**Now:** Organized into logical modules

### Easier to Maintain
**Before:** Hard to find specific features  
**Now:** Each module has clear purpose

## File Quick Reference

| File | Purpose | When to Edit |
|------|---------|--------------|
| `main.py` | Start the app | Rarely |
| `src/config.py` | Settings & URLs | Change URLs or settings |
| `src/utils.py` | Helper functions | Add utilities |
| `src/bot_core.py` | Bot actions | Add new game actions |
| `src/gui.py` | GUI interface | Change interface |

## Testing

Run the test script to verify everything works:
```bash
env\Scripts\activate
python test_structure.py
```

Or just run `test.bat` to launch the app!

Should output:
```
==================================================
TEVECLUB BOT - NEW STRUCTURE TEST
==================================================
Testing imports...
Config loaded
Utils loaded
Bot core loaded

ALL TESTS PASSED!
```

## Common Tasks

### Change URLs
Edit `src/config.py`:
```python
LOGIN_URL = "https://new-url.com/"
```

### Add Custom User Agents
Create `user_agents.json`:
```json
[
  "Mozilla/5.0 ...",
  "Mozilla/5.0 ..."
]
```

### Modify Feed Attempts
Edit `src/config.py`:
```python
MAX_FEED_ATTEMPTS = 5  # Change from 10 to 5
```

### Build Executable
```bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico;." main.py
```

## Troubleshooting

### Import Error
```
ModuleNotFoundError: No module named 'src'
```
**Solution:** Make sure you're in the project directory:
```bash
cd d:\Github\teveclub
python main.py
```

### Dependencies Missing
```
ModuleNotFoundError: No module named 'requests'
```
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Icon Not Found
**Solution:** Make sure `icon.ico` is in the same directory as `main.py`

## Next Steps

You mentioned wanting to make more changes later. Here are some ideas:

1. **Add Logging**
   - Replace print statements with proper logging
   - Save logs to file for debugging

2. **Schedule Automation**
   - Run bot at specific times
   - Use Windows Task Scheduler or cron

3. **Multiple Accounts**
   - Support managing multiple accounts
   - Switch between accounts in GUI

4. **Better Error Handling**
   - More specific error messages
   - Retry logic for failed requests

5. **Statistics**
   - Track feeding history
   - Show stats in GUI

6. **Configuration File**
   - Add settings.ini or config.yml
   - User-customizable settings

## Need Help?

The code is now well-organized and documented:
- Each function has docstrings explaining what it does
- Modules are separated by responsibility
- Configuration is centralized

Start with `main.py` and follow the imports to understand the flow!

## Summary of Improvements

Fixed food system (smart feeding)  
Modular structure (easy to maintain)  
Better naming (Python conventions)  
Centralized config (easy to change)  
Reusable utilities (DRY principle)  
Documentation (README, guides, docstrings)  
Both GUI and CLI modes  
Test script included  

**Your bot is now more efficient and easier to work with!**
