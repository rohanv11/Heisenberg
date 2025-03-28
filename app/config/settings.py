import os
from dotenv import load_dotenv
from pydantic import HttpUrl
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Environment
ENV = os.getenv("ENV", "development")
IS_DEVELOPMENT = ENV == "development"
IS_PRODUCTION = ENV == "production"
IS_TESTING = ENV == "testing"

# Common Settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")
API_PREFIX = "/api"

# Debugging Settings
DEBUG_PORT = int(os.getenv("DEBUG_PORT", "5678"))

# Server Config
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# Centrifugo Config
CENTRIFUGO_HOST = os.getenv("CENTRIFUGO_HOST", "localhost")
CENTRIFUGO_PORT = os.getenv("CENTRIFUGO_PORT", "8001")
CENTRIFUGO_API_KEY = os.getenv("CENTRIFUGO_API_KEY", "")
CENTRIFUGO_SECRET = os.getenv("CENTRIFUGO_SECRET", "")

# MongoDB Config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/heisenberg")
DB_NAME = os.path.basename(MONGO_URI) if "/" in MONGO_URI else "heisenberg"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()  # Default log level for the application
MONGO_LOG_LEVEL = os.getenv("MONGO_LOG_LEVEL", "warning").lower()  # MongoDB log level
UVICORN_LOG_LEVEL = os.getenv("UVICORN_LOG_LEVEL", "info").lower()  # Uvicorn/FastAPI log level

# Google OAuth Config
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
OAUTH_REDIRECT_URL = os.getenv("OAUTH_REDIRECT_URL", "http://localhost:8000/api/auth/callback")

# JWT Config
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24 * 7  # 1 week

# Game Config
DEFAULT_GAME_CONFIG = {
    "even_build": os.getenv("EVEN_BUILD", "True").lower() in ("true", "1", "t"),
    "starting_cash": int(os.getenv("STARTING_CASH", "1500")),
    "max_players": int(os.getenv("MAX_PLAYERS_PER_ROOM", "4")),
}

# PostgreSQL Config
POSTGRES_USER = os.getenv("POSTGRES_USER", "your_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "heisenberg")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

# Configuration based on environment
if IS_DEVELOPMENT:
    # Development-specific settings
    pass
elif IS_PRODUCTION:
    # Production-specific settings
    DEBUG_MODE = False
    assert GOOGLE_CLIENT_ID, "GOOGLE_CLIENT_ID must be set in production"
    assert GOOGLE_CLIENT_SECRET, "GOOGLE_CLIENT_SECRET must be set in production"
    assert JWT_SECRET_KEY != "supersecretkey", "JWT_SECRET_KEY must be changed in production"
elif IS_TESTING:
    # Testing-specific settings
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/heisenberg_test")
