"""Single source of truth for game rules.

All move/capture/win logic lives here. Parameterised by a Mode so the
2/3/4-player variants share one code path. Takes a Board (with O(1)
position index) instead of a raw piece list, which keeps the hot
`piece_at` lookup constant-time during search.
"""

from core.geometry import (
    is_vertex, is_center,
    move_directions, capture_directions,
)


def _in_bounds(pos, mode):
    x, y = pos
    return 0 <= x <= mode.board_width and 0 <= y <= mode.board_height


def _same_kind(a, b):
    if is_vertex(a) and is_vertex(b):
        return True
    if is_center(a) and is_center(b):
        return True
    return False


def legal_moves(piece, board, mode):
    """All landing squares the piece can jump to under `mode`."""
    src = (piece.x, piece.y)
    excluded = mode.excluded_cells
    moves = []
    for dx, dy, _step in move_directions(src):
        adj = (piece.x + dx, piece.y + dy)
        land = (piece.x + 2 * dx, piece.y + 2 * dy)
        if not (_in_bounds(adj, mode) and _in_bounds(land, mode)):
            continue
        if land in excluded:
            continue
        if not _same_kind(src, land):
            continue
        if board.piece_at(adj) is None:
            continue
        if board.piece_at(land) is not None:
            continue
        moves.append(land)
    return moves


def find_captures(moved_piece, board, mode):
    """Return {direction: [enemy_pieces_to_flip]} for each sandwich ray."""
    src = (moved_piece.x, moved_piece.y)
    options = {}
    for dx, dy in capture_directions(src):
        x, y = moved_piece.x, moved_piece.y
        to_flip = []
        step = 1 if (dx == 0 or dy == 0) else 0.5
        while True:
            x += dx * step
            y += dy * step
            if not _in_bounds((x, y), mode):
                break
            other = board.piece_at((x, y))
            if other is None:
                break
            if other.color != moved_piece.color:
                to_flip.append(other)
            else:
                if to_flip:
                    options[(dx, dy)] = list(to_flip)
                break
    return options


def all_moves(color, board, mode):
    """All (fx, fy, tx, ty) moves available to `color`."""
    out = []
    for p in board.pieces:
        if p.color != color:
            continue
        for tx, ty in legal_moves(p, board, mode):
            out.append((p.x, p.y, tx, ty))
    return out


def has_available_moves(color, board, mode):
    for p in board.pieces:
        if p.color == color and legal_moves(p, board, mode):
            return True
    return False


def apply_move(board, move, mode, capture_direction=None):
    """Mutate `board`: move the piece, then flip captured enemies.

    Returns (moved_piece, list_of_flipped_pieces). If `capture_direction` is
    None and multiple capture rays exist, the greediest ray (most flips) is
    auto-chosen — used by AI search and by single-option human moves.
    """
    fx, fy, tx, ty = move
    p = board.piece_at((fx, fy))
    if p is None:
        return None, []
    board.move_piece(p, (tx, ty))
    captures = find_captures(p, board, mode)
    if not captures:
        return p, []
    if capture_direction is not None and capture_direction in captures:
        chosen = capture_direction
    else:
        chosen = max(captures.keys(), key=lambda d: len(captures[d]))
    flipped = captures[chosen]
    for enemy in flipped:
        enemy.color = p.color
    return p, flipped


def is_alive(color, board, mode):
    """A player is alive if they have at least one piece AND a legal move."""
    return (
        any(p.color == color for p in board.pieces)
        and has_available_moves(color, board, mode)
    )
