import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = ROOT_DIR / "jarvis"
ASSETS_DIR = APP_DIR / "assets"
LOG_DIR = ROOT_DIR / "logs"

# Ensure directories exist
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Load .env file from root directory
dotenv_path = ROOT_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    load_dotenv()  # fallback to search in cwd

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Email Settings
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

# App defaults
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "New York")
NEWS_COUNTRY = os.getenv("NEWS_COUNTRY", "us")
WAKE_WORD = os.getenv("WAKE_WORD", "Hey Jarvis").strip().lower()
WAKE_WORD_SENSITIVITY = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))

# Log configuration
LOG_FILE_PATH = LOG_DIR / "jarvis.log"
