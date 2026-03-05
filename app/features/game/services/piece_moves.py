"""Pawn, knight, and king move calculations."""
from ..models import Board, Position, Piece, PieceType, PieceColor, Move, FILES


def _get_pawn_moves(
    board: Board,
    position: Position,
    piece: Piece,
    last_move: Move | None,
) -> list[Position]:
    """Get valid moves for a pawn."""
    moves: list[Position] = []
    file_idx, rank_idx = position.to_indices()
    direction = 1 if piece.color == PieceColor.POLICE else -1
    start_rank = 2 if piece.color == PieceColor.POLICE else 7
    en_passant_rank = 5 if piece.color == PieceColor.POLICE else 4

    # Forward one square
    new_rank_idx = rank_idx + direction
    if 0 <= new_rank_idx < 8:
        forward_pos = Position.from_indices(file_idx, new_rank_idx)
        if forward_pos and not board.get_piece(forward_pos):
            moves.append(forward_pos)

            # Forward two squares from start
            if position.rank == start_rank:
                two_rank_idx = rank_idx + direction * 2
                two_pos = Position.from_indices(file_idx, two_rank_idx)
                if two_pos and not board.get_piece(two_pos):
                    moves.append(two_pos)

    # Diagonal captures
    for file_delta in [-1, 1]:
        new_file_idx = file_idx + file_delta
        if 0 <= new_file_idx < 8 and 0 <= new_rank_idx < 8:
            capture_pos = Position.from_indices(new_file_idx, new_rank_idx)
            if capture_pos:
                target = board.get_piece(capture_pos)
                if target and target.color != piece.color:
                    moves.append(capture_pos)

    # En passant
    if (
        last_move and position.rank == en_passant_rank
        and last_move.piece.type == PieceType.PAWN
        and last_move.piece.color != piece.color
        and abs(last_move.from_pos.rank - last_move.to_pos.rank) == 2
    ):
        last_file_idx = FILES.index(last_move.to_pos.file)
        if abs(last_file_idx - file_idx) == 1:
            ep_pos = Position.from_indices(last_file_idx, new_rank_idx)
            if ep_pos:
                moves.append(ep_pos)

    return moves


def _get_knight_moves(board: Board, pos: Position, piece: Piece) -> list[Position]:
    """Get valid moves for a knight."""
    moves: list[Position] = []
    file_idx, rank_idx = pos.to_indices()

    knight_offsets = [
        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
        (1, -2), (1, 2), (2, -1), (2, 1),
    ]

    for d_file, d_rank in knight_offsets:
        new_file = file_idx + d_file
        new_rank = rank_idx + d_rank
        if 0 <= new_file < 8 and 0 <= new_rank < 8:
            new_pos = Position.from_indices(new_file, new_rank)
            if new_pos:
                target = board.get_piece(new_pos)
                if not target or target.color != piece.color:
                    moves.append(new_pos)

    return moves


def _get_king_moves(
    board: Board,
    pos: Position,
    piece: Piece,
    moved_pieces: set[str],
) -> list[Position]:
    """Get valid moves for a king (including castling)."""
    moves: list[Position] = []
    file_idx, rank_idx = pos.to_indices()

    # Normal moves
    for d_file in [-1, 0, 1]:
        for d_rank in [-1, 0, 1]:
            if d_file == 0 and d_rank == 0:
                continue
            new_file = file_idx + d_file
            new_rank = rank_idx + d_rank
            if 0 <= new_file < 8 and 0 <= new_rank < 8:
                new_pos = Position.from_indices(new_file, new_rank)
                if new_pos:
                    target = board.get_piece(new_pos)
                    if not target or target.color != piece.color:
                        moves.append(new_pos)

    # Castling
    king_start_rank = 1 if piece.color == PieceColor.POLICE else 8
    king_key = f"e{king_start_rank}"

    if pos.file == "e" and pos.rank == king_start_rank and king_key not in moved_pieces:
        # Kingside
        if f"h{king_start_rank}" not in moved_pieces:
            rook_pos = Position(file="h", rank=king_start_rank)  # type: ignore
            rook = board.get_piece(rook_pos)
            if rook and rook.type == PieceType.ROOK:
                # type: ignore
                f_pos = Position(file="f", rank=king_start_rank)
                # type: ignore
                g_pos = Position(file="g", rank=king_start_rank)
                if not board.get_piece(f_pos) and not board.get_piece(g_pos):
                    moves.append(g_pos)

        # Queenside
        if f"a{king_start_rank}" not in moved_pieces:
            rook_pos = Position(file="a", rank=king_start_rank)  # type: ignore
            rook = board.get_piece(rook_pos)
            if rook and rook.type == PieceType.ROOK:
                # type: ignore
                b_pos = Position(file="b", rank=king_start_rank)
                # type: ignore
                c_pos = Position(file="c", rank=king_start_rank)
                # type: ignore
                d_pos = Position(file="d", rank=king_start_rank)
                if not board.get_piece(b_pos) and not board.get_piece(c_pos) and not board.get_piece(d_pos):
                    moves.append(c_pos)

    return moves
