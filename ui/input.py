"""Pixel ↔ board coordinate conversions."""


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
    """Mouse pixel → nearest (x, y) board cell, or None if outside."""
    mx, my = mouse_pos
    tl = board_top_left(mode, width, height)
    bp = board_pixels(mode)
    if not (tl[0] - 20 <= mx <= tl[0] + bp + 20 and
            tl[1] - 20 <= my <= tl[1] + bp + 20):
        return None
    x = (mx - tl[0]) / mode.square_size
    y = (my - tl[1]) / mode.square_size
    return (round(x * 2) / 2, round(y * 2) / 2)
