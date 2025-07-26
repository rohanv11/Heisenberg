from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.router import router as api_router
from app.api.room_router import router as room_router
from app.api.auth_router import router as auth_router
from app.api.board_router import router as board_router
from app.config.settings import DEBUG_MODE
from app.utils.logging_config import configure_logging
from app.utils.exception_handlers import register_exception_handlers
from app.events.startup_shutdown import setup_debug_if_enabled
from app.services.board_service import BoardService
from app.events.socket_manager import create_socketio_app
from app.services.storage import get_storage
from app.services.storage.postgres_storage import PostgresStorage

# Configure all application logging in one place
configure_logging()

# Create logger for this module
logger = logging.getLogger(__name__)

# Create FastAPI app
server_app = FastAPI(
    title="Heisenberg Game Server",
    description="API for Rockefeller - A Monopoly-like Board Game",
    version="0.1.0",
    debug=DEBUG_MODE
)

# Configure CORS
## Find out how to configure CORS properly and why it's needed
server_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all exception handlers
register_exception_handlers(server_app)

# Include routers
PREFIX = "/api"
server_app.include_router(api_router, prefix=PREFIX)
server_app.include_router(room_router, prefix=PREFIX)
server_app.include_router(auth_router, prefix=PREFIX)
server_app.include_router(board_router, prefix=PREFIX)

# Initialize and mount the Socket.IO app to the FastAPI app
# This creates a WebSocket endpoint at /ws path
print("33333333")
server_app.mount("/ws", create_socketio_app())
print("44444444")

@server_app.get("/")
async def root():
    return {
        "message": "Welcome to Rockefeller - A Monopoly-like Board Game!",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@server_app.get("/health")
async def health_check():
    return {"status": "healthy"}

@server_app.on_event("startup")
async def startup_event():
    logger.info("Running startup events...")
    storage = get_storage()
    if isinstance(storage, PostgresStorage):
        await storage.connect()
        logger.info("PostgreSQL connection pool created.")
    await setup_debug_if_enabled()

@server_app.on_event("shutdown")
async def shutdown_event():
    logger.info("Running shutdown events...")
    storage = get_storage()
    if isinstance(storage, PostgresStorage):
        await storage.close()
        logger.info("PostgreSQL connection pool closed.")
