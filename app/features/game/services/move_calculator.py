from ..models import Board, Position, Piece, PieceType, PieceColor, Move, FILES
from .piece_moves import _get_pawn_moves, _get_knight_moves, _get_king_moves


def get_valid_moves(
    board: Board,
    position: Position,
    last_move: Move | None = None,
    moved_pieces: set[str] | None = None,
    active_effects: list[str] | None = None,
    revealed_hidden_king: bool = False,
) -> list[Position]:
    """Get all valid moves for a piece at the given position.

    Args:
        active_effects: List of active effect card types that modify movement.
            - knight_boost: Pawns can move like knights
            - diagonal_rook: Rooks can also move diagonally
            - pawn_charge: All pawns can move 2 squares forward
        revealed_hidden_king: If True, the hidden king moves like a king
            regardless of its disguised piece type.
    """
    piece = board.get_piece(position)
    if not piece:
        return []

    moved = moved_pieces or set()
    effects = active_effects or []

    # Revealed hidden king moves like a king regardless of disguised piece type
    if revealed_hidden_king and piece.is_hidden_king:
        return _get_king_moves(board, position, piece, moved)

    match piece.type:
        case PieceType.PAWN:
            moves = _get_pawn_moves(board, position, piece, last_move)
            # knight_boost: Pawn can move like a knight this turn
            if "knight_boost" in effects:
                knight_moves = _get_knight_moves(board, position, piece)
                moves.extend([m for m in knight_moves if m not in moves])
            # pawn_charge: All pawns can move 2 squares forward
            if "pawn_charge" in effects:
                moves = _get_pawn_moves_with_charge(
                    board, position, piece, last_move)
            return moves
        case PieceType.ROOK:
            moves = _get_rook_moves(board, position, piece)
            # diagonal_rook: Rook can also move diagonally this turn
            if "diagonal_rook" in effects:
                diagonal_moves = _get_bishop_moves(board, position, piece)
                moves.extend([m for m in diagonal_moves if m not in moves])
            return moves
        case PieceType.BISHOP:
            return _get_bishop_moves(board, position, piece)
        case PieceType.QUEEN:
            return _get_queen_moves(board, position, piece)
        case PieceType.KNIGHT:
            return _get_knight_moves(board, position, piece)
        case PieceType.KING:
            return _get_king_moves(board, position, piece, moved)
        case _:
            return []


def _get_pawn_moves_with_charge(
    board: Board,
    position: Position,
    piece: Piece,
    last_move: Move | None = None,
) -> list[Position]:
    """Get pawn moves with pawn_charge effect (can always move 2 squares)."""
    moves = _get_pawn_moves(board, position, piece, last_move)

    direction = 1 if piece.color == PieceColor.POLICE else -1
    file_idx, rank_idx = position.to_indices()

    # Always allow 2-square move if paths are clear
    one_ahead = rank_idx + direction
    two_ahead = rank_idx + (2 * direction)

    if 0 <= two_ahead < 8:
        one_pos = Position.from_indices(file_idx, one_ahead)
        two_pos = Position.from_indices(file_idx, two_ahead)

        if one_pos and two_pos:
            if not board.get_piece(one_pos) and not board.get_piece(two_pos):
                if two_pos not in moves:
                    moves.append(two_pos)

    return moves


def _is_valid_position(file_idx: int, rank_idx: int) -> bool:
    """Check if indices are within board bounds."""
    return 0 <= file_idx < 8 and 0 <= rank_idx < 8


def _add_move_if_valid(
    moves: list[Position],
    board: Board,
    file_idx: int,
    rank_idx: int,
    piece_color: PieceColor,
    can_capture: bool = True,
    must_capture: bool = False,
) -> bool:
    """Add move if valid, return True if can continue sliding."""
    if not _is_valid_position(file_idx, rank_idx):
        return False

    pos = Position.from_indices(file_idx, rank_idx)
    if not pos:
        return False

    target = board.get_piece(pos)

    if target:
        if can_capture and target.color != piece_color:
            moves.append(pos)
        return False

    if not must_capture:
        moves.append(pos)
    return True


def _get_sliding_moves(
    board: Board,
    position: Position,
    piece: Piece,
    directions: list[tuple[int, int]],
) -> list[Position]:
    """Get moves for sliding pieces (rook, bishop, queen)."""
    moves: list[Position] = []
    file_idx, rank_idx = position.to_indices()

    for d_file, d_rank in directions:
        for i in range(1, 8):
            can_continue = _add_move_if_valid(
                moves, board,
                file_idx + d_file * i,
                rank_idx + d_rank * i,
                piece.color,
            )
            if not can_continue:
                break

    return moves


def _get_rook_moves(board: Board, pos: Position, piece: Piece) -> list[Position]:
    """Get valid moves for a rook."""
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    return _get_sliding_moves(board, pos, piece, directions)


def _get_bishop_moves(board: Board, pos: Position, piece: Piece) -> list[Position]:
    """Get valid moves for a bishop."""
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return _get_sliding_moves(board, pos, piece, directions)


def _get_queen_moves(board: Board, pos: Position, piece: Piece) -> list[Position]:
    """Get valid moves for a queen."""
    return _get_rook_moves(board, pos, piece) + _get_bishop_moves(board, pos, piece)
