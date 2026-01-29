"""Move representation for chess game."""
from dataclasses import dataclass
from .position import Position
from .piece import Piece


@dataclass
class Move:
    """Represents a chess move."""
    from_pos: Position
    to_pos: Position
    piece: Piece
    captured_piece: Piece | None = None
    is_en_passant: bool = False
    is_castling: bool = False
    is_promotion: bool = False
    promotion_type: str | None = None

    def to_dict(self) -> dict:
        """Convert move to dictionary."""
        return {
            "from": self.from_pos.to_dict(),
            "to": self.to_pos.to_dict(),
            "piece": self.piece.to_dict(),
            "capturedPiece": self.captured_piece.to_dict() if self.captured_piece else None,
            "isEnPassant": self.is_en_passant,
            "isCastling": self.is_castling,
            "isPromotion": self.is_promotion,
            "promotionType": self.promotion_type,
        }
