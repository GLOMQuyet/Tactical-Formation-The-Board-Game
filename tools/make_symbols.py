"""Make the pieces with symbols, for players who cannot tell the colours apart.

Each colour gets its own shape, white with a dark outline, in the middle of
its piece: green a triangle, yellow a circle, purple a diamond, blue a
square. Writes assets/<colour>_piece_symbol.png and the same files in
web/src/assets/. The game shows them when "Symbols on pieces" is on.
Run with: uv run tools/make_symbols.py
"""

import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE = 120        # px of the output; the game shows pieces at 40 px
SCALE = 4         # drawn this many times larger, then smoothed down
OUTLINE = (25, 25, 25)
FILL = (255, 255, 255)


def _shape(color, c, r):
    """Points of the colour's shape around centre c with radius r (None: a circle)."""
    if color == 'green':
        return [(c, c - r), (c + r * 0.95, c + r * 0.72), (c - r * 0.95, c + r * 0.72)]
    if color == 'purple':
        return [(c, c - r), (c + r, c), (c, c + r), (c - r, c)]
    if color == 'blue':
        s = r * 0.78
        return [(c - s, c - s), (c + s, c - s), (c + s, c + s), (c - s, c + s)]
    return None


def make(color):
    big = SIZE * SCALE
    piece = pygame.image.load(os.path.join(REPO, 'assets', f'{color}_piece.png'))
    canvas = pygame.transform.smoothscale(piece, (big, big)).convert_alpha()
    c, r, line = big / 2, big * 0.24, big * 0.05
    points = _shape(color, c, r)
    if points is None:
        pygame.draw.circle(canvas, OUTLINE, (c, c), r * 0.82 + line)
        pygame.draw.circle(canvas, FILL, (c, c), r * 0.82)
    else:
        # The outline is the same shape drawn larger, behind the white one.
        grow = (r + line * 1.9) / r
        pygame.draw.polygon(canvas, OUTLINE, [(c + (x - c) * grow, c + (y - c) * grow) for x, y in points])
        pygame.draw.polygon(canvas, FILL, points)
    out = pygame.transform.smoothscale(canvas, (SIZE, SIZE))
    for folder in (os.path.join(REPO, 'assets'), os.path.join(REPO, 'web', 'src', 'assets')):
        pygame.image.save(out, os.path.join(folder, f'{color}_piece_symbol.png'))


def main():
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    for color in ('green', 'yellow', 'purple', 'blue'):
        make(color)
    print('wrote assets/*_piece_symbol.png and web/src/assets/*_piece_symbol.png')


if __name__ == '__main__':
    main()
