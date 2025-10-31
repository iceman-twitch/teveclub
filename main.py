#!/usr/bin/env python3
"""
Main entry point for Teveclub Bot
Can run in either GUI mode or CLI mode
"""
import sys
from src.bot_core import TeveClub
from src.gui import run_gui


def run_cli(username, password):
    """
    Run the bot in command-line mode
    
    Args:
        username (str): Teveclub username
        password (str): Teveclub password
    """
    print(f"Starting Teveclub Bot for user: {username}")
    teve = TeveClub(username, password)
    teve.run_bot()


def main():
    """Main function to determine run mode"""
    if len(sys.argv) > 2:
        # CLI mode with arguments
        username = str(sys.argv[1])
        password = str(sys.argv[2])
        run_cli(username, password)
    elif len(sys.argv) == 2 and sys.argv[1] in ['--gui', '-g']:
        # Explicit GUI mode
        run_gui()
    elif len(sys.argv) == 1:
        # No arguments - default to GUI mode
        run_gui()
    else:
        print("Usage:")
        print("  GUI mode (default):  python main.py")
        print("  GUI mode (explicit): python main.py --gui")
        print("  CLI mode:            python main.py <username> <password>")
        sys.exit(1)


if __name__ == "__main__":
    main()
