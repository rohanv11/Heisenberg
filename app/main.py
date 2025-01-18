from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from socketio import ASGIApp
from app.core.socket_manager import sio
from app.routers import player
from app.routers.room import room_router
from app.utils.exceptions import RoomValidationException, ErrorResponse


app = FastAPI()

@app.middleware("http")
async def custom_exception_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except RoomValidationException as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error_message="Room validation error",
                error=e.error_message,
                data=e.data
            ).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error_message="Internal server error",
                error=str(e),
                data={}
            ).dict()
        )



# Include REST routers
def include_routers(app):
    app.include_router(room_router, prefix="/api/rooms", tags=["Rooms"])
    # app.include_router(player.router, prefix="/api/players", tags=["Players"])

include_routers(app)

# Mount Socket.IO with FastAPI
socket_app = ASGIApp(sio, other_asgi_app=app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
