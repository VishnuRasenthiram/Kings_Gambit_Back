"""Comprehensive unit tests for all piece movements."""
import pytest
from app.features.game.models import Board, Piece, PieceType, PieceColor, Position
from app.features.game.services.move_calculator import get_valid_moves


def create_empty_board() -> Board:
    """Create an empty board."""
    return Board()


def place_piece(board: Board, file: str, rank: int, piece_type: PieceType, color: PieceColor, is_hidden_king: bool = False) -> None:
    """Place a piece on the board."""
    pos = Position(file, rank)
    piece = Piece(type=piece_type, color=color, is_hidden_king=is_hidden_king)
    board.set_piece(pos, piece)


def get_moves_as_strings(board: Board, file: str, rank: int) -> set[str]:
    """Get valid moves as a set of strings like 'e4'."""
    pos = Position(file, rank)
    moves = get_valid_moves(board, pos)
    return {f"{m.file}{m.rank}" for m in moves}


# ==================== PAWN TESTS ====================

class TestPawnMoves:
    """Tests for pawn movement."""
    
    def test_white_pawn_initial_move_one_square(self):
        """White pawn can move 1 square forward from starting position."""
        board = create_empty_board()
        place_piece(board, "e", 2, PieceType.PAWN, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "e", 2)
        assert "e3" in moves
    
    def test_white_pawn_initial_move_two_squares(self):
        """White pawn can move 2 squares forward from starting position."""
        board = create_empty_board()
        place_piece(board, "e", 2, PieceType.PAWN, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "e", 2)
        assert "e4" in moves
    
    def test_white_pawn_cannot_move_two_after_initial(self):
        """White pawn cannot move 2 squares from non-starting position."""
        board = create_empty_board()
        place_piece(board, "e", 3, PieceType.PAWN, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "e", 3)
        assert "e5" not in moves
        assert "e4" in moves
    
    def test_white_pawn_blocked_by_piece(self):
        """White pawn cannot move if blocked."""
        board = create_empty_board()
        place_piece(board, "e", 2, PieceType.PAWN, PieceColor.POLICE)
        place_piece(board, "e", 3, PieceType.PAWN, PieceColor.MAFIA)  # Blocker
        
        moves = get_moves_as_strings(board, "e", 2)
        assert "e3" not in moves
        assert "e4" not in moves  # Also blocked indirectly
    
    def test_white_pawn_blocked_two_square_move(self):
        """White pawn cannot jump over piece for 2-square move."""
        board = create_empty_board()
        place_piece(board, "e", 2, PieceType.PAWN, PieceColor.POLICE)
        place_piece(board, "e", 4, PieceType.PAWN, PieceColor.MAFIA)  # Blocker at destination
        
        moves = get_moves_as_strings(board, "e", 2)
        assert "e3" in moves  # Can still move 1
        assert "e4" not in moves  # Blocked
    
    def test_white_pawn_diagonal_capture(self):
        """White pawn can capture diagonally."""
        board = create_empty_board()
        place_piece(board, "e", 4, PieceType.PAWN, PieceColor.POLICE)
        place_piece(board, "d", 5, PieceType.PAWN, PieceColor.MAFIA)  # Capturable
        place_piece(board, "f", 5, PieceType.PAWN, PieceColor.MAFIA)  # Capturable
        
        moves = get_moves_as_strings(board, "e", 4)
        assert "d5" in moves
        assert "f5" in moves
    
    def test_white_pawn_cannot_capture_own_piece(self):
        """White pawn cannot capture own piece."""
        board = create_empty_board()
        place_piece(board, "e", 4, PieceType.PAWN, PieceColor.POLICE)
        place_piece(board, "d", 5, PieceType.PAWN, PieceColor.POLICE)  # Own piece
        
        moves = get_moves_as_strings(board, "e", 4)
        assert "d5" not in moves
    
    def test_black_pawn_moves_opposite_direction(self):
        """Black pawn moves down the board."""
        board = create_empty_board()
        place_piece(board, "e", 7, PieceType.PAWN, PieceColor.MAFIA)
        
        moves = get_moves_as_strings(board, "e", 7)
        assert "e6" in moves
        assert "e5" in moves  # 2-square initial move
        assert "e8" not in moves  # Wrong direction


# ==================== ROOK TESTS ====================

