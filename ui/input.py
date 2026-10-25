"""Pixel ↔ board coordinate conversions."""

import math


def board_top_left(mode, width=800, height=800):
    board_pixels = mode.square_size * mode.grid_cols
    return ((width - board_pixels) // 2, (height - board_pixels) // 2)


def board_pixels(mode):
    return mode.square_size * mode.grid_cols


def blit_pos(board_pos, mode, width=800, height=800):
    """Pixel position to blit a 40×40 piece sprite at `board_pos`."""
    tl = board_top_left(mode, width, height)
    x, y = board_pos
    return (tl[0] + x * mode.square_size - 20,
            tl[1] + y * mode.square_size - 20)


def pixel_pos(board_pos, mode, width=800, height=800):
    """Centre pixel position for a board square."""
    tl = board_top_left(mode, width, height)
    x, y = board_pos
    return (tl[0] + x * mode.square_size,
            tl[1] + y * mode.square_size)


def board_pos(mouse_pos, mode, width=800, height=800):
    """Mouse pixel → the nearest board point within half a square, or None.

    Board points are the vertices (whole numbers) and the centres (halves in
    both coordinates); a click anywhere near a piece or a dot finds it, as in
    the browser version. Rounding x and y separately would also give
    points like (1, 0.5), which are not on the board.
    """
    tl = board_top_left(mode, width, height)
    x = (mouse_pos[0] - tl[0]) / mode.square_size
    y = (mouse_pos[1] - tl[1]) / mode.square_size
    best, best_d = None, 0.5
    for px, py in ((round(x), round(y)), (math.floor(x) + 0.5, math.floor(y) + 0.5)):
        d = math.hypot(px - x, py - y)
        if (d < best_d and 0 <= px <= mode.board_width and 0 <= py <= mode.board_height
                and (px, py) not in mode.excluded_cells):
            best, best_d = (px, py), d
    return best
