"""
Gomoku (五目並べ) – Flet declarative UI
=======================================
Board rendering: Canvas で碁盤線を描画し、交点クリックで石を置く
"""

from __future__ import annotations
import flet as ft
import flet.canvas as cv

from game_logic import (
    calculate_winner,
    get_winning_cells,
    is_valid_move,
    is_forbidden,
)
from ai import get_ai_move

SIZE      = 15
BOARD_EMPTY: list[str] = [""] * (SIZE * SIZE)

# ── 定数 ─────────────────────────────────────────────────────────────────────
CELL      = 36          # 交点間の間隔 (px)
MARGIN    = 24          # 盤の端マージン
STONE_R   = 14          # 石の半径
BOARD_PX  = MARGIN * 2 + CELL * (SIZE - 1)   # キャンバス全体サイズ

BOARD_BG    = "#DEB887"
GRID_COLOR  = "#6B4A10"
BLACK_STONE = "#111111"
WHITE_STONE = "#F0F0F0"
WHITE_RING  = "#888888"
WIN_COLOR   = "#FF3333"
STAR_COLOR  = "#6B4A10"


def _xy(row: int, col: int) -> tuple[float, float]:
    """交点 (row, col) のピクセル座標を返す。"""
    return MARGIN + col * CELL, MARGIN + row * CELL


def _nearest(px: float, py: float) -> tuple[int, int]:
    """クリック座標に最も近い交点 (row, col) を返す。"""
    col = round((px - MARGIN) / CELL)
    row = round((py - MARGIN) / CELL)
    col = max(0, min(SIZE - 1, col))
    row = max(0, min(SIZE - 1, row))
    return row, col


# ── Board component ────────────────────────────────────────────────────────────

@ft.component
def Board(
    squares: list[str],
    x_is_next: bool,
    on_play,
    winning_cells: list[int],
    game_over: bool,
):
    current_player = "X" if x_is_next else "O"
    winning_set    = set(winning_cells)

    def handle_tap(e: ft.TapEvent):
        if game_over:
            return
        if e.local_position is None:
            return
        row, col = _nearest(e.local_position.x, e.local_position.y)
        idx = row * SIZE + col
        if not is_valid_move(squares, idx):
            return
        if current_player == "X" and is_forbidden(squares, idx, "X", SIZE):
            return
        next_sq      = squares[:]
        next_sq[idx] = current_player
        on_play(next_sq)

    # ── shapes リストを構築 ────────────────────────────────────────────────

    shapes: list[cv.Shape] = []

    # 1. 背景
    shapes.append(cv.Rect(
        x=0, y=0,
        width=BOARD_PX, height=BOARD_PX,
        paint=ft.Paint(color=BOARD_BG, style=ft.PaintingStyle.FILL),
    ))

    # 2. 碁盤の格子線
    line_paint = ft.Paint(color=GRID_COLOR, stroke_width=1,
                          style=ft.PaintingStyle.STROKE)
    for i in range(SIZE):
        x0, y0 = _xy(0, i)
        x1, y1 = _xy(SIZE - 1, i)
        shapes.append(cv.Line(x1=x0, y1=y0, x2=x1, y2=y1, paint=line_paint))
        x0, y0 = _xy(i, 0)
        x1, y1 = _xy(i, SIZE - 1)
        shapes.append(cv.Line(x1=x0, y1=y0, x2=x1, y2=y1, paint=line_paint))

    # 3. 星（天元・星点）
    stars = [(3,3),(3,7),(3,11),(7,3),(7,7),(7,11),(11,3),(11,7),(11,11)]
    star_paint = ft.Paint(color=STAR_COLOR, style=ft.PaintingStyle.FILL)
    for sr, sc in stars:
        sx, sy = _xy(sr, sc)
        shapes.append(cv.Circle(x=sx, y=sy, radius=3, paint=star_paint))

    # 4. 石
    for idx, stone in enumerate(squares):
        if not stone:
            continue
        row, col = divmod(idx, SIZE)
        sx, sy   = _xy(row, col)
        is_win   = idx in winning_set

        if stone == "X":
            # 黒石
            if is_win:
                shapes.append(cv.Circle(
                    x=sx, y=sy, radius=STONE_R + 3,
                    paint=ft.Paint(color=WIN_COLOR, style=ft.PaintingStyle.FILL),
                ))
            shapes.append(cv.Circle(
                x=sx, y=sy, radius=STONE_R,
                paint=ft.Paint(color=BLACK_STONE, style=ft.PaintingStyle.FILL),
            ))
        else:
            # 白石
            if is_win:
                shapes.append(cv.Circle(
                    x=sx, y=sy, radius=STONE_R + 3,
                    paint=ft.Paint(color=WIN_COLOR, style=ft.PaintingStyle.FILL),
                ))
            shapes.append(cv.Circle(
                x=sx, y=sy, radius=STONE_R,
                paint=ft.Paint(color=WHITE_STONE, style=ft.PaintingStyle.FILL),
            ))
            shapes.append(cv.Circle(
                x=sx, y=sy, radius=STONE_R,
                paint=ft.Paint(color=WHITE_RING, stroke_width=1.5,
                               style=ft.PaintingStyle.STROKE),
            ))

    canvas = cv.Canvas(
        shapes=shapes,
        width=BOARD_PX,
        height=BOARD_PX,
    )

    return ft.GestureDetector(
        content=canvas,
        on_tap=handle_tap,
    )


