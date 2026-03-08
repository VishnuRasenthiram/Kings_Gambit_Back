"""Pydantic models for bug reports."""
from typing import Any, Optional
from pydantic import BaseModel


class GameStateSnapshot(BaseModel):
    phase: str
    current_turn: str
    active_effects: list[str]


class HiddenKingInfo(BaseModel):
    card: Optional[str] = None
    is_revealed: bool = False


class HiddenKingsSnapshot(BaseModel):
    police: Optional[HiddenKingInfo] = None
    mafia: Optional[HiddenKingInfo] = None


class BugReportSubmit(BaseModel):
    description: str
    timestamp: str
    game_state: GameStateSnapshot
    board: list[list[str]]
    hidden_kings: HiddenKingsSnapshot
    move_history: list[dict[str, Any]]
