"""Check and checkmate detection for the hidden king."""
from ..models import Board, Position, PieceColor
from .move_calculator import get_valid_moves


def find_hidden_king_position(board: Board, color: PieceColor) -> Position | None:
    """Find the position of the hidden king."""
    return board.find_hidden_king(color)


def is_position_attacked(
    board: Board,
    position: Position,
    by_color: PieceColor,
) -> bool:
    """Check if a position is attacked by any piece of the given color."""
    for pos, piece in board.find_pieces(by_color):
        valid_moves = get_valid_moves(board, pos)
        if position in valid_moves:
            return True
    return False


def is_hidden_king_in_check(board: Board, king_color: PieceColor) -> bool:
    """Check if the hidden king is in check."""
    king_pos = find_hidden_king_position(board, king_color)
    if not king_pos:
        return False

    opponent = PieceColor.MAFIA if king_color == PieceColor.POLICE else PieceColor.POLICE
    return is_position_attacked(board, king_pos, opponent)


def is_visible_king_in_check(board: Board, king_color: PieceColor) -> bool:
    """Check if the visible king (decoy) is in check."""
    # Find the visible king (PieceType.KING of that color)
    for pos, piece in board.find_pieces(king_color):
        from ..models import PieceType
        if piece.type == PieceType.KING:
            opponent = PieceColor.MAFIA if king_color == PieceColor.POLICE else PieceColor.POLICE
            return is_position_attacked(board, pos, opponent)
    return False


def simulate_move(board: Board, from_pos: Position, to_pos: Position) -> Board:
    """Simulate a move and return the new board state."""
    new_board = board.copy()
    piece = new_board.get_piece(from_pos)
    new_board.set_piece(from_pos, None)
    new_board.set_piece(to_pos, piece)
    return new_board


def can_escape_check(board: Board, king_color: PieceColor) -> bool:
    """Check if the player can make any move to escape check."""
    for pos, piece in board.find_pieces(king_color):
        valid_moves = get_valid_moves(board, pos)
        for move in valid_moves:
            simulated = simulate_move(board, pos, move)
            if not is_hidden_king_in_check(simulated, king_color):
                return True
    return False


def is_hidden_king_checkmated(board: Board, king_color: PieceColor) -> bool:
    """Check if the hidden king is checkmated."""
    if not is_hidden_king_in_check(board, king_color):
        return False
    return not can_escape_check(board, king_color)


def is_hidden_king_captured(board: Board, color: PieceColor) -> bool:
    """Check if the hidden king has been captured."""
    return find_hidden_king_position(board, color) is None
