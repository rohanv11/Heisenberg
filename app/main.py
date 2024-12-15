from fastapi import FastAPI
from socketio import ASGIApp
from app.socket_manager import sio
from .routers import room

app = FastAPI()

# Include REST endpoints
def include_routers(app):
    app.include_router(room.router)

include_routers(app)

# Mount Socket.IO with FastAPI
socket_app = ASGIApp(sio, other_asgi_app=app)

# Entry point for Docker
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)