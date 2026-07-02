"""
Gomoku AI using Minimax with Alpha-Beta Pruning.

Public API
----------
get_ai_move(board, ai_player="O", size=15, depth=3) -> int
    Return the best move index for *ai_player* given the current *board*.
"""

from __future__ import annotations
import math
from game_logic import calculate_winner, is_valid_move, is_forbidden

# ── Scoring constants ─────────────────────────────────────────────────────────
_WIN_SCORE    = 10_000_000
_SCORE_TABLE  = {
    # (length, open_ends): score
    (5, 0): _WIN_SCORE,
    (5, 1): _WIN_SCORE,
    (5, 2): _WIN_SCORE,
    (4, 2): 50_000,   # 活四 (open four)
    (4, 1): 5_000,    # 眠四 (half-open four)
    (4, 0): 0,
    (3, 2): 2_000,    # 活三 (open three)
    (3, 1): 200,      # 眠三 (half-open three)
    (3, 0): 0,
    (2, 2): 100,      # 活二
    (2, 1): 10,
    (2, 0): 0,
    (1, 2): 5,
    (1, 1): 1,
    (1, 0): 0,
}
_DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _rc(idx: int, size: int) -> tuple[int, int]:
    return divmod(idx, size)


def _idx(row: int, col: int, size: int) -> int:
    return row * size + col


def _in_bounds(row: int, col: int, size: int) -> bool:
    return 0 <= row < size and 0 <= col < size


def _count_dir(board: list[str], r: int, c: int, dr: int, dc: int,
               player: str, size: int) -> int:
    count = 0
    r2, c2 = r + dr, c + dc
    while _in_bounds(r2, c2, size) and board[_idx(r2, c2, size)] == player:
        count += 1
        r2 += dr
        c2 += dc
    return count


def _score_line(board: list[str], r: int, c: int, dr: int, dc: int,
                player: str, size: int) -> int:
    """Score a single consecutive run of *player* that passes through (r,c)."""
    fwd  = _count_dir(board, r, c,  dr,  dc, player, size)
    bwd  = _count_dir(board, r, c, -dr, -dc, player, size)
    length = 1 + fwd + bwd

    if length >= 5:
        return _WIN_SCORE

    # Count open ends
    open_ends = 0
    nr_f, nc_f = r + dr * (fwd + 1), c + dc * (fwd + 1)
    if _in_bounds(nr_f, nc_f, size) and board[_idx(nr_f, nc_f, size)] == "":
        open_ends += 1
    nr_b, nc_b = r - dr * (bwd + 1), c - dc * (bwd + 1)
    if _in_bounds(nr_b, nc_b, size) and board[_idx(nr_b, nc_b, size)] == "":
        open_ends += 1

    return _SCORE_TABLE.get((length, open_ends), 0)


# ── Board evaluation ──────────────────────────────────────────────────────────

def _already_counted(
    board: list[str], r: int, c: int, dr: int, dc: int, player: str, size: int
) -> bool:
    """Return True if the run through (r,c) in direction (dr,dc) was already
    scored from an earlier cell (to avoid double counting)."""
    r2, c2 = r - dr, c - dc
    return _in_bounds(r2, c2, size) and board[_idx(r2, c2, size)] == player


def evaluate_board(board: list[str], ai_player: str, size: int = 15) -> int:
    """
    Return a heuristic score for *ai_player* on the current *board*.
    Positive = good for AI, negative = good for opponent.
    """
    opponent = "X" if ai_player == "O" else "O"
    score = 0

    for idx, stone in enumerate(board):
        if not stone:
            continue
        r, c = _rc(idx, size)
        multiplier = 1 if stone == ai_player else -1

        for dr, dc in _DIRECTIONS:
            if _already_counted(board, r, c, dr, dc, stone, size):
                continue
            line_score = _score_line(board, r, c, dr, dc, stone, size)
            score += multiplier * line_score

    return score


# ── Candidate move generation ─────────────────────────────────────────────────

def _get_candidates(board: list[str], size: int, radius: int = 2) -> list[int]:
    """
    Return empty cells within *radius* steps of any placed stone.
    Falls back to the center cell when the board is empty.
    """
    occupied = {i for i, v in enumerate(board) if v}
    if not occupied:
        center = size // 2
        return [_idx(center, center, size)]

    candidates: set[int] = set()
    for idx in occupied:
        r, c = _rc(idx, size)
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                nr, nc = r + dr, c + dc
                if _in_bounds(nr, nc, size):
                    ni = _idx(nr, nc, size)
                    if board[ni] == "":
                        candidates.add(ni)
    return list(candidates)


# ── Minimax with Alpha-Beta Pruning ───────────────────────────────────────────

def _minimax(
    board: list[str],
    depth: int,
    alpha: int,
    beta: int,
    is_maximizing: bool,
    ai_player: str,
    human_player: str,
    size: int,
) -> int:
    winner = calculate_winner(board, size)
    if winner == ai_player:
        return _WIN_SCORE + depth        # prefer faster wins
    if winner == human_player:
        return -(_WIN_SCORE + depth)     # prefer slower losses
    if depth == 0:
        return evaluate_board(board, ai_player, size)

    candidates = _get_candidates(board, size)
    if not candidates:
        return evaluate_board(board, ai_player, size)

    current_player = ai_player if is_maximizing else human_player

    if is_maximizing:
        best = -math.inf
        for idx in candidates:
            if not is_valid_move(board, idx):
                continue
            # AI (white, "O") has no forbidden moves
            board[idx] = current_player
            val = _minimax(board, depth - 1, alpha, beta, False,
                           ai_player, human_player, size)
            board[idx] = ""
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break   # β cut-off
        return best
    else:
        best = math.inf
        for idx in candidates:
            if not is_valid_move(board, idx):
                continue
            # Skip forbidden moves for the human (black, "X")
            if is_forbidden(board, idx, current_player, size):
                continue
            board[idx] = current_player
            val = _minimax(board, depth - 1, alpha, beta, True,
                           ai_player, human_player, size)
            board[idx] = ""
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break   # α cut-off
        return best


# ── Public API ────────────────────────────────────────────────────────────────

def get_ai_move(
    board: list[str],
    ai_player: str = "O",
    size: int = 15,
    depth: int = 3,
) -> int:
    """
    Return the best move index for *ai_player* using Minimax + Alpha-Beta Pruning.

    Parameters
    ----------
    board      : flat list of "" / "X" / "O"  (size*size elements)
    ai_player  : the AI's token, default "O" (white)
    size       : board side length, default 15
    depth      : search depth, default 3
    """
    human_player = "X" if ai_player == "O" else "O"
    candidates = _get_candidates(board, size)

    # ── Priority 1: Take an immediate win ────────────────────────────────────
    for idx in candidates:
        if not is_valid_move(board, idx):
            continue
        board[idx] = ai_player
        won = calculate_winner(board, size) == ai_player
        board[idx] = ""
        if won:
            return idx

    # ── Priority 2: Block opponent's immediate win ────────────────────────────
    for idx in candidates:
        if not is_valid_move(board, idx):
            continue
        board[idx] = human_player
        threat = calculate_winner(board, size) == human_player
        board[idx] = ""
        if threat:
            return idx

    # ── Priority 3: Full minimax search ──────────────────────────────────────
    best_score = -math.inf
    best_move  = -1

    for idx in candidates:
        if not is_valid_move(board, idx):
            continue
        board[idx] = ai_player
        score = _minimax(board, depth - 1, -math.inf, math.inf,
                         False, ai_player, human_player, size)
        board[idx] = ""
        if score > best_score:
            best_score = score
            best_move  = idx

    return best_move
