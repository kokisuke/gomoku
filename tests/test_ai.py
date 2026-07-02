"""Tests for ai.py (Task 3)."""

import pytest
from ai import get_ai_move, evaluate_board

SIZE = 15
EMPTY = [""] * (SIZE * SIZE)


def make_board(moves: dict[int, str]) -> list[str]:
    board = EMPTY[:]
    for idx, player in moves.items():
        board[idx] = player
    return board


def rc(row: int, col: int) -> int:
    return row * SIZE + col


class TestGetAiMove:
    def test_returns_valid_index_on_empty_board(self):
        board = EMPTY[:]
        move = get_ai_move(board, ai_player="O", size=SIZE, depth=1)
        assert 0 <= move < SIZE * SIZE
        assert board[move] == ""  # board must not be mutated

    def test_takes_winning_move_horizontal(self):
        """AI should take the 5th cell to win immediately."""
        board = make_board({rc(7, 5): "O", rc(7, 6): "O",
                            rc(7, 7): "O", rc(7, 8): "O"})
        move = get_ai_move(board, ai_player="O", size=SIZE, depth=3)
        assert move in {rc(7, 4), rc(7, 9)}

    def test_takes_winning_move_vertical(self):
        """AI should take the 5th cell to win vertically."""
        board = make_board({rc(3, 7): "O", rc(4, 7): "O",
                            rc(5, 7): "O", rc(6, 7): "O"})
        move = get_ai_move(board, ai_player="O", size=SIZE, depth=3)
        assert move in {rc(2, 7), rc(7, 7)}

    def test_blocks_opponent_winning_move(self):
        """AI should block human's 5-in-a-row threat."""
        # Human (X) has 4 in a row; AI must block
        board = make_board({rc(7, 5): "X", rc(7, 6): "X",
                            rc(7, 7): "X", rc(7, 8): "X"})
        move = get_ai_move(board, ai_player="O", size=SIZE, depth=3)
        assert move in {rc(7, 4), rc(7, 9)}

    def test_blocks_opponent_winning_move_vertical(self):
        """AI should block vertical threat."""
        board = make_board({rc(3, 7): "X", rc(4, 7): "X",
                            rc(5, 7): "X", rc(6, 7): "X"})
        move = get_ai_move(board, ai_player="O", size=SIZE, depth=3)
        assert move in {rc(2, 7), rc(7, 7)}

    def test_does_not_mutate_board(self):
        """get_ai_move must leave the board unchanged."""
        board = make_board({rc(7, 7): "X", rc(7, 8): "O"})
        original = board[:]
        get_ai_move(board, ai_player="O", size=SIZE, depth=2)
        assert board == original

    def test_prefers_win_over_defense(self):
        """When AI can win in one move AND block opponent, it should win."""
        board = make_board({
            # AI's winning row
            rc(7, 5): "O", rc(7, 6): "O", rc(7, 7): "O", rc(7, 8): "O",
            # Human's 4-in-a-row (different direction)
            rc(3, 7): "X", rc(4, 7): "X", rc(5, 7): "X", rc(6, 7): "X",
        })
        move = get_ai_move(board, ai_player="O", size=SIZE, depth=3)
        # AI should win at (7,4) or (7,9) rather than blocking at (2,7) or (7,7)
        assert move in {rc(7, 4), rc(7, 9)}


class TestEvaluateBoard:
    def test_empty_board_scores_zero(self):
        assert evaluate_board(EMPTY[:], "O") == 0

    def test_ai_advantage_scores_positive(self):
        """AI having more stones in a row should yield a positive score."""
        board = make_board({rc(7, 7): "O", rc(7, 8): "O", rc(7, 9): "O"})
        assert evaluate_board(board, "O") > 0

    def test_opponent_advantage_scores_negative(self):
        """Opponent having more stones in a row should yield a negative score."""
        board = make_board({rc(7, 7): "X", rc(7, 8): "X", rc(7, 9): "X"})
        assert evaluate_board(board, "O") < 0
