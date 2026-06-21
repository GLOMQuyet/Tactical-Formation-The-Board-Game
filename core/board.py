"""Board — pieces list + O(1) position index + Zobrist hash.

The old `piece_at(pieces, pos)` did a linear scan, which the profiler showed
to be ~38% of the search runtime. Wrapping pieces in a Board with a
`{(x, y): piece}` index makes lookups O(1). Mutating helpers (`move_piece`)
keep the index in sync, so callers can't fall out of sync.

`_hash` is a Zobrist hash of the position, used by the AI as a transposition
table key. It is maintained incrementally inside the search hot path
(`rules.make_move` / `rules.unmake_move`); `move_piece` itself is deliberately
hash-agnostic, and `clone()` recomputes the hash from scratch, so any drift on
the live UI board (which never needs the hash) is harmless.
"""

import random as _random

from core.piece import Piece

# Stable, seeded keys so hashes are reproducible across runs (helps testing).
_ZOB_RNG = _random.Random(0xC0FFEE)
_ZOBRIST = {}


def _zob(pos, color):
    """64-bit Zobrist key for a (position, color) pair — lazily generated."""
    key = (pos, color)
    h = _ZOBRIST.get(key)
    if h is None:
        h = _ZOB_RNG.getrandbits(64)
        _ZOBRIST[key] = h
    return h


class Board:
    __slots__ = ('pieces', '_index', '_hash')

    def __init__(self, pieces):
        self.pieces = pieces
        self._index = {(p.x, p.y): p for p in pieces}
        self._hash = self._compute_hash()

    def _compute_hash(self):
        h = 0
        for p in self.pieces:
            h ^= _zob((p.x, p.y), p.color)
        return h

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
        """Move `piece` to `new_pos` and keep the index consistent.

        Hash-agnostic by design — see module docstring.
        """
        old_pos = (piece.x, piece.y)
        if self._index.get(old_pos) is piece:
            del self._index[old_pos]
        piece.x, piece.y = new_pos
        self._index[new_pos] = piece

    def clone(self):
        """Deep-clone for AI search branches — pieces copied, index + hash rebuilt."""
        new_pieces = [Piece(p.x, p.y, p.color) for p in self.pieces]
        new_board = Board.__new__(Board)
        new_board.pieces = new_pieces
        new_board._index = {(p.x, p.y): p for p in new_pieces}
        new_board._hash = new_board._compute_hash()
        return new_board

    def __iter__(self):
        return iter(self.pieces)

    def __len__(self):
        return len(self.pieces)
