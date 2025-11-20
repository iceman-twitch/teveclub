# Teveclub Bot - Automation Tool for TeveClub.hu

An automation bot for TeveClub.hu, a Hungarian browser-based pet game that has been entertaining players since the early 2000s. In TeveClub, players raise and care for virtual camels by feeding them, teaching tricks, and playing guessing games to earn points and compete on leaderboards.

## Live Demo

Try the web interface online: **[https://eternionwow.servegame.com/](https://eternionwow.servegame.com/)**

Use this demo to test the bot features without setting up your own server. Just log in with your TeveClub.hu credentials and start automating your camel care routine.

## About TeveClub.hu

TeveClub.hu is a long-running Hungarian virtual pet game where you manage your own camel. The game involves:
- **Feeding** your camel to keep it healthy and happy
- **Teaching tricks** to increase your camel's skills
- **Playing guessing games** to earn points and climb the rankings
- **Competing** with other players on various leaderboards

The game requires regular attention and repetitive clicking, which is where this automation tool comes in handy.

## What This Bot Does

This bot automates the repetitive tasks in TeveClub.hu, allowing you to:
- Automatically feed your camel when hungry
- Complete learning sessions without manual clicking
- Play through guessing games automatically
- Run all tasks in sequence with a single command

The bot can operate in both GUI mode (with a user-friendly interface) and CLI mode (for headless automation or scripting).

## Features

### Current Features
- **Smart Feeding System** - Only feeds when the camel is actually hungry, avoiding wasted actions
- **Automated Learning** - Completes trick learning sessions automatically
- **Guessing Game Automation** - Plays through guessing games without manual input
- **Web Interface** - Modern Django-based web UI for remote control and automation
- **Auto Mode** - Complete automation with one click: login, feed, learn, guess, logout
- **Remember Me** - Save username and password for quick access
- **GUI Desktop Application** - Native desktop interface with rounded, themed design
- **CLI Mode** - Command-line interface for automation and scripting
- **Session Management** - Maintains login sessions across multiple actions
- **Credential Storage** - Securely saves login credentials for convenience

### Future Plans

We're planning several exciting features for future releases:

- **Multi-Camel Support** - Switch between multiple camels on the same account
- **Scheduling System** - Set specific times for the bot to run tasks
- **Advanced Statistics** - Track your camel's progress and bot activity over time
- **Custom Action Sequences** - Create your own automation routines
- **Notification System** - Get alerts when tasks complete or issues occur
- **Enhanced Food Selection** - More control over feeding preferences

## Quick Start

### Desktop GUI Application (Windows)

```bash
# First time setup
env.bat

# Run the application
test.bat
```

Or run directly with Python:
```bash
python main.py
```

### Web Interface

```bash
# Navigate to Django folder
cd django

# Start the web server
run_server.bat

# Open browser to http://127.0.0.1:8000
```

### Command Line Interface

```bash
# Run with username and password
python main.py --cli username password

# The bot will automatically perform all tasks
```

## Installation

### Windows
1. Clone this repository
2. Run `env.bat` to set up the virtual environment
3. Run `test.bat` to launch the GUI application

### Linux
1. Clone this repository
2. Run `./env.sh` to set up the virtual environment
3. Run `./run.sh` for CLI mode or deploy the web interface

For detailed Linux deployment with HTTPS, see `docs/LINUX_QUICK.md`.

## Web Deployment

The Django web interface can be deployed on any server. We provide:
- Automated deployment script (`deploy.sh`)
- Complete HTTPS setup guide
- Nginx reverse proxy configuration
- Systemd service for automatic startup

See `docs/LINUX_QUICK.md` for comprehensive deployment instructions.

## Configuration

### Custom User Agents
Create a `user_agents.json` file to use custom browser user agents:
```json
[
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
]
```

### Credentials
Credentials are automatically saved after first login in `credentials.json`. You can edit this file manually if needed.

## Project Structure

```
teveclub/
├── main.py              # Main entry point
├── src/                 # Core application code
│   ├── bot_core.py     # Bot logic and automation
│   ├── gui.py          # Desktop GUI interface
│   ├── config.py       # Configuration settings
│   └── utils.py        # Utility functions
├── django/             # Web interface
│   ├── bot_api/        # REST API
│   ├── templates/      # HTML templates
│   └── static/         # CSS and JavaScript
└── docs/               # Documentation
```

## Documentation

- `docs/QUICK_START.md` - Getting started guide
- `docs/LINUX_QUICK.md` - Linux deployment guide
- `docs/ARCHITECTURE.md` - Technical architecture
- `docs/PROJECT_STRUCTURE.md` - Detailed file structure
- `docs/UI_DESIGN.md` - UI design documentation

## Contributing

This is a personal automation project, but suggestions and improvements are welcome. Feel free to open issues or submit pull requests.

## Disclaimer

This bot is intended for personal use and educational purposes. Use it responsibly and in accordance with TeveClub.hu's terms of service. The authors are not responsible for any consequences of using this automation tool.

## License

This project is open source and available for personal use.
