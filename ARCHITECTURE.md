# Project Architecture

## Module Dependencies

```
┌─────────────────────────────────────────────────────┐
│                     main.py                         │
│              (Application Entry Point)              │
│  ┌────────────────────────────────────────────┐   │
│  │  - Parses command line arguments           │   │
│  │  - Determines run mode (GUI or CLI)        │   │
│  │  - Delegates to appropriate module         │   │
│  └────────────────────────────────────────────┘   │
└───────────────┬─────────────────────┬───────────────┘
                │                     │
        ┌───────▼────────┐    ┌──────▼──────┐
        │   src/gui.py   │    │ src/bot_core│
        │   (GUI Mode)   │    │  (CLI Mode) │
        └───────┬────────┘    └──────┬──────┘
                │                     │
                └──────────┬──────────┘
                           │
              ┌────────────▼─────────────┐
              │    src/bot_core.py       │
              │   (TeveClub Class)       │
              │  ┌────────────────────┐ │
              │  │ - login()          │ │
              │  │ - feed()  ←FIXED!  │ │
              │  │ - learn()          │ │
              │  │ - guess()          │ │
              │  │ - run_bot()        │ │
              │  └────────────────────┘ │
              └────────────┬─────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
  ┌───────▼────────┐ ┌────▼──────┐ ┌──────▼──────┐
  │  src/config.py │ │src/utils.py│ │  requests   │
  │                │ │            │ │BeautifulSoup│
  │ - URLs         │ │ - Helpers  │ │  (external) │
  │ - Paths        │ │ - Sleep    │ └─────────────┘
  │ - Settings     │ │ - UserAgent│
  └────────────────┘ │ - Creds    │
                     └────────────┘
```

## Data Flow

### GUI Mode
```
User clicks button
       │
       ▼
  GUI Handler (src/gui.py)
       │
       ├─► Load/Save Credentials (src/utils.py)
       │
       ▼
  TeveClub method (src/bot_core.py)
       │
       ├─► Get User Agent (src/utils.py)
       ├─► Sleep (src/utils.py)
       ├─► Use URLs (src/config.py)
       │
       ▼
  HTTP Request to Teveclub.hu
       │
       ▼
  Parse Response (BeautifulSoup)
       │
       ▼
  Return Result
       │
       ▼
  Update GUI Status
```

### CLI Mode
```
Command line args
       │
       ▼
  main.py parses args
       │
       ▼
  Create TeveClub instance
       │
       ▼
  Run run_bot()
       │
       ├─► login()
       ├─► feed()    ← Smart feeding!
       ├─► learn()
       └─► guess()
       │
       ▼
  Print results to console
```

## File Responsibilities

### `main.py` - Entry Point
- Parse command line arguments
- Route to GUI or CLI mode
- Minimal logic, delegates to modules

### `src/__init__.py` - Package
- Package initialization
- Exports main classes
- Version information

### `src/config.py` - Configuration
- **ONLY** constants and configuration
- No logic
- Easy to modify settings

### `src/utils.py` - Utilities
- Reusable helper functions
- No business logic
- Pure utility functions

### `src/bot_core.py` - Bot Logic
- All bot actions
- Stateful TeveClub class
- Core business logic

### `src/gui.py` - GUI Interface
- Tkinter interface
- User interaction
- Calls bot_core methods

## Key Design Principles

1. **Separation of Concerns**
   - Each file has ONE responsibility
   - No mixing of GUI, logic, and config

2. **DRY (Don't Repeat Yourself)**
   - Utilities are centralized
   - No duplicated code

3. **Single Source of Truth**
   - Config values in one place
   - URLs, paths, settings centralized

4. **Dependency Direction**
   - High-level modules depend on low-level
   - Config/Utils have no dependencies
   - Bot core depends on config/utils
   - GUI depends on bot core

5. **Testability**
   - Each module can be tested independently
   - Pure functions in utils
   - Class methods in bot_core

## Import Graph

```
main.py
  └─► src.gui
       └─► src.bot_core
            ├─► src.config
            └─► src.utils
                 └─► src.config

main.py
  └─► src.bot_core
       ├─► src.config
       └─► src.utils
            └─► src.config
```

## Adding New Features

### Example: Add Email Notifications

1. **Add config** (src/config.py):
   ```python
   EMAIL_ENABLED = True
   EMAIL_ADDRESS = "user@example.com"
   ```

2. **Add utility** (src/utils.py):
   ```python
   def send_email(subject, body):
       # Email logic here
   ```

3. **Use in bot** (src/bot_core.py):
   ```python
   from src.utils import send_email
   from src.config import EMAIL_ENABLED
   
   def feed(self):
       result = # ... feeding logic
       if EMAIL_ENABLED:
           send_email("Feed Complete", f"Fed {count} times")
   ```

4. **Update GUI** (src/gui.py):
   ```python
   # Add email settings panel
   ```

This structure makes it easy to add features without breaking existing code!
