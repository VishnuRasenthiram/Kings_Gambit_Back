"""Game state model for a complete game session."""
from dataclasses import dataclass, field
from enum import Enum
from ..models import Board, PieceType, PieceColor, Move


class GamePhase(str, Enum):
    """Game phase states."""
    SETUP = "setup"
    PLAYING = "playing"
    GAME_OVER = "game_over"


class VictoryReason(str, Enum):
    """Reason for game ending."""
    CHECKMATE = "checkmate"
    CAPTURE = "capture"
    RESIGNATION = "resignation"
    TIMEOUT = "timeout"



@dataclass
class HiddenKingState:
    """State of a player's hidden king."""
    card: PieceType
    is_revealed: bool = False
    decoy_king_captured: bool = False

    def to_dict(self, show_card: bool = True) -> dict:
        return {
            "card": self.card.value if show_card else None,
            "isRevealed": self.is_revealed,
            "decoyKingCaptured": self.decoy_king_captured,
        }


@dataclass
class GameState:
    """Complete state of a game session."""
    game_id: str
    board: Board
    current_turn: PieceColor = PieceColor.POLICE
    phase: GamePhase = GamePhase.SETUP
    hidden_kings: dict[str, HiddenKingState | None] = field(
        default_factory=lambda: {"police": None, "mafia": None}
    )
    move_history: list[Move] = field(default_factory=list)
    moved_pieces: set[str] = field(default_factory=set)
    winner: PieceColor | None = None
    victory_reason: VictoryReason | None = None
    effect_cards: dict[str, list[str]] = field(
        default_factory=lambda: {"police": [], "mafia": []}
    )
    # Active effects that modify piece movements (cleared after each turn)
    active_effects: dict[str, list[str]] = field(
        default_factory=lambda: {"police": [], "mafia": []}
    )

    def to_dict(self, viewer_color: PieceColor | None = None) -> dict:
        """Convert game state to dictionary for JSON."""
        return {
            "gameId": self.game_id,
            "board": self.board.to_dict(),
            "currentTurn": self.current_turn.value,
            "phase": self.phase.value,
            "hiddenKings": {
                k: v.to_dict(
                    show_card=(
                        viewer_color is None or 
                        viewer_color == PieceColor(k) or 
                        v.is_revealed
                    )
                ) if v else None
                for k, v in self.hidden_kings.items()
            },
            "winner": self.winner.value if self.winner else None,
            "victoryReason": self.victory_reason.value if self.victory_reason else None,
        }

    @property
    def last_move(self) -> Move | None:
        """Get the last move made."""
        return self.move_history[-1] if self.move_history else None
