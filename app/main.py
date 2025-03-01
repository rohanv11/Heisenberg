from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.api.room_router import router as room_router
from app.api.centrifugo_router import router as centrifugo_router
from app.config.settings import DEBUG, SERVER_HOST, SERVER_PORT

# Create FastAPI app
server_app = FastAPI(
    title="Heisenberg Game Server",
    description="API for Rockefeller - A Monopoly-like Board Game",
    version="0.1.0",
    debug=DEBUG
)

# Configure CORS
server_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
server_app.include_router(api_router, prefix="/api")
server_app.include_router(room_router, prefix="/api")
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

if __name__ == "__main__":
    # This allows running the app directly with python app/main.py
    # Useful for debugging and development outside of Docker
    import uvicorn
    
    uvicorn.run(
        "app.main:server_app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=DEBUG
    )