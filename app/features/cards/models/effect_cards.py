"""Effect cards for the game."""
from enum import Enum
import random


class EffectCardType(str, Enum):
    """Types of effect cards."""
    DOUBLE_MOVE = "double_move"
    SHIELD = "shield"
    REVEAL_HINT = "reveal_hint"
    SWAP = "swap"
    RESURRECT = "resurrect"
    FREEZE = "freeze"
    TELEPORT = "teleport"
    KNIGHT_BOOST = "knight_boost"
    DIAGONAL_ROOK = "diagonal_rook"
    PAWN_CHARGE = "pawn_charge"
    KING_CLOAK = "king_cloak"
    SPY = "spy"


class EffectCardRarity(str, Enum):
    """Rarity levels for effect cards."""
    COMMON = "common"
    RARE = "rare"
    LEGENDARY = "legendary"


# Card rarity mapping
CARD_RARITIES: dict[EffectCardType, EffectCardRarity] = {
    EffectCardType.DOUBLE_MOVE: EffectCardRarity.RARE,
    EffectCardType.SHIELD: EffectCardRarity.COMMON,
    EffectCardType.REVEAL_HINT: EffectCardRarity.COMMON,
    EffectCardType.SWAP: EffectCardRarity.COMMON,
    EffectCardType.RESURRECT: EffectCardRarity.RARE,
    EffectCardType.FREEZE: EffectCardRarity.COMMON,
    EffectCardType.TELEPORT: EffectCardRarity.RARE,
    EffectCardType.KNIGHT_BOOST: EffectCardRarity.COMMON,
    EffectCardType.DIAGONAL_ROOK: EffectCardRarity.RARE,
    EffectCardType.PAWN_CHARGE: EffectCardRarity.COMMON,
    EffectCardType.KING_CLOAK: EffectCardRarity.LEGENDARY,
    EffectCardType.SPY: EffectCardRarity.LEGENDARY,
}

# Cards by rarity
COMMON_CARDS = [c for c, r in CARD_RARITIES.items() if r == EffectCardRarity.COMMON]
RARE_CARDS = [c for c, r in CARD_RARITIES.items() if r == EffectCardRarity.RARE]
LEGENDARY_CARDS = [c for c, r in CARD_RARITIES.items() if r == EffectCardRarity.LEGENDARY]


def draw_effect_card() -> EffectCardType:
    """Draw a random effect card based on rarity probabilities."""
    roll = random.random() * 100
    
    if roll < 60:
        # 60% - Common
        return random.choice(COMMON_CARDS)
    elif roll < 90:
        # 30% - Rare
        return random.choice(RARE_CARDS)
    else:
        # 10% - Legendary
        return random.choice(LEGENDARY_CARDS)
