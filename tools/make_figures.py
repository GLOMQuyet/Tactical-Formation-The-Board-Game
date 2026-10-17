"""Render real in-game board screenshots (headless) for the paper figures.

Runs Pygame with the dummy video driver so it works over SSH/WSL with no
display, draws each mode's board + pieces using the *actual* game renderer
(ui/renderer.py), crops to the board, and writes PNGs to paper/figures/.

Usage:  python tools/make_figures.py
"""

import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame  # noqa: E402

from core.state import GameState  # noqa: E402
from core.board import Board  # noqa: E402
from core.piece import Piece  # noqa: E402
from core.modes import MODE_BOT_2, MODE_PLAY_3, MODE_PLAY_4  # noqa: E402
from ui import assets, input as ui_input, renderer  # noqa: E402

OUT = os.path.join(REPO, 'paper', 'figures')
W = H = 800


def _bbox(mode):
    tl = ui_input.board_top_left(mode, W, H)
    bp = ui_input.board_pixels(mode)
    pad = 34  # pieces overhang the lattice by ~20px; centres add half a cell
    x0 = max(0, tl[0] - pad)
    y0 = max(0, tl[1] - pad)
    x1 = min(W, tl[0] + bp + pad)
    y1 = min(H, tl[1] + bp + pad)
    return pygame.Rect(x0, y0, x1 - x0, y1 - y0)


def render_board(mode, name, pieces=True):
    state = GameState.new(mode)
    surf = pygame.Surface((W, H))
    renderer.draw_board(surf, mode)
    n = 0
    if pieces:
        renderer.draw_pieces(surf, state.pieces, renderer.SpriteRegistry(), mode)
        n = len(state.pieces)
    cropped = surf.subsurface(_bbox(mode)).copy()
    path = os.path.join(OUT, name)
    pygame.image.save(cropped, path)
    print(f"wrote {path}  ({cropped.get_width()}x{cropped.get_height()}, "
          f"{n} pieces)")


def render_scene(name, pieces, selected=None, dots=(), rays=(), pad_cells=0.9):
    """Render a custom board position (2-player board) with the game's own
    overlays: gold ring on the selected piece, green dots for valid landings,
    gold lines for capture directions. `pieces` = [(x,y,color)], `rays` =
    [((x,y),[(dx,dy),...])]. Cropped tightly around the relevant cells."""
    mode = MODE_BOT_2
    ss = mode.square_size
    objs = [Piece(x, y, c) for (x, y, c) in pieces]
    board = Board(objs)
    surf = pygame.Surface((W, H))
    renderer.draw_board(surf, mode)
    sel = board.piece_at(tuple(selected)) if selected is not None else None
    renderer.draw_pieces(surf, objs, renderer.SpriteRegistry(), mode,
                         selected_piece=sel)
    if dots:
        renderer.draw_valid_moves(surf, [tuple(d) for d in dots], mode)
    focus = [(x, y) for (x, y, _) in pieces] + [tuple(d) for d in dots]
    for base, dirs in rays:
        moved = board.piece_at(tuple(base)) or Piece(base[0], base[1], 'green')
        renderer.draw_capture_options(surf, moved, list(dirs), mode)
        focus.append(tuple(base))
        focus += [(base[0] + dx, base[1] + dy) for dx, dy in dirs]
    pad = int(ss * pad_cells)
    xs = [ui_input.pixel_pos(p, mode)[0] for p in focus]
    ys = [ui_input.pixel_pos(p, mode)[1] for p in focus]
    x0, y0 = max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad)
    x1, y1 = min(W, int(max(xs)) + pad), min(H, int(max(ys)) + pad)
    rect = pygame.Rect(x0, y0, x1 - x0, y1 - y0)
    pygame.image.save(surf.subsurface(rect).copy(), os.path.join(OUT, name))
    print(f"wrote {name}  {rect.size}")


