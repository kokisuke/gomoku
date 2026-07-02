"""Tests for game_logic.py (Tasks 1 & 2)."""

import pytest
from game_logic import (
    calculate_winner,
    get_winning_cells,
    is_valid_move,
    is_forbidden,
)

SIZE = 15
EMPTY = [""] * (SIZE * SIZE)


def make_board(moves: dict[int, str]) -> list[str]:
    """Create a board with specific stones placed. moves = {idx: player}."""
    board = EMPTY[:]
    for idx, player in moves.items():
        board[idx] = player
    return board


def rc(row: int, col: int) -> int:
    return row * SIZE + col


# ── Task 1: calculate_winner ──────────────────────────────────────────────────

class TestCalculateWinner:
    def test_no_winner_on_empty_board(self):
        assert calculate_winner(EMPTY[:]) is None

    def test_horizontal_win_X(self):
        board = make_board({rc(7, 5): "X", rc(7, 6): "X", rc(7, 7): "X",
                            rc(7, 8): "X", rc(7, 9): "X"})
        assert calculate_winner(board) == "X"

    def test_horizontal_win_O(self):
        board = make_board({rc(3, 2): "O", rc(3, 3): "O", rc(3, 4): "O",
                            rc(3, 5): "O", rc(3, 6): "O"})
        assert calculate_winner(board) == "O"

    def test_vertical_win_X(self):
        board = make_board({rc(2, 7): "X", rc(3, 7): "X", rc(4, 7): "X",
                            rc(5, 7): "X", rc(6, 7): "X"})
        assert calculate_winner(board) == "X"

    def test_diagonal_down_right_win_X(self):
        board = make_board({rc(0, 0): "X", rc(1, 1): "X", rc(2, 2): "X",
                            rc(3, 3): "X", rc(4, 4): "X"})
        assert calculate_winner(board) == "X"

    def test_diagonal_down_left_win_O(self):
        board = make_board({rc(0, 4): "O", rc(1, 3): "O", rc(2, 2): "O",
                            rc(3, 1): "O", rc(4, 0): "O"})
        assert calculate_winner(board) == "O"

    def test_four_in_a_row_no_winner(self):
        board = make_board({rc(7, 5): "X", rc(7, 6): "X",
                            rc(7, 7): "X", rc(7, 8): "X"})
        assert calculate_winner(board) is None

    def test_no_winner_ongoing_game(self):
        board = make_board({rc(7, 7): "X", rc(7, 8): "O",
                            rc(6, 7): "X", rc(8, 7): "O"})
        assert calculate_winner(board) is None

    def test_six_in_a_row_O_wins(self):
        # White (O) wins even with 6+ in a row (no overline rule for O)
        board = make_board({rc(5, c): "O" for c in range(6)})
        assert calculate_winner(board) == "O"


class TestGetWinningCells:
    def test_returns_empty_if_no_winner(self):
        assert get_winning_cells(EMPTY[:]) == []

    def test_returns_five_cells_for_horizontal(self):
        board = make_board({rc(7, 5): "X", rc(7, 6): "X", rc(7, 7): "X",
                            rc(7, 8): "X", rc(7, 9): "X"})
        cells = get_winning_cells(board)
        assert len(cells) >= 5
        expected = {rc(7, 5), rc(7, 6), rc(7, 7), rc(7, 8), rc(7, 9)}
        assert expected.issubset(set(cells))

    def test_returns_five_cells_for_vertical(self):
        board = make_board({rc(r, 7): "X" for r in range(5)})
        cells = get_winning_cells(board)
        assert len(cells) >= 5


class TestIsValidMove:
    def test_empty_cell_is_valid(self):
        assert is_valid_move(EMPTY[:], rc(7, 7)) is True

    def test_occupied_cell_is_invalid(self):
        board = make_board({rc(7, 7): "X"})
        assert is_valid_move(board, rc(7, 7)) is False

    def test_out_of_bounds_is_invalid(self):
        assert is_valid_move(EMPTY[:], 225) is False
        assert is_valid_move(EMPTY[:], -1) is False


