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
    voluntarily_revealed: bool = False

    def to_dict(self, show_card: bool = True) -> dict:
        return {
            "card": self.card.value if show_card else None,
            "isRevealed": self.is_revealed,
            "decoyKingCaptured": self.decoy_king_captured,
            "voluntarilyRevealed": self.voluntarily_revealed,
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
    active_effects: dict[str, list[str]] = field(
        default_factory=lambda: {"police": [], "mafia": []}
    )
    card_used_this_turn: dict[str, bool] = field(
        default_factory=lambda: {"police": False, "mafia": False}
    )
    frozen_pieces: dict[str, list[dict]] = field(
        default_factory=lambda: {"police": [], "mafia": []}
    )
    shielded_pieces: dict[str, list[dict]] = field(
        default_factory=lambda: {"police": [], "mafia": []}
    )
    king_cloak_active: dict[str, bool] = field(
        default_factory=lambda: {"police": False, "mafia": False}
    )
    double_move_pending: dict[str, bool] = field(
        default_factory=lambda: {"police": False, "mafia": False}
    )
    captured_pieces: dict[str, list[str]] = field(
        default_factory=lambda: {"police": [], "mafia": []}
    )

    def to_dict(self, viewer_color: PieceColor | None = None) -> dict:
        """Convert game state to dictionary for JSON."""
        viewer_val = viewer_color.value if viewer_color else None

        # Build hidden kings with positions
        hidden_kings_dict: dict[str, dict | None] = {}
        for k, v in self.hidden_kings.items():
            if v is None:
                hidden_kings_dict[k] = None
                continue
            show_card = (
                viewer_color is None
                or viewer_color == PieceColor(k)
                or v.is_revealed
            )
            hk_dict = v.to_dict(show_card=show_card)
            # Include position if viewer owns this king or it's revealed
            if show_card:
                pos = self.board.find_hidden_king(PieceColor(k))
                hk_dict["position"] = pos.to_dict() if pos else None
            hidden_kings_dict[k] = hk_dict

        return {
            "gameId": self.game_id,
            "board": self.board.to_dict(),
            "currentTurn": self.current_turn.value,
            "phase": self.phase.value,
            "hiddenKings": hidden_kings_dict,
            "winner": self.winner.value if self.winner else None,
            "victoryReason": self.victory_reason.value if self.victory_reason else None,
            "effectCards": {
                k: v if k == viewer_val else []
                for k, v in self.effect_cards.items()
            } if viewer_val else self.effect_cards,
            "frozenPieces": self.frozen_pieces,
            "shieldedPieces": self.shielded_pieces,
            "cardUsedThisTurn": self.card_used_this_turn.get(viewer_val, False) if viewer_val else False,
            "kingCloakActive": self.king_cloak_active,
            "activeEffects": self.active_effects.get(viewer_val, []) if viewer_val else [],
            "lastMove": self.last_move.to_dict() if self.last_move else None,
            "moveHistory": [m.to_dict() for m in self.move_history],
        }

    @property
    def last_move(self) -> Move | None:
        """Get the last move made."""
        return self.move_history[-1] if self.move_history else None
