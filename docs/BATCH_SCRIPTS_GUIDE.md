# Batch Scripts Guide

## Available Scripts

### 1. `env.bat` - Environment Setup
**Purpose:** Creates and sets up the Python virtual environment

**When to use:** 
- First time setup
- After cloning the repository
- If virtual environment gets corrupted

**What it does:**
1. Creates Python 3.9 virtual environment in `env/` folder
2. Activates the environment
3. Upgrades pip
4. Installs packages from `requirements.txt`
5. Deactivates and exits

**Usage:**
```bash
env.bat
```

**Note:** You only need to run this once!

---

### 2. `test.bat` - Application Launcher (NEW)
**Purpose:** Activates environment and runs the Teveclub bot

**When to use:**
- Every time you want to run the bot
- For testing the application
- Daily use

**What it does:**
1. Checks if virtual environment exists
2. Activates the environment
3. Runs `python main.py` (GUI mode)
4. Deactivates when you close the app

**Usage:**
```bash
test.bat
```

**This is the main way to run your bot!**

---

### 3. `onefile.bat` - Build Executable
**Purpose:** Creates a standalone .exe file

**When to use:**
- When you want to distribute the bot
- To create a portable version
- For production deployment

**What it does:**
1. Activates virtual environment
2. Runs PyInstaller
3. Creates executable in `dist/` folder

**Usage:**
```bash
onefile.bat
```

---

## Quick Start Guide

### First Time Setup
```bash
# Step 1: Set up environment
env.bat

# Step 2: Run the bot
test.bat
```

### Daily Use
```bash
# Just run this every time
test.bat
```

### Manual Activation (Advanced)
If you prefer to use the command line directly:

```bash
# Activate environment
env\Scripts\activate

# Run GUI mode
python main.py

# Run CLI mode
python main.py username password

# Run tests
python test_structure.py

# Deactivate when done
deactivate
```

---

## Troubleshooting

### "Virtual environment not found"
**Solution:** Run `env.bat` first

### "Python 3.9 not found"
**Solution:** Install Python 3.9 from https://www.python.org/downloads/

### "Module not found" errors
**Solution:** Run `env.bat` to reinstall dependencies

### Script won't run
**Solution:** Make sure you're in the correct directory:
```bash
cd d:\Github\teveclub
test.bat
```

---

## Script Comparison

| Script | Purpose | Frequency | Creates Output |
|--------|---------|-----------|----------------|
| `env.bat` | Setup | Once | `env/` folder |
| `test.bat` | Run app | Every use | None |
| `onefile.bat` | Build exe | As needed | `dist/` folder |

---

## Windows PowerShell Alternative

If you're using PowerShell instead of Command Prompt:

### Activate environment
```powershell
env\Scripts\Activate.ps1
```

### Run the bot
```powershell
python main.py
```

### Deactivate
```powershell
deactivate
```

**Note:** You may need to enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Recommended Workflow

```
┌─────────────────────────────────────────────┐
│  First Time Setup                           │
│  ▼                                          │
│  Run: env.bat                               │
│  (Creates virtual environment)              │
└─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Daily Use                                  │
│  ▼                                          │
│  Run: test.bat                              │
│  (Launches the bot in GUI mode)             │
└─────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Building Executable (Optional)             │
│  ▼                                          │
│  Run: onefile.bat                           │
│  (Creates standalone .exe file)             │
└─────────────────────────────────────────────┘
```

---

## Summary

**For 99% of use cases, just remember:**

1. **First time:** `env.bat`
2. **Every other time:** `test.bat`

That's it! 🎉
