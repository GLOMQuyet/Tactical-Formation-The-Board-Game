"""PieceSprite — visual companion to core.Piece.

The core engine never touches this. The renderer maintains a sprite per piece
(keyed by piece identity) and reads x/y/color to draw.
"""

ANIMATION_STEP = 0.1   # per-frame decay; matches the original `1e-1` constant


class PieceSprite:
    __slots__ = ('selected', 'progress', 'start_pixel', 'end_pixel')

    def __init__(self):
        self.selected = False
        self.progress = 0
        self.start_pixel = None
        self.end_pixel = None

    def start_animation(self, start_pixel, end_pixel):
        self.start_pixel = start_pixel
        self.end_pixel = end_pixel
        self.progress = 1.0

    def tick(self):
        """Advance one frame; return current draw pixel or None if idle."""
        if self.progress <= 0:
            return None
        sx, sy = self.start_pixel
        ex, ey = self.end_pixel
        t = 1 - self.progress
        px = sx + (ex - sx) * t
        py = sy + (ey - sy) * t
        self.progress -= ANIMATION_STEP
        if self.progress <= 0:
            self.progress = 0
            self.start_pixel = None
            self.end_pixel = None
        return (px, py)
