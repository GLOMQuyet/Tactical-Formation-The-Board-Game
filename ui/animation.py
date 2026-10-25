"""PieceSprite — visual companion to core.Piece.

The core engine never touches this. The renderer maintains a sprite per piece
(keyed by piece identity) and reads x/y/color to draw. Timings follow the
browser version (web/src/game/controller.ts): a jump eases in and out and
lifts the piece; pieces it flips keep their old colour until it lands, then
pulse once in their new colour.
"""

import math

MOVE_TIME = 0.26   # s, a jump
FLIP_TIME = 0.30   # s, the pulse of a flipped piece


class PieceSprite:
    __slots__ = ('selected', 'start', 'start_pixel', 'end_pixel', 'flip_at', 'old_color')

    def __init__(self):
        self.selected = False
        self.start = None
        self.start_pixel = None
        self.end_pixel = None
        self.flip_at = None      # when the piece takes its new colour
        self.old_color = None    # the colour shown until then

    def start_animation(self, start_pixel, end_pixel, now):
        self.start_pixel = start_pixel
        self.end_pixel = end_pixel
        self.start = now

    def start_flip(self, old_color, at):
        self.old_color = old_color
        self.flip_at = at

    def jump(self, now):
        """(pixel, scale) while the piece is in the air, else None."""
        if self.start is None:
            return None
        t = (now - self.start) / MOVE_TIME
        if t >= 1:
            self.start = self.start_pixel = self.end_pixel = None
            return None
        e = 2 * t * t if t < 0.5 else 1 - (2 - 2 * t) ** 2 / 2
        sx, sy = self.start_pixel
        ex, ey = self.end_pixel
        return (sx + (ex - sx) * e, sy + (ey - sy) * e), 1 + 0.25 * math.sin(math.pi * t)

    def flip(self, now):
        """(colour to show instead of the piece's own, or None; scale)."""
        if self.flip_at is None:
            return None, 1
        if now < self.flip_at:
            return self.old_color, 1
        t = (now - self.flip_at) / FLIP_TIME
        if t >= 1:
            self.flip_at = self.old_color = None
            return None, 1
        return None, 1 + 0.3 * math.sin(math.pi * t)