# ── MoveHistory component ─────────────────────────────────────────────────────

@ft.component
def MoveHistory(history: list[list[str]], current_move: int, on_jump):
    items: list[ft.Control] = []
    for move, _ in enumerate(history):
        label      = f"手 #{move}" if move > 0 else "開始"
        is_current = move == current_move
        items.append(
            ft.TextButton(
                content=ft.Text(
                    label,
                    weight=ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL,
                    color=ft.Colors.BLUE_700 if is_current else None,
                    size=12,
                ),
                on_click=lambda e, m=move: on_jump(m),
            )
        )

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("手の履歴", weight=ft.FontWeight.BOLD, size=13),
                ft.Container(
                    content=ft.Column(
                        items,
                        scroll=ft.ScrollMode.AUTO,
                        spacing=0,
                    ),
                    height=480,
                    width=110,
                ),
            ],
            spacing=6,
        ),
        padding=ft.padding.Padding.only(left=12),
    )


# ── Game component (root) ─────────────────────────────────────────────────────

@ft.component
def Game():
    history,       set_history       = ft.use_state([BOARD_EMPTY[:]])
    current_move,  set_current_move  = ft.use_state(0)
    mode,          set_mode          = ft.use_state("pvp")   # "pvp" | "ai"
    ai_thinking,   set_ai_thinking   = ft.use_state(False)

    squares   = history[current_move]
    x_is_next = current_move % 2 == 0
    winner    = calculate_winner(squares, SIZE)
    win_cells = get_winning_cells(squares, SIZE) if winner else []
    is_draw   = not winner and all(s != "" for s in squares)
    game_over = bool(winner) or is_draw

    def handle_play(next_squares: list[str]):
        next_history = history[: current_move + 1] + [next_squares]
        set_history(next_history)
        set_current_move(len(next_history) - 1)

    def jump_to(move: int):
        set_current_move(move)

    def handle_mode_change(e):
        set_mode(e.control.value)
        set_history([BOARD_EMPTY[:]])
        set_current_move(0)
        set_ai_thinking(False)

    def handle_reset(_e):
        set_history([BOARD_EMPTY[:]])
        set_current_move(0)
        set_ai_thinking(False)

    # ── AI トリガー ────────────────────────────────────────────────────────
    # use_effect の setup を async にすることで Flet のイベントループ内で実行される。
    # AI の計算は asyncio.to_thread でスレッドにオフロードし、
    # 結果が返ってきたら set_state を安全に呼び出す。
    async def trigger_ai():
        import asyncio
        if mode == "ai" and not x_is_next and not game_over and not ai_thinking:
            set_ai_thinking(True)
            board_copy = squares[:]
            move_idx = await asyncio.to_thread(
                get_ai_move, board_copy, "O", SIZE, 2
            )
            if move_idx >= 0 and is_valid_move(squares, move_idx):
                next_sq           = squares[:]
                next_sq[move_idx] = "O"
                handle_play(next_sq)
            set_ai_thinking(False)

    ft.use_effect(trigger_ai, [mode, current_move, x_is_next, game_over])

    # ── ステータステキスト ─────────────────────────────────────────────────
    if winner:
        who = "黒（あなた）" if winner == "X" else ("白（AI）" if mode == "ai" else "白")
        status = f"🎉 {who} の勝利！"
    elif is_draw:
        status = "引き分け"
    elif ai_thinking:
        status = "⏳ AI が考え中…"
    else:
        status = ("次の手番：黒 ●" if x_is_next
                  else "次の手番：白 ○" + ("（AI）" if mode == "ai" else ""))

    return ft.SafeArea(
        content=ft.Column(
            [
                ft.Text("五目並べ", size=22, weight=ft.FontWeight.BOLD),
                ft.RadioGroup(
                    content=ft.Row([
                        ft.Radio(value="pvp", label="2人対戦"),
                        ft.Radio(value="ai",  label="AI対戦"),
                    ]),
                    value=mode,
                    on_change=handle_mode_change,
                ),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(status, size=15),
                                ft.Container(height=6),
                                Board(
                                    squares=squares,
                                    x_is_next=x_is_next,
                                    on_play=handle_play,
                                    winning_cells=win_cells,
                                    game_over=game_over or ai_thinking,
                                ),
                                ft.Container(height=8),
                                ft.Button(
                                    "リセット",
                                    on_click=handle_reset,
                                    icon=ft.Icons.REFRESH,
                                ),
                            ],
                            spacing=0,
                        ),
                        MoveHistory(
                            history=history,
                            current_move=current_move,
                            on_jump=jump_to,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=16,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        )
    )


if __name__ == "__main__":
    ft.run(lambda page: page.render(Game))
