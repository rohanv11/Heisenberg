from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.router import router as api_router
from app.api.room_router import router as room_router
from app.api.auth_router import router as auth_router
from app.api.centrifugo_router import router as centrifugo_router
from app.config.settings import DEBUG_MODE, DEBUG_PORT, SERVER_HOST, SERVER_PORT
from app.utils.logging_config import configure_logging
from app.utils.exception_handlers import register_exception_handlers
from app.events.startup_shutdown import startup_db_client, setup_debug_if_enabled, shutdown_db_client

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
server_app.include_router(api_router, prefix="/api")
server_app.include_router(room_router, prefix="/api")
server_app.include_router(auth_router, prefix="/api")
server_app.include_router(centrifugo_router, prefix="/api")

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

# Register startup and shutdown events
# server_app.add_event_handler("startup", startup_db_client)
server_app.add_event_handler("startup", setup_debug_if_enabled)
# server_app.add_event_handler("shutdown", shutdown_db_client)

if __name__ == "__main__":
    # This allows running the app directly with python app/main.py
    # Useful for debugging and development outside of Docker
    import uvicorn
    from app.config.settings import UVICORN_LOG_LEVEL
    
    uvicorn.run(
        "app.main:server_app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=DEBUG_MODE
    )
