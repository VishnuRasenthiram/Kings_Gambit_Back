"""Chess board representation."""
from dataclasses import dataclass, field
from .piece import Piece, PieceType, PieceColor
from .position import Position, FILES, RANKS


@dataclass
class Square:
    """Represents a square on the board."""
    position: Position
    piece: Piece | None = None

    def to_dict(self) -> dict:
        """Convert square to dictionary."""
        return {
            "position": self.position.to_dict(),
            "piece": self.piece.to_dict() if self.piece else None,
        }


@dataclass
class Board:
    """8x8 chess board."""
    squares: list[list[Square]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize empty board if not provided."""
        if not self.squares:
            self.squares = [
                [Square(Position(f, r)) for f in FILES]
                for r in reversed(RANKS)
            ]

    def get_piece(self, pos: Position) -> Piece | None:
        """Get piece at position."""
        file_idx, rank_idx = pos.to_indices()
        return self.squares[rank_idx][file_idx].piece

    def set_piece(self, pos: Position, piece: Piece | None) -> None:
        """Set piece at position."""
        file_idx, rank_idx = pos.to_indices()
        self.squares[rank_idx][file_idx].piece = piece

    def find_pieces(self, color: PieceColor) -> list[tuple[Position, Piece]]:
        """Find all pieces of a given color."""
        pieces: list[tuple[Position, Piece]] = []
        for rank_idx, row in enumerate(self.squares):
            for file_idx, square in enumerate(row):
                if square.piece and square.piece.color == color:
                    pos = Position.from_indices(file_idx, rank_idx)
                    if pos:
                        pieces.append((pos, square.piece))
        return pieces

    def find_hidden_king(self, color: PieceColor) -> Position | None:
        """Find the hidden king for a color."""
        for pos, piece in self.find_pieces(color):
            if piece.is_hidden_king:
                return pos
        return None

    def copy(self) -> "Board":
        """Create a deep copy of the board."""
        new_board = Board()
        for rank_idx, row in enumerate(self.squares):
            for file_idx, square in enumerate(row):
                if square.piece:
                    new_board.squares[rank_idx][file_idx].piece = Piece(
                        type=square.piece.type,
                        color=square.piece.color,
                        is_hidden_king=square.piece.is_hidden_king,
                    )
        return new_board

    def to_dict(self) -> list[list[dict]]:
        """Convert board to nested list for JSON."""
        return [[sq.to_dict() for sq in row] for row in self.squares]
