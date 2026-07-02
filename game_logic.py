"""
Gomoku (五目並べ) game logic.
Board is represented as a flat list of strings:
  "X" = black stone, "O" = white stone, "" = empty
Board size defaults to 15x15 = 225 cells.
"""

from __future__ import annotations

# ── directions: (row_delta, col_delta) ────────────────────────────────────────
_DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]  # →  ↓  ↘  ↙


# ── helpers ───────────────────────────────────────────────────────────────────

def _rc(idx: int, size: int) -> tuple[int, int]:
    """Convert flat index → (row, col)."""
    return divmod(idx, size)


def _idx(row: int, col: int, size: int) -> int:
    """Convert (row, col) → flat index."""
    return row * size + col


def _in_bounds(row: int, col: int, size: int) -> bool:
    return 0 <= row < size and 0 <= col < size


def _count_direction(
    board: list[str], row: int, col: int,
    dr: int, dc: int, player: str, size: int
) -> int:
    """Count consecutive player stones in one direction (not counting the origin)."""
    count = 0
    r, c = row + dr, col + dc
    while _in_bounds(r, c, size) and board[_idx(r, c, size)] == player:
        count += 1
        r += dr
        c += dc
    return count


def _line_length(
    board: list[str], row: int, col: int,
    dr: int, dc: int, player: str, size: int
) -> int:
    """Total consecutive length through (row,col) in both ±directions."""
    return (
        1
        + _count_direction(board, row, col, dr, dc, player, size)
        + _count_direction(board, row, col, -dr, -dc, player, size)
    )


# ── public API ────────────────────────────────────────────────────────────────

def is_valid_move(board: list[str], idx: int) -> bool:
    """Return True if the cell at *idx* is empty."""
    return 0 <= idx < len(board) and board[idx] == ""


def calculate_winner(board: list[str], size: int = 15) -> str | None:
    """
    Return "X" or "O" if that player has exactly 5 (or more for "O") in a row,
    otherwise None.

    Note: For black ("X"), exactly 5 wins; 6+ is a long connection (handled by
    forbidden-move rules when *placing*, but we still award the win if it somehow
    appears on the board so the game can end).
    """
    for idx, player in enumerate(board):
        if not player:
            continue
        row, col = _rc(idx, size)
        for dr, dc in _DIRECTIONS:
            length = _line_length(board, row, col, dr, dc, player, size)
            if length >= 5:
                return player
    return None


def get_winning_cells(board: list[str], size: int = 15) -> list[int]:
    """
    Return the flat indices of the winning five-in-a-row cells.
    Returns an empty list if there is no winner yet.
    """
    for idx, player in enumerate(board):
        if not player:
            continue
        row, col = _rc(idx, size)
        for dr, dc in _DIRECTIONS:
            # Collect all cells in this line through (row, col)
            cells: list[int] = [idx]
            r, c = row + dr, col + dc
            while _in_bounds(r, c, size) and board[_idx(r, c, size)] == player:
                cells.append(_idx(r, c, size))
                r += dr
                c += dc
            r, c = row - dr, col - dc
            while _in_bounds(r, c, size) and board[_idx(r, c, size)] == player:
                cells.append(_idx(r, c, size))
                r -= dr
                c -= dc
            if len(cells) >= 5:
                return cells
    return []


# ── forbidden-move (禁じ手) for black ("X") ────────────────────────────────────

def _count_open_ends(
    board: list[str], row: int, col: int,
    dr: int, dc: int, player: str, size: int
) -> int:
    """Return the number of open (empty) ends of a consecutive run."""
    open_ends = 0
    # positive direction: go past the run and check if the next cell is empty
    r = row + dr * (_count_direction(board, row, col, dr, dc, player, size) + 1) - dr
    c = col + dc * (_count_direction(board, row, col, dr, dc, player, size) + 1) - dc
    # simpler: just step past the run
    steps = _count_direction(board, row, col, dr, dc, player, size)
    nr, nc = row + dr * (steps + 1), col + dc * (steps + 1)
    if _in_bounds(nr, nc, size) and board[_idx(nr, nc, size)] == "":
        open_ends += 1
    steps2 = _count_direction(board, row, col, -dr, -dc, player, size)
    nr2, nc2 = row - dr * (steps2 + 1), col - dc * (steps2 + 1)
    if _in_bounds(nr2, nc2, size) and board[_idx(nr2, nc2, size)] == "":
        open_ends += 1
    return open_ends


def _is_overline(board: list[str], row: int, col: int, player: str, size: int) -> bool:
    """Return True if placing at (row,col) creates 6+ in a row (長連)."""
    for dr, dc in _DIRECTIONS:
        if _line_length(board, row, col, dr, dc, player, size) >= 6:
            return True
    return False


def _count_fours(board: list[str], row: int, col: int, player: str, size: int) -> int:
    """
    Count the number of distinct 'four' patterns (連四 or 四) created by
    placing player's stone at (row, col).
    A four = exactly 4 in a row with at least one open end (活四 or 眠四).
    """
    count = 0
    for dr, dc in _DIRECTIONS:
        length = _line_length(board, row, col, dr, dc, player, size)
        if length == 4:
            open_ends = _count_open_ends(board, row, col, dr, dc, player, size)
            if open_ends >= 1:
                count += 1
    return count


def _count_open_threes(
    board: list[str], row: int, col: int, player: str, size: int
) -> int:
    """
    Count the number of 'open three' (活三) patterns created by placing at (row,col).
    An open three = exactly 3 in a row with BOTH ends open.
    """
    count = 0
    for dr, dc in _DIRECTIONS:
        length = _line_length(board, row, col, dr, dc, player, size)
        if length == 3:
            open_ends = _count_open_ends(board, row, col, dr, dc, player, size)
            if open_ends == 2:
                count += 1
    return count


def is_forbidden(
    board: list[str], idx: int, player: str = "X", size: int = 15
) -> bool:
    """
    Return True if placing *player*'s stone at *idx* is a forbidden move.
    Forbidden moves only apply to black ("X"):
      - 長連  : 6 or more in a row
      - 四四  : two or more fours simultaneously
      - 三三  : two or more open threes simultaneously
    White ("O") never has forbidden moves.
    """
    if player != "X":
        return False
    if not is_valid_move(board, idx):
        return False

    # Temporarily place the stone
    board[idx] = player
    row, col = _rc(idx, size)

    forbidden = False

    # 1. 長連 (overline): 6+ in a row
    if _is_overline(board, row, col, player, size):
        forbidden = True

    # 2. 四四 (double four): two or more fours
    elif _count_fours(board, row, col, player, size) >= 2:
        forbidden = True

    # 3. 三三 (double open three): two or more open threes
    elif _count_open_threes(board, row, col, player, size) >= 2:
        forbidden = True

    # Remove the temporary stone
    board[idx] = ""
    return forbidden
