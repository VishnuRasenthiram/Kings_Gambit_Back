"""WebSocket package."""
from .events import ClientEvents, ServerEvents
from .game_socket import register_game_handlers

__all__ = ["ClientEvents", "ServerEvents", "register_game_handlers"]
