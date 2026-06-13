"""Board — pieces list + O(1) position index.

The old `piece_at(pieces, pos)` did a linear scan, which the profiler showed
to be ~38% of the search runtime. Wrapping pieces in a Board with a
`{(x, y): piece}` index makes lookups O(1). Mutating helpers (`move_piece`)
keep the index in sync, so callers can't fall out of sync.
"""

from core.piece import Piece


class Board:
    __slots__ = ('pieces', '_index')

    def __init__(self, pieces):
        self.pieces = pieces
        self._index = {(p.x, p.y): p for p in pieces}

    @classmethod
    def from_mode(cls, mode):
        pieces = []
        for color, positions in mode.start_positions.items():
            for x, y in positions:
                pieces.append(Piece(x, y, color))
        return cls(pieces)

    def piece_at(self, pos):
        return self._index.get(pos)

    def move_piece(self, piece, new_pos):
        """Move `piece` to `new_pos` and keep the index consistent."""
        old_pos = (piece.x, piece.y)
        if self._index.get(old_pos) is piece:
            del self._index[old_pos]
        piece.x, piece.y = new_pos
        self._index[new_pos] = piece

    def clone(self):
        """Deep-clone for AI search branches — pieces are copied, index rebuilt."""
        new_pieces = [Piece(p.x, p.y, p.color) for p in self.pieces]
        new_board = Board.__new__(Board)
        new_board.pieces = new_pieces
        new_board._index = {(p.x, p.y): p for p in new_pieces}
        return new_board

    def __iter__(self):
        return iter(self.pieces)

    def __len__(self):
        return len(self.pieces)
