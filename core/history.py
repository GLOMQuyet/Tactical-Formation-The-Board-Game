"""Move records — what one completed move changed, for undo and for saves.

A record stores positions, not Piece objects, so it can be written to a save
file and read back. Records are undone last-in-first-out, so when a record is
undone the board is exactly as that move left it: the moved piece stands on
`to_pos` and every captured piece is still where it was captured.
"""

from dataclasses import dataclass, field


@dataclass
class MoveRecord:
    player: str
    from_pos: tuple
    to_pos: tuple
    captured: list = field(default_factory=list)   # [(pos, color_before), ...]


def apply_record(board, rec):
    """Replay `rec` on `board`: move the piece, then flip the captured pieces."""
    piece = board.piece_at(rec.from_pos)
    board.move_piece(piece, rec.to_pos)
    for pos, _before in rec.captured:
        board.piece_at(pos).color = piece.color


def undo_record(board, rec):
    """Reverse `rec`, which must be the most recent move still on `board`."""
    piece = board.piece_at(rec.to_pos)
    for pos, before in rec.captured:
        board.piece_at(pos).color = before
    board.move_piece(piece, rec.from_pos)
