"""Validation logic for targeted effect cards."""
from ...game.models import GameState, PieceColor, Position


def validate_shield_target(
    game: GameState, player_color: PieceColor, target: dict
) -> str | None:
    """Validate shield target is an own piece. Returns error or None."""
    pos = Position.from_dict(target)
    piece = game.board.get_piece(pos)
    if not piece:
        return "Aucune piece sur cette case"
    if piece.color != player_color:
        return "Vous ne pouvez proteger qu'une de vos pieces"
    return None


def validate_freeze_target(
    game: GameState, player_color: PieceColor, target: dict
) -> str | None:
    """Validate freeze target is an enemy piece. Returns error or None."""
    pos = Position.from_dict(target)
    piece = game.board.get_piece(pos)
    if not piece:
        return "Aucune piece sur cette case"
    if piece.color == player_color:
        return "Vous ne pouvez geler qu'une piece ennemie"
    return None


def validate_swap_targets(
    game: GameState, player_color: PieceColor, targets: list[dict]
) -> str | None:
    """Validate swap: 2 own pieces. Returns error or None."""
    if len(targets) != 2:
        return "Selectionnez exactement 2 pieces"
    for t in targets:
        pos = Position.from_dict(t)
        piece = game.board.get_piece(pos)
        if not piece:
            return "Aucune piece sur cette case"
        if piece.color != player_color:
            return "Vous ne pouvez echanger que vos propres pieces"
    return None


def validate_teleport_targets(
    game: GameState, player_color: PieceColor, targets: list[dict]
) -> str | None:
    """Validate teleport: own piece + empty square. Returns error or None."""
    if len(targets) != 2:
        return "Selectionnez une piece puis une case vide"
    piece_pos = Position.from_dict(targets[0])
    dest_pos = Position.from_dict(targets[1])
    piece = game.board.get_piece(piece_pos)
    if not piece:
        return "Aucune piece sur la case source"
    if piece.color != player_color:
        return "Vous ne pouvez teleporter que vos propres pieces"
    dest_piece = game.board.get_piece(dest_pos)
    if dest_piece:
        return "La case de destination doit etre vide"
    return None
