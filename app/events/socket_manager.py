"""
Socket.IO manager module to avoid circular imports.
"""
from fastapi_socketio import SocketManager

# Create a socket manager instance - it will be initialized in main.py
sio = None

def init_socketio(app):
    """Initialize the Socket.IO manager with the FastAPI app"""
    global sio
    sio = SocketManager(app=app)
    return sio