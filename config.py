import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
PROFILES_DIR = BASE_DIR / "browser_profiles"
X_PROFILE_DIR = PROFILES_DIR / "x_profile"
THREADS_PROFILE_DIR = PROFILES_DIR / "threads_profile"

# Ensure directories exist
PROFILES_DIR.mkdir(exist_ok=True)
X_PROFILE_DIR.mkdir(exist_ok=True)
THREADS_PROFILE_DIR.mkdir(exist_ok=True)

# Excel / Data settings
DEFAULT_EXCEL_PATH = BASE_DIR / "promo_data.xlsx"

# Safety and anti-spam delays (in seconds)
TYPING_DELAY_MIN = 0.03   # Min delay between keystrokes
TYPING_DELAY_MAX = 0.12   # Max delay between keystrokes
ACTION_DELAY_MIN = 2.0    # Min delay between clicks/actions
ACTION_DELAY_MAX = 5.0    # Max delay between clicks/actions
POST_INTERVAL_MIN = 30    # Min delay (seconds) between two consecutive posts
POST_INTERVAL_MAX = 60    # Max delay (seconds) between two consecutive posts

# Browser settings
HEADLESS_MODE = False     # Set to False to monitor what the bot is doing; True for silent mode
BROWSER_TIMEOUT_MS = 60000 # 60 seconds
