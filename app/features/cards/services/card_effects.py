"""Card effect application logic for all 12 effect cards."""
from ...game.models import GameState, PieceColor, PieceType
from .card_validators import validate_shield_target, validate_freeze_target
from .card_effects_targeted import apply_swap, apply_teleport, apply_resurrect

MOVEMENT_CARDS = ["knight_boost", "diagonal_rook", "pawn_charge"]
MAJOR_HINT = {PieceType.QUEEN, PieceType.ROOK}
MINOR_HINT = {PieceType.BISHOP, PieceType.KNIGHT, PieceType.PAWN}


def apply_card_effect(
    game: GameState,
    player_color: PieceColor,
    card_type: str,
    targets: list[dict],
) -> dict | str:
    """Apply a card effect. Returns result dict or error string."""
    match card_type:
        case "double_move":
            return _apply_double_move(game, player_color)
        case "reveal_hint":
            return _apply_reveal_hint(game, player_color)
        case "spy":
            return _apply_spy(game, player_color)
        case "king_cloak":
            return _apply_king_cloak(game, player_color)
        case "shield":
            return _apply_shield(game, player_color, targets)
        case "freeze":
            return _apply_freeze(game, player_color, targets)
        case "swap":
            return apply_swap(game, player_color, targets)
        case "teleport":
            return apply_teleport(game, player_color, targets)
        case "resurrect":
            return apply_resurrect(game, player_color)
        case _ if card_type in MOVEMENT_CARDS:
            game.active_effects[player_color.value].append(card_type)
            return {"effect": card_type}
        case _:
            return "Effet de carte inconnu"


def _apply_double_move(game: GameState, color: PieceColor) -> dict:
    """Allow player to play a second move this turn."""
    game.double_move_pending[color.value] = True
    return {"effect": "double_move"}


def _apply_reveal_hint(game: GameState, color: PieceColor) -> dict:
    """Reveal if opponent hidden king is major or minor."""
    opponent = "mafia" if color == PieceColor.POLICE else "police"
    hk = game.hidden_kings.get(opponent)
    if not hk:
        return {"hint": "unknown"}
    hint = "majeure" if hk.card in MAJOR_HINT else "mineure"
    return {"hint": hint, "effect": "reveal_hint"}


def _apply_spy(game: GameState, color: PieceColor) -> dict:
    """Reveal opponent hidden king type for 3 seconds."""
    opponent = "mafia" if color == PieceColor.POLICE else "police"
    hk = game.hidden_kings.get(opponent)
    if not hk:
        return {"spy_king_type": "unknown", "effect": "spy"}
    return {"spy_king_type": hk.card.value, "effect": "spy"}


def _apply_king_cloak(game: GameState, color: PieceColor) -> dict:
    """Protect hidden king from capture this turn."""
    game.king_cloak_active[color.value] = True
    return {"effect": "king_cloak"}


def _apply_shield(
    game: GameState, color: PieceColor, targets: list[dict]
) -> dict | str:
    """Shield one own piece from capture for 1 turn."""
    if len(targets) < 1:
        return "Selectionnez une piece a proteger"
    err = validate_shield_target(game, color, targets[0])
    if err:
        return err
    game.shielded_pieces[color.value].append(targets[0])
    return {"effect": "shield", "target": targets[0]}


def _apply_freeze(
    game: GameState, color: PieceColor, targets: list[dict]
) -> dict | str:
    """Freeze one enemy piece for 1 turn."""
    if len(targets) < 1:
        return "Selectionnez une piece ennemie a geler"
    err = validate_freeze_target(game, color, targets[0])
    if err:
        return err
    opponent = "mafia" if color == PieceColor.POLICE else "police"
    game.frozen_pieces[opponent].append(targets[0])
    return {"effect": "freeze", "target": targets[0]}
