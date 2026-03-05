"""Board initialization service."""
from ..models import Board, Piece, PieceType, PieceColor, Position


def initialize_board() -> Board:
    """Create a new board with pieces in starting positions."""
    board = Board()

    # Setup pieces for both sides
    _setup_back_rank(board, 1, PieceColor.POLICE)
    _setup_pawns(board, 2, PieceColor.POLICE)
    _setup_pawns(board, 7, PieceColor.MAFIA)
    _setup_back_rank(board, 8, PieceColor.MAFIA)

    return board


def _setup_back_rank(board: Board, rank: int, color: PieceColor) -> None:
    """Setup the back rank with major pieces."""
    piece_order = [
        PieceType.ROOK,
        PieceType.KNIGHT,
        PieceType.BISHOP,
        PieceType.QUEEN,
        PieceType.KING,
        PieceType.BISHOP,
        PieceType.KNIGHT,
        PieceType.ROOK,
    ]
    files = ["a", "b", "c", "d", "e", "f", "g", "h"]

    for file, piece_type in zip(files, piece_order):
        pos = Position(file=file, rank=rank)  # type: ignore
        board.set_piece(pos, Piece(type=piece_type, color=color))


def _setup_pawns(board: Board, rank: int, color: PieceColor) -> None:
    """Setup pawns on the given rank."""
    files = ["a", "b", "c", "d", "e", "f", "g", "h"]

    for file in files:
        pos = Position(file=file, rank=rank)  # type: ignore
        board.set_piece(pos, Piece(type=PieceType.PAWN, color=color))
