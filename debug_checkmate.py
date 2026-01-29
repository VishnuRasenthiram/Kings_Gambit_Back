"""Quick debug script to trace the checkmate detection."""
from app.features.game.models import Board, Piece, PieceType, PieceColor, Position
from app.features.game.services import is_hidden_king_in_check, is_hidden_king_checkmated, initialize_board
from app.features.game.services.check_detector import can_escape_check
from app.features.game.services.move_calculator import get_valid_moves


def place_piece(board: Board, file: str, rank: int, piece_type: PieceType, color: PieceColor, is_hidden_king: bool = False) -> None:
    pos = Position(file, rank)
    piece = Piece(type=piece_type, color=color, is_hidden_king=is_hidden_king)
    board.set_piece(pos, piece)


def test_with_full_board():
    """Test with the full initial board setup."""
    print("\n=== TEST WITH FULL BOARD ===")
    
    board = initialize_board()
    
    # Set a pawn as hidden king - let's use the e2 pawn
    e2_pos = Position("e", 2)
    e2_pawn = board.get_piece(e2_pos)
    if e2_pawn:
        e2_pawn.is_hidden_king = True
        print(f"Set e2 pawn as hidden king: {e2_pawn}")
    
    # Simulate a move: e2 pawn to e4
    board.set_piece(Position("e", 4), e2_pawn)
    board.set_piece(e2_pos, None)
    
    # Now simulate enemy pawn from d7 moving to d5
    d7_pos = Position("d", 7)
    d7_pawn = board.get_piece(d7_pos)
    board.set_piece(Position("d", 5), d7_pawn)
    board.set_piece(d7_pos, None)
    
    # Check situation
    king_pos = Position("e", 4)
    print(f"\nHidden king at e4: {board.get_piece(king_pos)}")
    print(f"Enemy pawn at d5: {board.get_piece(Position('d', 5))}")
    
    in_check = is_hidden_king_in_check(board, PieceColor.POLICE)
    print(f"\nIs hidden king in check? {in_check}")
    
    if in_check:
        can_escape = can_escape_check(board, PieceColor.POLICE)
        print(f"Can escape check? {can_escape}")
        
        # Show all police pieces and their moves
        print("\n--- Checking all Police pieces ---")
        for pos, piece in board.find_pieces(PieceColor.POLICE):
            moves = get_valid_moves(board, pos)
            if moves:
                print(f"  {piece.type.value} at {pos.file}{pos.rank}: {[(m.file, m.rank) for m in moves[:5]]}{'...' if len(moves) > 5 else ''}")
    
    is_checkmate = is_hidden_king_checkmated(board, PieceColor.POLICE)
    print(f"\nIs checkmate? {is_checkmate}")
    print("Expected: NOT checkmate (pawn at e4 can capture d5 or move to e5)")


def test_specific_scenario():
    """Test a specific scenario where the bug occurs."""
    print("\n=== TEST SPECIFIC SCENARIO ===")
    
    board = initialize_board()
    
    # Move e2 pawn (hidden king) to e4
    e2_pawn = board.get_piece(Position("e", 2))
    e2_pawn.is_hidden_king = True
    board.set_piece(Position("e", 4), e2_pawn)
    board.set_piece(Position("e", 2), None)
    
    # Move d7 pawn to e5 (attacks e4 diagonally from front)
    d7_pawn = board.get_piece(Position("d", 7))
    board.set_piece(Position("d", 5), d7_pawn)
    board.set_piece(Position("d", 7), None)
    
    print(f"Hidden king e2 pawn at e4, enemy d7 pawn at d5")
    
    # The mafia pawn at d5 attacks e4 from d5
    enemy_moves = get_valid_moves(board, Position("d", 5))
    print(f"Enemy pawn d5 can move to: {[(m.file, m.rank) for m in enemy_moves]}")
    
    # Does it attack e4?
    can_attack_e4 = Position("e", 4) in enemy_moves
    print(f"Can enemy pawn attack e4? {can_attack_e4}")
    
    # Hidden king moves
    king_moves = get_valid_moves(board, Position("e", 4))
    print(f"Hidden king e4 can move to: {[(m.file, m.rank) for m in king_moves]}")
    
    in_check = is_hidden_king_in_check(board, PieceColor.POLICE)
    is_checkmate = is_hidden_king_checkmated(board, PieceColor.POLICE)
    print(f"\nIn check: {in_check}, Is checkmate: {is_checkmate}")


if __name__ == "__main__":
    test_with_full_board()
    test_specific_scenario()
