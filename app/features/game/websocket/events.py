"""WebSocket event constants."""

# Client -> Server events
class ClientEvents:
    """Events sent from client to server."""
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    SELECT_HIDDEN_KING = "select_hidden_king"
    MAKE_MOVE = "make_move"
    DRAW_CARD = "draw_card"


# Server -> Client events
class ServerEvents:
    """Events sent from server to client."""
    ROOM_JOINED = "room_joined"
    OPPONENT_JOINED = "opponent_joined"
    GAME_STARTED = "game_started"
    HIDDEN_KING_SELECTED = "hidden_king_selected"
    MOVE_MADE = "move_made"
    CHECK = "check"
    GAME_OVER = "game_over"
    CARD_DRAWN = "card_drawn"
    ERROR = "error"
    PLAYER_LEFT = "player_left"
