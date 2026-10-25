"""Board + piece + overlay rendering. Reads core state; never mutates it."""

import math
import time

import pygame

from ui import assets, i18n, input as ui_input
from ui.animation import MOVE_TIME, PieceSprite


WHITE = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 215, 0)
VALID_MOVE_COLOR = (50, 205, 50)
LAST_FROM_COLOR = (255, 215, 0)     # where the last move started
LAST_TO_COLOR = (255, 140, 0)       # where it landed
FLIPPED_COLOR = (255, 255, 255)     # pieces it flipped
MOVABLE_GLOW = (255, 245, 180, 150)  # under pieces that can jump
TURN_STRIP = (0, 0, 0, 110)
HINT_STRIP = (0, 0, 0, 150)
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

    def start_move_anim(self, piece, from_pos, to_pos, mode, now=None):
        self.get(piece).start_animation(
            ui_input.pixel_pos(from_pos, mode),
            ui_input.pixel_pos(to_pos, mode),
            time.monotonic() if now is None else now,
        )

    def start_flips(self, flipped, delay=MOVE_TIME, now=None):
        """`flipped` is [(piece, colour before)]: they turn after `delay` (s),
        by default when the jump that sandwiched them lands."""
        at = (time.monotonic() if now is None else now) + delay
        for piece, old_color in flipped:
            self.get(piece).start_flip(old_color, at)

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


def _glow(radius, color):
    surf = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (radius, radius), radius)
    return surf


def draw_pieces(win, pieces, sprites: SpriteRegistry, mode, selected_piece=None,
                movable=(), now=None):
    """Draw the pieces, a jump in progress on top. `movable` pieces get a glow."""
    now = time.monotonic() if now is None else now
    glow = _glow(27, MOVABLE_GLOW) if movable else None
    movable = {id(p) for p in movable}
    flying = []
    for piece in pieces:
        sprite = sprites.get(piece)
        old_color, scale = sprite.flip(now)
        img = assets.piece_image(old_color or piece.color)
        jump = sprite.jump(now)
        if jump is not None:
            flying.append((img, *jump))
            continue
        cx, cy = ui_input.pixel_pos((piece.x, piece.y), mode)
        if id(piece) in movable:
            win.blit(glow, (cx - 27, cy - 27))
        if piece is selected_piece:
            pygame.draw.circle(win, HIGHLIGHT_COLOR, (int(cx), int(cy)), 30, 5)
        _blit_piece(win, img, (cx, cy), scale)
    for img, center, scale in flying:
        _blit_piece(win, img, center, scale)


def _blit_piece(win, img, center, scale=1):
    if scale != 1:
        side = round(img.get_width() * scale)
        img = pygame.transform.smoothscale(img, (side, side))
    win.blit(img, img.get_rect(center=(round(center[0]), round(center[1]))))


def draw_valid_moves(win, moves, mode):
    for m in moves:
        bx, by = ui_input.blit_pos(m, mode)
        pygame.draw.circle(win, VALID_MOVE_COLOR,
                           (int(bx + 20), int(by + 20)), 15, 0)


def _dashed_circle(win, color, center, radius, width, dashes=10):
    rect = pygame.Rect(0, 0, 2 * radius, 2 * radius)
    rect.center = center
    arc = 2 * math.pi / dashes
    for k in range(dashes):
        pygame.draw.arc(win, color, rect, k * arc, k * arc + arc * 0.55, width)


def draw_capture_options(win, moved_piece, capture_options, mode):
    """A gold line along each sandwiched row, and a dashed ring on what it flips.

    `capture_options` is {direction: [pieces to flip]} (rules.find_captures);
    a plain list of directions draws one step of each line.
    """
    src = ui_input.pixel_pos((moved_piece.x, moved_piece.y), mode)
    for d in capture_options:
        flips = capture_options[d] if isinstance(capture_options, dict) else ()
        dx, dy = d
        step = 1 if (dx == 0 or dy == 0) else 0.5
        reach = (len(flips) + 1) * step if flips else 1
        end = ui_input.pixel_pos((moved_piece.x + dx * reach, moved_piece.y + dy * reach), mode)
        pygame.draw.line(win, HIGHLIGHT_COLOR, src, end, 8)
        for dot in (src, end):
            pygame.draw.circle(win, HIGHLIGHT_COLOR, dot, 4)
        for p in flips:
            _dashed_circle(win, HIGHLIGHT_COLOR, ui_input.pixel_pos((p.x, p.y), mode), 30, 4)


def nearest_capture_direction(mouse_pos, moved_piece, capture_options, mode):
    """The (dx, dy) of the sandwiched row pointing nearest to the mouse.

    None for a click on the moved piece itself, where no row is meant.
    """
    sx, sy = ui_input.pixel_pos((moved_piece.x, moved_piece.y), mode)
    mx, my = mouse_pos[0] - sx, mouse_pos[1] - sy
    if math.hypot(mx, my) < 0.2 * mode.square_size:   # at least the piece's half-width
        return None
    angle = math.atan2(my, mx)
    best, best_diff = None, float('inf')
    for d in capture_options:
        diff = abs(math.atan2(d[1], d[0]) - angle)
        diff = min(diff, 2 * math.pi - diff)
        if diff < best_diff:
            best, best_diff = d, diff
    return best


def draw_turn_text(win, mode, current_player, bot_thinking=False, yours=False):
    """Top-left bar: the side to move, its piece, and whether a bot is thinking.

    `yours` says "Your turn" (a person playing against bots).
    """
    key = 'thinking' if bot_thinking else 'your_turn' if yours else 'turn'
    text = assets.big_font().render(i18n.t(key, color=i18n.color(current_player)), True, WHITE)
    strip = pygame.Surface((text.get_width() + 70, 52), pygame.SRCALPHA)
    pygame.draw.rect(strip, TURN_STRIP, strip.get_rect(), border_radius=10)
    win.blit(strip, (6, 6))
    win.blit(assets.piece_image(current_player), (14, 12))
    win.blit(text, (62, 13))


def draw_hint(win, text, strong=False):
    """One line of help just above the piece counts; `strong` is in gold."""
    if not text:
        return
    surf = assets.hint_font(bold=strong).render(text, True, HIGHLIGHT_COLOR if strong else WHITE)
    rect = surf.get_rect(center=(win.get_width() // 2, win.get_height() - 63))
    strip = pygame.Surface(rect.inflate(22, 6).size, pygame.SRCALPHA)
    pygame.draw.rect(strip, HINT_STRIP, strip.get_rect(), border_radius=8)
    win.blit(strip, rect.inflate(22, 6))
    win.blit(surf, rect)


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

