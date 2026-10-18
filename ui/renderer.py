"""Board + piece + overlay rendering. Reads core state; never mutates it."""

import pygame

from ui import assets, i18n, input as ui_input
from ui.animation import PieceSprite


WHITE = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 215, 0)
VALID_MOVE_COLOR = (50, 205, 50)
LAST_FROM_COLOR = (255, 215, 0)     # where the last move started
LAST_TO_COLOR = (255, 140, 0)       # where it landed
FLIPPED_COLOR = (255, 255, 255)     # pieces it flipped
TURN_STRIP = (0, 0, 0, 110)
SCORE_OUT = (150, 150, 150)         # count of a side that is out


class SpriteRegistry:
    """Holds one PieceSprite per piece, keyed by piece identity."""
    def __init__(self):
        self._sprites = {}

    def get(self, piece):
        sp = self._sprites.get(id(piece))
        if sp is None:
            sp = PieceSprite()
            self._sprites[id(piece)] = sp
        return sp

    def start_move_anim(self, piece, from_pos, to_pos, mode):
        self.get(piece).start_animation(
            ui_input.blit_pos(from_pos, mode),
            ui_input.blit_pos(to_pos, mode),
        )

    def clear(self):
        self._sprites.clear()


def draw_board(win, mode):
    """Draw board lattice — for each present cell, draw its 4 outer edges and
    4 diamond diagonals. Cells in `mode.missing_cells` are skipped entirely,
    which automatically removes the lattice segments that bordered them."""
    tl = ui_input.board_top_left(mode)
    win.blit(assets.background_image(), (0, 0))

    missing = set(mode.missing_cells)
    ss = mode.square_size
    for row in range(mode.grid_rows):
        for col in range(mode.grid_cols):
            if (col, row) in missing:
                continue
            x0 = tl[0] + col * ss
            y0 = tl[1] + row * ss
            top_left = (x0, y0)
            top_right = (x0 + ss, y0)
            bottom_left = (x0, y0 + ss)
            bottom_right = (x0 + ss, y0 + ss)
            center = (x0 + ss // 2, y0 + ss // 2)
            # diamond diagonals
            pygame.draw.line(win, WHITE, top_left, center, 5)
            pygame.draw.line(win, WHITE, top_right, center, 5)
            pygame.draw.line(win, WHITE, bottom_left, center, 5)
            pygame.draw.line(win, WHITE, bottom_right, center, 5)
            # outer edges of this cell — drawing per-cell automatically skips
            # segments adjacent to missing cells, giving the cut-corner look
            pygame.draw.line(win, WHITE, top_left, top_right, 5)
            pygame.draw.line(win, WHITE, top_right, bottom_right, 5)
            pygame.draw.line(win, WHITE, bottom_left, bottom_right, 5)
            pygame.draw.line(win, WHITE, top_left, bottom_left, 5)


def draw_last_move(win, rec, mode):
    """Mark the last move (a core.history.MoveRecord): start, landing, flips.

    Drawn before the pieces, so the rings show around them.
    """
    if rec is None:
        return
    pygame.draw.circle(win, LAST_FROM_COLOR, ui_input.pixel_pos(rec.from_pos, mode), 13, 3)
    for pos, _before in rec.captured:
        pygame.draw.circle(win, FLIPPED_COLOR, ui_input.pixel_pos(pos, mode), 31, 3)
    pygame.draw.circle(win, LAST_TO_COLOR, ui_input.pixel_pos(rec.to_pos, mode), 32, 4)


def draw_pieces(win, pieces, sprites: SpriteRegistry, mode, selected_piece=None):
    for piece in pieces:
        sprite = sprites.get(piece)
        img = assets.piece_image(piece.color)
        if sprite.progress > 0:
            pos = sprite.tick()
            if pos is not None:
                win.blit(img, pos)
                continue
        bx, by = ui_input.blit_pos((piece.x, piece.y), mode)
        if piece is selected_piece:
            pygame.draw.circle(win, HIGHLIGHT_COLOR,
                               (int(bx + 20), int(by + 20)), 30, 5)
        win.blit(img, (bx, by))


def draw_valid_moves(win, moves, mode):
    for m in moves:
        bx, by = ui_input.blit_pos(m, mode)
        pygame.draw.circle(win, VALID_MOVE_COLOR,
                           (int(bx + 20), int(by + 20)), 15, 0)


def draw_capture_options(win, moved_piece, capture_options, mode):
    src = ui_input.pixel_pos((moved_piece.x, moved_piece.y), mode)
    for dx, dy in capture_options:
        end = ui_input.pixel_pos((moved_piece.x + dx, moved_piece.y + dy), mode)
        pygame.draw.line(win, HIGHLIGHT_COLOR, src, end, 5)


def nearest_capture_direction(mouse_pos, moved_piece, capture_options, mode):
    """Return the (dx, dy) direction whose end pixel is closest to the mouse."""
    best = None
    best_d = float('inf')
    for d in capture_options:
        dx, dy = d
        ex, ey = ui_input.pixel_pos((moved_piece.x + dx, moved_piece.y + dy), mode)
        dist2 = (mouse_pos[0] - ex) ** 2 + (mouse_pos[1] - ey) ** 2
        if dist2 < best_d:
            best_d = dist2
            best = d
    return best


def draw_turn_text(win, mode, current_player, bot_thinking=False):
    """Top-left bar: the side to move, its piece, and whether a bot is thinking."""
    key = 'thinking' if bot_thinking else 'turn'
    text = assets.big_font().render(i18n.t(key, color=i18n.color(current_player)), True, WHITE)
    strip = pygame.Surface((text.get_width() + 70, 52), pygame.SRCALPHA)
    pygame.draw.rect(strip, TURN_STRIP, strip.get_rect(), border_radius=10)
    win.blit(strip, (6, 6))
    win.blit(assets.piece_image(current_player), (14, 12))
    win.blit(text, (62, 13))


def draw_scores(win, mode, pieces, active_players):
    """Bottom strip: how many pieces each side has, in turn order.

    Sides that are out of the game are dimmed and struck through; their
    pieces stay on the board and can still be flipped.
    """
    counts = {color: 0 for color in mode.players}
    for p in pieces:
        counts[p.color] += 1
    font = assets.small_font()
    cells = []
    for color in mode.players:
        out = color not in active_players
        icon = assets.image(f'assets/{color}_piece.png', size=(28, 28)).copy()
        if out:
            icon.set_alpha(90)
        text = font.render(str(counts[color]), True, SCORE_OUT if out else WHITE)
        cells.append((icon, text, out))
    widths = [28 + 6 + text.get_width() for _icon, text, _out in cells]
    gap = 28
    total = sum(widths) + gap * (len(cells) - 1)
    strip = pygame.Surface((total + 32, 40), pygame.SRCALPHA)
    pygame.draw.rect(strip, TURN_STRIP, strip.get_rect(), border_radius=10)
    left = (win.get_width() - strip.get_width()) // 2
    top = win.get_height() - 48
    win.blit(strip, (left, top))
    x = left + 16
    for (icon, text, out), width in zip(cells, widths):
        win.blit(icon, (x, top + 6))
        win.blit(text, (x + 34, top + 20 - text.get_height() // 2))
        if out:
            pygame.draw.line(win, SCORE_OUT, (x - 2, top + 20), (x + width + 2, top + 20), 2)
        x += width + gap