def generate_mechanic_figures():
    G, Y = 'green', 'yellow'
    # ── movement directions (valid-move dots from the game) ──
    render_scene('dir_vertex.png',
                 [(2, 2, G), (1, 2, Y), (3, 2, Y), (2, 1, Y), (2, 3, Y),
                  (1.5, 1.5, Y), (2.5, 2.5, Y), (1.5, 2.5, Y), (2.5, 1.5, Y)],
                 selected=(2, 2),
                 dots=[(0, 2), (4, 2), (2, 0), (2, 4),
                       (1, 1), (3, 3), (1, 3), (3, 1)])
    render_scene('dir_center.png',
                 [(2.5, 2.5, G), (2, 2, Y), (3, 3, Y), (2, 3, Y), (3, 2, Y)],
                 selected=(2.5, 2.5),
                 dots=[(1.5, 1.5), (3.5, 3.5), (1.5, 3.5), (3.5, 1.5)])
    # ── three jump types: before (with landing dot) → after ──
    render_scene('jump1_before.png', [(1, 2, G), (2, 2, Y)],
                 selected=(1, 2), dots=[(3, 2)])
    render_scene('jump1_after.png', [(2, 2, Y), (3, 2, G)])
    render_scene('jump2_before.png', [(1, 1, G), (1.5, 1.5, Y)],
                 selected=(1, 1), dots=[(2, 2)])
    render_scene('jump2_after.png', [(1.5, 1.5, Y), (2, 2, G)])
    render_scene('jump3_before.png', [(1.5, 1.5, G), (2, 2, Y)],
                 selected=(1.5, 1.5), dots=[(2.5, 2.5)])
    render_scene('jump3_after.png', [(2, 2, Y), (2.5, 2.5, G)])
    # ── sandwich capture: landed with two capture rays → after flip ──
    cap = [(1, 2, G), (2, 2, Y), (3, 2, G), (1.5, 2.5, Y), (2, 3, Y),
           (2.5, 3.5, Y), (3, 4, G)]
    render_scene('capture_before.png', cap, selected=(1, 2),
                 rays=[((1, 2), [(1, 0), (0.5, 0.5)])])
    render_scene('capture_after.png',
                 [(1, 2, G), (2, 2, Y), (3, 2, G), (1.5, 2.5, G), (2, 3, G),
                  (2.5, 3.5, G), (3, 4, G)])
    # ── one full move: A jump → B capture ray → C after flip ──
    render_scene('move_a.png', [(0, 2, G), (1, 2, Y), (3, 2, Y), (4, 2, G)],
                 selected=(0, 2), dots=[(2, 2)])
    render_scene('move_b.png', [(1, 2, Y), (2, 2, G), (3, 2, Y), (4, 2, G)],
                 rays=[((2, 2), [(1, 0)])])
    render_scene('move_c.png', [(1, 2, Y), (2, 2, G), (3, 2, G), (4, 2, G)])
    # ── two ways to lose ──
    e1 = ([(x, y, G) for x in range(5) for y in (4, 3, 2)]
          + [(x + 0.5, y + 0.5, G) for x in range(4) for y in (3, 2, 1)]
          + [(0, 1, G)])
    render_scene('end_nopieces.png', e1, pad_cells=0.6)
    e2 = ([(x, y, G) for x in range(5) for y in (4, 3, 2)]
          + [(x + 0.5, y + 0.5, G) for x in range(4) for y in (3, 2)]
          + [(0, 1, Y), (2, 1, Y), (4, 1, Y), (1, 0, Y), (3, 0, Y)])
    render_scene('end_blocked.png', e2, pad_cells=0.6)


def main():
    # assets.resource_path resolves relative to __main__; force repo-root base.
    assets.resource_path = lambda rel: os.path.join(REPO, rel)
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))  # needed for convert_alpha()
    os.makedirs(OUT, exist_ok=True)
    render_board(MODE_BOT_2, 'board_2p_empty.png', pieces=False)
    render_board(MODE_BOT_2, 'board_2p.png')
    render_board(MODE_PLAY_3, 'board_3p.png')
    render_board(MODE_PLAY_4, 'board_4p.png')
    generate_mechanic_figures()
    pygame.quit()


if __name__ == '__main__':
    main()
