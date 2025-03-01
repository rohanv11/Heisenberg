import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment
ENV = os.getenv("ENV", "development")
IS_DEVELOPMENT = ENV == "development"
IS_PRODUCTION = ENV == "production"
IS_TESTING = ENV == "testing"

# Common Settings
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
API_PREFIX = "/api"

# Server Config
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# Centrifugo Config
CENTRIFUGO_HOST = os.getenv("CENTRIFUGO_HOST", "localhost")
CENTRIFUGO_PORT = os.getenv("CENTRIFUGO_PORT", "8001")
CENTRIFUGO_API_KEY = os.getenv("CENTRIFUGO_API_KEY", "")
CENTRIFUGO_SECRET = os.getenv("CENTRIFUGO_SECRET", "")

# Game Config
DEFAULT_GAME_CONFIG = {
    "even_build": os.getenv("EVEN_BUILD", "True").lower() in ("true", "1", "t"),
    "starting_cash": int(os.getenv("STARTING_CASH", "1500")),
    "max_players": int(os.getenv("MAX_PLAYERS_PER_ROOM", "4")),
}

# Configuration based on environment
if IS_DEVELOPMENT:
    # Development-specific settings
    pass
elif IS_PRODUCTION:
    # Production-specific settings
    DEBUG = False
elif IS_TESTING:
    # Testing-specific settings
    pass