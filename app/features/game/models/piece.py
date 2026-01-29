"""Piece types and colors for the chess game."""
from enum import Enum
from dataclasses import dataclass


class PieceType(str, Enum):
    """Types of chess pieces."""
    KING = "king"
    QUEEN = "queen"
    ROOK = "rook"
    BISHOP = "bishop"
    KNIGHT = "knight"
    PAWN = "pawn"


class PieceColor(str, Enum):
    """Player colors/teams."""
    POLICE = "police"
    MAFIA = "mafia"


@dataclass
class Piece:
    """Represents a chess piece on the board."""
    type: PieceType
    color: PieceColor
    is_hidden_king: bool = False
    has_moved: bool = False

    def to_dict(self) -> dict:
        """Convert piece to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "color": self.color.value,
            "isHiddenKing": self.is_hidden_king,
            "hasMoved": self.has_moved,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Piece":
        """Create a Piece from a dictionary."""
        return cls(
            type=PieceType(data["type"]),
            color=PieceColor(data["color"]),
            is_hidden_king=data.get("isHiddenKing", False),
            has_moved=data.get("hasMoved", False),
        )

