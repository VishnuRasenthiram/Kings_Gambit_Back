"""King's Gambit - Main application entry point."""
import os
import socketio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.features.game.websocket import register_game_handlers
from app.features.auth.routes.admin_routes import router as admin_router
from app.features.bug_report.routes.report_routes import router as report_router
from app.features.bug_report.services.db_service import init_db

_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
)
allowed_origins: list[str] = [o.strip()
                              for o in _raw_origins.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield


# Create FastAPI app
app = FastAPI(
    title="King's Gambit API",
    description="Backend for the King's Gambit chess variant game",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST routers
app.include_router(admin_router)
app.include_router(report_router)

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
