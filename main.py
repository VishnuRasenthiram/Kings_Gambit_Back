"""King's Gambit - Main application entry point."""
import os
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.features.game.websocket import register_game_handlers

_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
)
allowed_origins: list[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# Create FastAPI app
app = FastAPI(
    title="King's Gambit API",
    description="Backend for the King's Gambit chess variant game",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=allowed_origins,
)

# Register game event handlers
register_game_handlers(sio)

# Create combined ASGI app
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "King's Gambit API", "status": "running"}


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
