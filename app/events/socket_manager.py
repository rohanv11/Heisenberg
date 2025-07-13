"""
Socket.IO manager module to avoid circular imports.
Uses direct python-socketio AsyncServer for better reliability.
"""
import socketio
import logging

logger = logging.getLogger(__name__)

def create_socketio_app():
    """Create and initialize the Socket.IO server and ASGI app
    This should be called explicitly during application startup
    
    Returns:
        socketio.ASGIApp: The ASGI app to mount in FastAPI
    """
    # Create SocketIO server
    sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
    
    # Create the ASGI app
    socket_app = socketio.ASGIApp(sio)
    logger.info("SocketIO server initialized")
    
    # Import and register socket event handlers
    from app.events.socket_events import register_handlers
    register_handlers(sio)
    logger.info("Socket.IO event handlers registered")
    
    return socket_app
