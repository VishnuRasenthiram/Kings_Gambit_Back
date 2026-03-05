"""Targeted card effects: swap, teleport, resurrect."""
from ...game.models import GameState, PieceColor, PieceType, Position, Piece
from .card_validators import validate_swap_targets, validate_teleport_targets

POLICE_PAWN_RANK = 2
MAFIA_PAWN_RANK = 7


def apply_swap(
    game: GameState, color: PieceColor, targets: list[dict]
) -> dict | str:
    """Swap positions of 2 own pieces."""
    err = validate_swap_targets(game, color, targets)
    if err:
        return err
    pos1 = Position.from_dict(targets[0])
    pos2 = Position.from_dict(targets[1])
    piece1 = game.board.get_piece(pos1)
    piece2 = game.board.get_piece(pos2)
    game.board.set_piece(pos1, piece2)
    game.board.set_piece(pos2, piece1)
    return {"effect": "swap", "targets": targets}


def apply_teleport(
    game: GameState, color: PieceColor, targets: list[dict]
) -> dict | str:
    """Teleport own piece to any empty square."""
    err = validate_teleport_targets(game, color, targets)
    if err:
        return err
    src = Position.from_dict(targets[0])
    dest = Position.from_dict(targets[1])
    piece = game.board.get_piece(src)
    game.board.set_piece(src, None)
    game.board.set_piece(dest, piece)
    return {"effect": "teleport", "targets": targets}


def apply_resurrect(
    game: GameState, color: PieceColor
) -> dict | str:
    """Bring back a captured pawn to starting rank."""
    color_val = color.value
    captured = game.captured_pieces.get(color_val, [])
    if PieceType.PAWN.value not in captured:
        return "Aucun pion capture a ressusciter"

    pawn_rank = POLICE_PAWN_RANK if color == PieceColor.POLICE else MAFIA_PAWN_RANK
    empty_pos = _find_empty_on_rank(game, pawn_rank)
    if not empty_pos:
        return "Aucune case libre sur la rangee de depart"

    new_pawn = Piece(type=PieceType.PAWN, color=color)
    game.board.set_piece(empty_pos, new_pawn)
    captured.remove(PieceType.PAWN.value)
    game.captured_pieces[color_val] = captured
    return {
        "effect": "resurrect",
        "position": empty_pos.to_dict(),
    }


def _find_empty_on_rank(game: GameState, rank: int) -> Position | None:
    """Find first empty square on a given rank."""
    from ...game.models import FILES
    for f in FILES:
        pos = Position(file=f, rank=rank)
        if not game.board.get_piece(pos):
            return pos
    return None