# ── Task 2: is_forbidden ──────────────────────────────────────────────────────

class TestIsForbidden:
    def test_white_never_forbidden(self):
        """White (O) has no forbidden moves."""
        board = EMPTY[:]
        # Even if it would be a forbidden pattern for black, white is fine
        assert is_forbidden(board, rc(7, 7), player="O") is False

    def test_normal_move_not_forbidden(self):
        board = EMPTY[:]
        assert is_forbidden(board, rc(7, 7), player="X") is False

    # ── 長連 (overline: 6+) ──

    def test_overline_forbidden(self):
        """Placing to create 6 in a row is forbidden for black."""
        # X X X X X _ <- place at col 5 → 6 in a row
        board = make_board({rc(7, c): "X" for c in range(5)})
        assert is_forbidden(board, rc(7, 5), player="X") is True

    def test_exactly_five_not_overline(self):
        """Exactly 5 in a row is NOT forbidden (it's a win)."""
        board = make_board({rc(7, c): "X" for c in range(4)})
        assert is_forbidden(board, rc(7, 4), player="X") is False

    # ── 四四 (double four) ──

    def test_double_four_forbidden(self):
        """Creating two fours simultaneously is forbidden for black.

        Layout (place at 7,7):
          Horizontal: X at (7,4) (7,5) (7,6) _ (7,8) → place at (7,7) → 4 in row (7,4-7)
          But we need exactly 4 and one open end, not 5.
          Use: (7,4)(7,5)(7,6) + place(7,7) → length=4, blocked at col 3 by O, open at col 8
               (4,7)(5,7)(6,7) + place(7,7) → length=4, blocked at row 3 by O, open at row 8
        """
        board = make_board({
            # Horizontal: blocked on left by O, 3 stones to the left of target
            rc(7, 3): "O",                                       # blocker
            rc(7, 4): "X", rc(7, 5): "X", rc(7, 6): "X",       # 3 black stones
            # Vertical: blocked on top by O, 3 stones above target
            rc(3, 7): "O",                                       # blocker
            rc(4, 7): "X", rc(5, 7): "X", rc(6, 7): "X",       # 3 black stones
        })
        # Placing at (7,7) → horizontal length=4 (open at col 8), vertical length=4 (open at row 8)
        assert is_forbidden(board, rc(7, 7), player="X") is True

    def test_single_four_not_forbidden(self):
        """Only one four is not forbidden."""
        board = make_board({rc(7, 5): "X", rc(7, 6): "X",
                            rc(7, 8): "X", rc(7, 9): "X"})
        assert is_forbidden(board, rc(7, 7), player="X") is False

    # ── 三三 (double open three) ──

    def test_double_open_three_forbidden(self):
        """Creating two open threes simultaneously is forbidden for black."""
        # Horizontal open three: _XX_ at cols 6,7 (place at 5, open at 4 and 8)
        # Vertical open three: _XX_ at rows 6,7 (place at 5, open at 4 and 8)
        board = make_board({
            rc(7, 6): "X", rc(7, 7): "X",   # horizontal
            rc(6, 5): "X", rc(7, 5): "X",   # vertical  (共通の配置)
        })
        # Place at (5,5) to create two open threes
        board2 = make_board({
            rc(5, 6): "X", rc(5, 7): "X",   # horiz: place at (5,5) → _XX with open ends
            rc(6, 5): "X", rc(7, 5): "X",   # vert:  place at (5,5) → _XX with open ends
        })
        assert is_forbidden(board2, rc(5, 5), player="X") is True

    def test_single_open_three_not_forbidden(self):
        """Only one open three is not forbidden."""
        board = make_board({rc(7, 6): "X", rc(7, 7): "X"})
        assert is_forbidden(board, rc(7, 5), player="X") is False

    def test_forbidden_move_does_not_modify_board(self):
        """is_forbidden must not leave any side effects on the board."""
        board = EMPTY[:]
        original = board[:]
        is_forbidden(board, rc(7, 7), player="X")
        assert board == original
