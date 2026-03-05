"""Game WebSocket handler."""
import uuid
import socketio
from ..models import GameState, GamePhase, PieceColor, PieceType, Position
from ..models.game_state import HiddenKingState, VictoryReason
from ..services import (
    initialize_board,
    get_valid_moves,
    is_hidden_king_in_check,
    is_hidden_king_checkmated,
    is_hidden_king_captured,
)


# In-memory game storage (replace with DB for production)
games: dict[str, GameState] = {}

GAME_NOT_FOUND_MSG = "Game not found"
player_rooms: dict[str, str] = {}  # sid -> room_id
player_colors: dict[str, PieceColor] = {}  # sid -> color


async def broadcast_game_state(sio: socketio.AsyncServer, room_id: str) -> None:
    """Send personalized game state to each player in the room."""
    if room_id not in games:
        return

    game = games[room_id]
    room_sids = [sid for sid, rid in player_rooms.items() if rid == room_id]

    for sid in room_sids:
        player_color = player_colors.get(sid)
        await sio.emit(
            "game_state",
            game.to_dict(viewer_color=player_color),
            to=sid,
        )


def register_game_handlers(sio: socketio.AsyncServer) -> None:
    """Register Socket.IO event handlers for game logic."""

    @sio.event
    async def connect(sid: str, environ: dict) -> None:
        print(f"Client connected: {sid}")

    @sio.event
    async def disconnect(sid: str) -> None:
        print(f"Client disconnected: {sid}")
        if sid in player_rooms:
            room_id = player_rooms.pop(sid)
            player_colors.pop(sid, None)
            await sio.emit("player_left", room=room_id)

    @sio.on("create_game")
    async def handle_create_game(sid: str) -> None:
        """Create a new game room."""
        room_id = str(uuid.uuid4())[:8].upper()

        board = initialize_board()
        games[room_id] = GameState(game_id=room_id, board=board)

        # Randomly assign color to creator
        import random
        creator_color = random.choice([PieceColor.POLICE, PieceColor.MAFIA])

        await sio.enter_room(sid, room_id)
        player_rooms[sid] = room_id
        player_colors[sid] = creator_color

        await sio.emit(
            "game_created",
            {
                "game_id": room_id,
                "player_color": creator_color.value,
            },
            to=sid,
        )
        print(f"Game created: {room_id} by {sid} as {creator_color.value}")

    @sio.on("join_game")
    async def handle_join_game(sid: str, data: dict) -> None:
        """Join an existing game room."""
        room_id = data.get("game_id", "").upper()

        if room_id not in games:
            await sio.emit(
                "error",
                {"message": "Partie introuvable", "code": "GAME_NOT_FOUND"},
                to=sid,
            )
            return

        game = games[room_id]

        # Check if game is full
        room_players = [s for s, r in player_rooms.items() if r == room_id]
        if len(room_players) >= 2:
            await sio.emit(
                "error",
                {"message": "Partie complète", "code": "GAME_FULL"},
                to=sid,
            )
            return

        # Determine available color
        existing_player_sid = room_players[0]
        existing_player_color = player_colors.get(existing_player_sid)

        # Assign opposite color
        joiner_color = PieceColor.MAFIA if existing_player_color == PieceColor.POLICE else PieceColor.POLICE

        await sio.enter_room(sid, room_id)
        player_rooms[sid] = room_id
        player_colors[sid] = joiner_color

        # Notify the joiner
        await sio.emit(
            "game_joined",
            {
                "game_id": room_id,
                "player_color": joiner_color.value,
                "opponent_connected": True,
            },
            to=sid,
        )

        # Notify the creator that opponent joined
        await sio.emit(
            "opponent_joined",
            {},
            room=room_id,
            skip_sid=sid,
        )

        # Broadcast initial state to both players
        await broadcast_game_state(sio, room_id)

        print(f"Player {sid} joined game: {room_id}")

    @sio.on("rejoin_game")
    async def handle_rejoin_game(sid: str, data: dict) -> None:
        """Rejoin an existing game after page refresh."""
        room_id = data.get("game_id", "").upper()
        requested_color = data.get("player_color", "")

        if room_id not in games:
            await sio.emit(
                "error",
                {"message": "Partie introuvable ou expirée",
                    "code": "GAME_NOT_FOUND"},
                to=sid,
            )
            return

        game = games[room_id]

        # Check if this color slot is available (player disconnected)
        room_players = [(s, player_colors.get(s))
                        for s, r in player_rooms.items() if r == room_id]
        color_taken = any(color == requested_color for _,
                          color in room_players)

        if color_taken:
            await sio.emit(
                "error",
                {"message": "Cette place est déjà prise", "code": "SLOT_TAKEN"},
                to=sid,
            )
            return

        # Rejoin the game
        await sio.enter_room(sid, room_id)
        player_rooms[sid] = room_id
        player_colors[sid] = PieceColor(requested_color)

        # Check if opponent is connected
        opponent_connected = len(
            [s for s, r in player_rooms.items() if r == room_id]) > 1

        await sio.emit(
            "game_rejoined",
            {
                "game_id": room_id,
                "player_color": requested_color,
                "opponent_connected": opponent_connected,
            },
            to=sid,
        )

        # Notify opponent that player reconnected
        if opponent_connected:
            await sio.emit(
                "opponent_rejoined",
                {},
                room=room_id,
                skip_sid=sid,
            )

        # Send current game state
        await broadcast_game_state(sio, room_id)

        print(f"Player {sid} rejoined game: {room_id} as {requested_color}")

    @sio.on("select_hidden_king")
    async def handle_select_hidden_king(sid: str, data: dict) -> None:
        room_id = player_rooms.get(sid)
        if not room_id or room_id not in games:
            await sio.emit("error", {"message": GAME_NOT_FOUND_MSG, "code": "GAME_NOT_FOUND"}, to=sid)
            return

        game = games[room_id]
        if game.phase != GamePhase.SETUP:
            await sio.emit("error", {"message": "Wrong game phase", "code": "WRONG_PHASE"}, to=sid)
            return

        piece_type = PieceType(data.get("king_type"))
        player_color = player_colors.get(sid)

        if not player_color:
            return

        # Check if already selected
        if game.hidden_kings[player_color.value] is not None:
            return

        # Find valid pieces of this type and pick one at random
        import random
        valid_positions = [pos for pos, piece in game.board.find_pieces(
            player_color) if piece.type == piece_type]

        if not valid_positions:
            await sio.emit("error", {"message": "Aucune pièce de ce type disponible", "code": "INVALID_PIECE"}, to=sid)
            return

        king_pos = random.choice(valid_positions)
        piece = game.board.get_piece(king_pos)
        if piece:
            piece.is_hidden_king = True

        game.hidden_kings[player_color.value] = HiddenKingState(
            card=piece_type)

        await sio.emit(
            "hidden_king_selected",
            {"color": player_color.value},
            room=room_id,
        )

        # Transition to playing if both selected
        if game.hidden_kings["police"] and game.hidden_kings["mafia"]:
            game.phase = GamePhase.PLAYING

        await broadcast_game_state(sio, room_id)

    @sio.on("make_move")
    async def handle_make_move(sid: str, data: dict) -> None:
        room_id = player_rooms.get(sid)
        if not room_id or room_id not in games:
            await sio.emit("error", {"message": GAME_NOT_FOUND_MSG, "code": "GAME_NOT_FOUND"}, to=sid)
            return

        game = games[room_id]

        # Check if it's this player's turn
        player_color = player_colors.get(sid)
        if player_color != game.current_turn:
            await sio.emit("error", {"message": "Ce n'est pas votre tour", "code": "NOT_YOUR_TURN"}, to=sid)
            return

        from_pos = Position.from_dict(data["from"])
        to_pos = Position.from_dict(data["to"])

        # Validate and execute move
        piece = game.board.get_piece(from_pos)
        if not piece or piece.color != game.current_turn:
            await sio.emit("error", {"message": "Mouvement invalide", "code": "INVALID_MOVE"}, to=sid)
            return

        # Check if piece is frozen
        frozen = game.frozen_pieces.get(player_color.value, [])
        if any(p["file"] == from_pos.file and p["rank"] == from_pos.rank for p in frozen):
            await sio.emit("error", {"message": "Cette piece est gelee !", "code": "PIECE_FROZEN"}, to=sid)
            return

        valid_moves = get_valid_moves(
            game.board, from_pos, game.last_move, game.moved_pieces,
            active_effects=game.active_effects.get(player_color.value, [])
        )
        if to_pos not in valid_moves:
            await sio.emit("error", {"message": "Mouvement invalide", "code": "INVALID_MOVE"}, to=sid)
            return

        # NEW: Verify that the move does not leave (or put) the player in check
        # We simulate the move on a copy of the board
        from ..services.check_detector import simulate_move, is_hidden_king_in_check, is_visible_king_in_check

        simulated_board = simulate_move(game.board, from_pos, to_pos)

        # Check if Hidden King is in check
        if is_hidden_king_in_check(simulated_board, game.current_turn):
            await sio.emit("error", {"message": "Ce mouvement laisse votre Roi Caché en échec !", "code": "MOVE_IN_CHECK"}, to=sid)
            return

        # Check if Visible King (decoy) is in check - STANDARD CHESS RULES ALSO APPLY
        if is_visible_king_in_check(simulated_board, game.current_turn):
            await sio.emit("error", {"message": "Ce mouvement laisse votre Roi (visible) en échec !", "code": "MOVE_IN_CHECK"}, to=sid)
            return

        # Check shield and king_cloak on target
        captured = game.board.get_piece(to_pos)
        if captured:
            target_color = captured.color.value
            shielded = game.shielded_pieces.get(target_color, [])
            if any(p["file"] == to_pos.file and p["rank"] == to_pos.rank for p in shielded):
                await sio.emit("error", {"message": "Cette piece est protegee !", "code": "PIECE_SHIELDED"}, to=sid)
                return
            if captured.is_hidden_king and game.king_cloak_active.get(target_color, False):
                await sio.emit("error", {"message": "Le roi cache est protege !", "code": "KING_CLOAKED"}, to=sid)
                return

        # Execute move
        piece.has_moved = True
        game.board.set_piece(from_pos, None)
        game.board.set_piece(to_pos, piece)
        game.moved_pieces.add(f"{from_pos.file}{from_pos.rank}")

        # Properly update move history
        from ..models.move import Move
        new_move = Move(from_pos=from_pos, to_pos=to_pos,
                        piece=piece, captured_piece=captured)
        game.move_history.append(new_move)

        # Check for game over conditions
        opponent = PieceColor.MAFIA if game.current_turn == PieceColor.POLICE else PieceColor.POLICE

        if is_hidden_king_captured(game.board, opponent):
            game.winner = game.current_turn
            game.victory_reason = VictoryReason.CAPTURE
            game.phase = GamePhase.GAME_OVER
        elif is_hidden_king_checkmated(game.board, opponent):
            game.winner = game.current_turn
            game.victory_reason = VictoryReason.CHECKMATE
            game.phase = GamePhase.GAME_OVER

        # Track captured piece for resurrect
        if captured:
            game.captured_pieces[captured.color.value].append(
                captured.type.value)

        # Clear active effects for current player
        cur = game.current_turn.value
        game.active_effects[cur] = []
        game.shielded_pieces[cur] = []
        game.king_cloak_active[cur] = False
        game.frozen_pieces[cur] = []

        # Check if opponent is in check
        in_check = is_hidden_king_in_check(game.board, opponent)

        # Handle double_move: don't switch turn
        if game.double_move_pending.get(cur, False):
            game.double_move_pending[cur] = False
        else:
            game.current_turn = opponent
            game.card_used_this_turn[opponent.value] = False

        await sio.emit(
            "move_made",
            {
                "from": from_pos.to_dict(),
                "to": to_pos.to_dict(),
                "captured": captured.to_dict() if captured else None,
            },
            room=room_id,
        )

        # Card draw: only on major piece capture, only for capturing player
        major_types = {PieceType.QUEEN, PieceType.ROOK,
                       PieceType.BISHOP, PieceType.KNIGHT}
        if captured and game.phase != GamePhase.GAME_OVER and captured.type in major_types:
            from ...cards.models.effect_cards import draw_effect_card
            card = draw_effect_card()
            game.effect_cards[player_color.value].append(card.value)
            await sio.emit(
                "card_drawn",
                {"card": card.value, "for_player": player_color.value},
                to=sid,
            )

        # Send updated game state to each player securely
        await broadcast_game_state(sio, room_id)

        if in_check:
            await sio.emit(
                "check",
                {"color": opponent.value},
                room=room_id,
            )

        if game.phase == GamePhase.GAME_OVER:
            await sio.emit(
                "game_over",
                {
                    "winner": game.winner.value if game.winner else None,
                    "reason": game.victory_reason.value if game.victory_reason else None,
                },
                room=room_id,
            )

    @sio.on("resign")
    async def handle_resign(sid: str) -> None:
        """Handle player resignation."""
        room_id = player_rooms.get(sid)
        if not room_id or room_id not in games:
            return

        game = games[room_id]
        player_color = player_colors.get(sid)

        if player_color:
            game.winner = PieceColor.MAFIA if player_color == PieceColor.POLICE else PieceColor.POLICE
            game.victory_reason = VictoryReason.RESIGNATION
            game.phase = GamePhase.GAME_OVER

            await sio.emit(
                "game_over",
                {
                    "winner": game.winner.value,
                    "reason": "resignation",
                },
                room=room_id,
            )

    @sio.on("use_card")
    async def handle_use_card(sid: str, data: dict) -> None:
        """Handle using an effect card from hand."""
        room_id = player_rooms.get(sid)
        if not room_id or room_id not in games:
            await sio.emit("error", {"message": GAME_NOT_FOUND_MSG, "code": "GAME_NOT_FOUND"}, to=sid)
            return

        game = games[room_id]
        player_color = player_colors.get(sid)
        if player_color != game.current_turn:
            await sio.emit("error", {"message": "Ce n'est pas votre tour", "code": "NOT_YOUR_TURN"}, to=sid)
            return

        if game.card_used_this_turn.get(player_color.value, False):
            await sio.emit("error", {"message": "Deja utilise une carte ce tour", "code": "CARD_ALREADY_USED"}, to=sid)
            return

        card_type = data.get("card")
        if not card_type:
            await sio.emit("error", {"message": "No card specified", "code": "NO_CARD"}, to=sid)
            return

        player_hand = game.effect_cards.get(player_color.value, [])
        if card_type not in player_hand:
            await sio.emit("error", {"message": "Carte absente de la main", "code": "CARD_NOT_IN_HAND"}, to=sid)
            return

        targets = data.get("targets", [])
        from ...cards.services.card_effects import apply_card_effect
        result = apply_card_effect(game, player_color, card_type, targets)

        if isinstance(result, str):
            await sio.emit("error", {"message": result, "code": "CARD_ERROR"}, to=sid)
            return

        player_hand.remove(card_type)
        game.effect_cards[player_color.value] = player_hand
        game.card_used_this_turn[player_color.value] = True

        await sio.emit("card_used", {"card": card_type, "player": player_color.value, **result}, room=room_id)

        if card_type == "spy" and "spy_king_type" in result:
            await sio.emit("spy_reveal", {"king_type": result["spy_king_type"]}, to=sid)
        if card_type == "reveal_hint" and "hint" in result:
            await sio.emit("reveal_hint_result", {"hint": result["hint"]}, to=sid)

        await broadcast_game_state(sio, room_id)
