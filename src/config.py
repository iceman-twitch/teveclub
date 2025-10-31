"""
Configuration file for Teveclub Bot
Contains all constants and URLs used throughout the application
"""

# API URLs
LOGIN_URL = "https://teveclub.hu/"
MYTEVE_URL = "https://teveclub.hu/myteve.pet"
TANIT_URL = "https://teveclub.hu/tanit.pet"
TIPP_URL = "https://teveclub.hu/egyszam.pet"

# File paths
CREDENTIALS_FILE = "credentials.json"
USER_AGENTS_FILE = "user_agents.json"
ICON_FILE = "icon.ico"

# Default User Agents
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
]

# Bot settings
MAX_FEED_ATTEMPTS = 10
SLEEP_MIN = 0.0
SLEEP_MAX = 1.0
SLEEP_LAMBDA = 0.6
