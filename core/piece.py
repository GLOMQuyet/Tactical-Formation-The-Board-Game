"""Lightweight piece — data only, no pygame, no animation.

Used by the rules engine and AI search. The UI layer keeps a separate sprite
keyed by the same identity (object id) and reads x/y/color to render.
"""


class Piece:
    __slots__ = ('x', 'y', 'color')

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def clone(self):
        return Piece(self.x, self.y, self.color)

    def __repr__(self):
        return f"Piece({self.x}, {self.y}, {self.color!r})"


def piece_at(pieces, pos):
    for p in pieces:
        if p.x == pos[0] and p.y == pos[1]:
            return p
    return None