class TestRookMoves:
    """Tests for rook movement."""
    
    def test_rook_moves_horizontally(self):
        """Rook can move along entire rank."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.ROOK, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "d", 4)
        # All squares on rank 4
        for f in ["a", "b", "c", "e", "f", "g", "h"]:
            assert f"{f}4" in moves
    
    def test_rook_moves_vertically(self):
        """Rook can move along entire file."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.ROOK, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "d", 4)
        # All squares on file d
        for r in [1, 2, 3, 5, 6, 7, 8]:
            assert f"d{r}" in moves
    
    def test_rook_cannot_move_diagonally(self):
        """Rook cannot move diagonally."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.ROOK, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "d", 4)
        assert "e5" not in moves
        assert "c3" not in moves
    
    def test_rook_blocked_by_own_piece(self):
        """Rook is blocked by own pieces."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.ROOK, PieceColor.POLICE)
        place_piece(board, "d", 6, PieceType.PAWN, PieceColor.POLICE)  # Blocker
        
        moves = get_moves_as_strings(board, "d", 4)
        assert "d5" in moves  # Before blocker
        assert "d6" not in moves  # Own piece
        assert "d7" not in moves  # Behind blocker
    
    def test_rook_can_capture(self):
        """Rook can capture enemy piece."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.ROOK, PieceColor.POLICE)
        place_piece(board, "d", 6, PieceType.PAWN, PieceColor.MAFIA)  # Enemy
        
        moves = get_moves_as_strings(board, "d", 4)
        assert "d6" in moves  # Can capture
        assert "d7" not in moves  # Blocked after capture


# ==================== BISHOP TESTS ====================

class TestBishopMoves:
    """Tests for bishop movement."""
    
    def test_bishop_moves_diagonally(self):
        """Bishop can move on diagonals."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.BISHOP, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "d", 4)
        # Diagonal squares
        assert "a1" in moves
        assert "g7" in moves
        assert "a7" in moves
        assert "g1" in moves
    
    def test_bishop_cannot_move_straight(self):
        """Bishop cannot move horizontally or vertically."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.BISHOP, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "d", 4)
        assert "d5" not in moves
        assert "e4" not in moves
    
    def test_bishop_blocked_by_piece(self):
        """Bishop is blocked by pieces."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.BISHOP, PieceColor.POLICE)
        place_piece(board, "f", 6, PieceType.PAWN, PieceColor.POLICE)  # Blocker
        
        moves = get_moves_as_strings(board, "d", 4)
        assert "e5" in moves
        assert "f6" not in moves  # Own piece
        assert "g7" not in moves  # Blocked


# ==================== KNIGHT TESTS ====================

class TestKnightMoves:
    """Tests for knight movement."""
    
    def test_knight_L_shape_moves(self):
        """Knight moves in L-shape."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.KNIGHT, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "d", 4)
        expected = {"c2", "e2", "b3", "f3", "b5", "f5", "c6", "e6"}
        assert moves == expected
    
    def test_knight_can_jump_over_pieces(self):
        """Knight can jump over other pieces."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.KNIGHT, PieceColor.POLICE)
        # Surround with pieces
        for f in ["c", "d", "e"]:
            for r in [3, 4, 5]:
                if not (f == "d" and r == 4):
                    place_piece(board, f, r, PieceType.PAWN, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "d", 4)
        # Knight can still move despite being "surrounded"
        assert len(moves) > 0
    
    def test_knight_corner_limited_moves(self):
        """Knight in corner has fewer moves."""
        board = create_empty_board()
        place_piece(board, "a", 1, PieceType.KNIGHT, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "a", 1)
        assert moves == {"b3", "c2"}


# ==================== QUEEN TESTS ====================

class TestQueenMoves:
    """Tests for queen movement."""
    
    def test_queen_moves_like_rook_and_bishop(self):
        """Queen combines rook and bishop movement."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.QUEEN, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "d", 4)
        # Rook moves
        assert "d1" in moves
        assert "a4" in moves
        # Bishop moves
        assert "a1" in moves
        assert "g7" in moves
    
    def test_queen_blocked(self):
        """Queen is blocked by pieces."""
        board = create_empty_board()
        place_piece(board, "d", 4, PieceType.QUEEN, PieceColor.POLICE)
        place_piece(board, "d", 6, PieceType.PAWN, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "d", 4)
        assert "d7" not in moves


# ==================== KING TESTS ====================

class TestKingMoves:
    """Tests for king movement."""
    
    def test_king_moves_one_square(self):
        """King can move one square in any direction."""
        board = create_empty_board()
        place_piece(board, "e", 4, PieceType.KING, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "e", 4)
        expected = {"d3", "e3", "f3", "d4", "f4", "d5", "e5", "f5"}
        assert moves == expected
    
    def test_king_cannot_move_more_than_one(self):
        """King cannot move more than one square."""
        board = create_empty_board()
        place_piece(board, "e", 4, PieceType.KING, PieceColor.POLICE)
        
        moves = get_moves_as_strings(board, "e", 4)
        assert "e6" not in moves
        assert "g4" not in moves


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
