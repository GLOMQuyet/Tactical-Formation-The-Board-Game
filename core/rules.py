"""Single source of truth for game rules.

All move/capture/win logic lives here. Parameterised by a Mode so the
2/3/4-player variants share one code path. Takes a Board (with O(1)
position index) instead of a raw piece list, which keeps the hot
`piece_at` lookup constant-time during search.
"""

from core.board import _zob
from core.geometry import move_directions, capture_directions


def legal_moves(piece, board, mode):
    """All landing squares the piece can jump to under `mode`.

    Hot path, so the bounds checks are written out. No vertex/centre check is
    needed: the move direction tables keep the kind (land = src + 2·dir), so
    a piece always lands on the same kind of point it left.
    """
    px = piece.x
    py = piece.y
    bw = mode.board_width
    bh = mode.board_height
    excluded = mode.excluded_cells
    index = board._index
    moves = []
    for dx, dy, _step in move_directions((px, py)):
        ax = px + dx
        ay = py + dy
        if ax < 0 or ax > bw or ay < 0 or ay > bh:
            continue
        lx = px + 2 * dx
        ly = py + 2 * dy
        if lx < 0 or lx > bw or ly < 0 or ly > bh:
            continue
        land = (lx, ly)
        if land in excluded:
            continue
        if (ax, ay) not in index:        # need an adjacent piece to jump over
            continue
        if land in index:                # landing must be empty
            continue
        moves.append(land)
    return moves


def count_moves(color, board, mode):
    """Number of legal moves for `color` — counts without building tuples."""
    n = 0
    for p in board.pieces:
        if p.color == color:
            n += len(legal_moves(p, board, mode))
    return n


def find_captures(moved_piece, board, mode):
    """Return {direction: [enemy_pieces_to_flip]} for each sandwich ray."""
    src = (moved_piece.x, moved_piece.y)
    bw = mode.board_width
    bh = mode.board_height
    index = board._index
    my_color = moved_piece.color
    options = {}
    for dx, dy in capture_directions(src):
        x, y = moved_piece.x, moved_piece.y
        to_flip = []
        step = 1 if (dx == 0 or dy == 0) else 0.5
        while True:
            x += dx * step
            y += dy * step
            if x < 0 or x > bw or y < 0 or y > bh:
                break
            other = index.get((x, y))
            if other is None:
                break
            if other.color != my_color:
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


def make_move(board, move, mode, capture_direction=None):
    """Mutate `board`: move the piece, flip one capture ray; return an undo token.

    The flipped ray is `capture_direction` when given and available, otherwise
    the greediest (most flips) — matching the old `apply_move` default. The
    returned token is `(moved_piece, from_pos, [(enemy, old_color), ...])`; pass
    it to `unmake_move` to restore the board exactly. `board._hash` is kept in
    sync so AI search can use it as a transposition-table key. Returns None if
    there is no piece at the source.
    """
    fx, fy, tx, ty = move
    p = board.piece_at((fx, fy))
    if p is None:
        return None
    board._hash ^= _zob((fx, fy), p.color)
    board.move_piece(p, (tx, ty))
    board._hash ^= _zob((tx, ty), p.color)

    flipped = []
    captures = find_captures(p, board, mode)
    if captures:
        if capture_direction is not None and capture_direction in captures:
            chosen = capture_direction
        else:
            chosen = max(captures.keys(), key=lambda d: len(captures[d]))
        for enemy in captures[chosen]:
            flipped.append((enemy, enemy.color))
            board._hash ^= _zob((enemy.x, enemy.y), enemy.color)
            enemy.color = p.color
            board._hash ^= _zob((enemy.x, enemy.y), enemy.color)
    return (p, (fx, fy), flipped)


def unmake_move(board, token):
    """Reverse a `make_move` using its token — positions, colors, hash restored."""
    if token is None:
        return
    p, from_pos, flipped = token
    for enemy, old_color in flipped:
        board._hash ^= _zob((enemy.x, enemy.y), enemy.color)
        enemy.color = old_color
        board._hash ^= _zob((enemy.x, enemy.y), enemy.color)
    cur = (p.x, p.y)
    board._hash ^= _zob(cur, p.color)
    board.move_piece(p, from_pos)
    board._hash ^= _zob(from_pos, p.color)


def apply_move(board, move, mode, capture_direction=None):
    """Mutate `board`: move the piece, then flip captured enemies.

    Returns (moved_piece, list_of_flipped_pieces). If `capture_direction` is
    None and multiple capture rays exist, the greediest ray (most flips) is
    auto-chosen. Thin wrapper over `make_move` — used by the UI.
    """
    token = make_move(board, move, mode, capture_direction)
    if token is None:
        return None, []
    p, _from, flipped = token
    return p, [enemy for enemy, _old in flipped]


def expanded_moves(color, board, mode):
    """Like `all_moves` but each entry is (move, capture_direction, n_flips).

    When a landing creates more than one capture ray, yields one entry per ray
    so the AI can consider taking a smaller (non-greedy) capture instead of
    always grabbing the biggest flip. Pure: temporarily moves the piece to
    inspect rays, then restores it (board._hash is left untouched).
    """
    out = []
    for p in board.pieces:
        if p.color != color:
            continue
        src = (p.x, p.y)
        for tx, ty in legal_moves(p, board, mode):
            board.move_piece(p, (tx, ty))
            caps = find_captures(p, board, mode)
            board.move_piece(p, src)
            move = (src[0], src[1], tx, ty)
            if not caps:
                out.append((move, None, 0))
            elif len(caps) == 1:
                d = next(iter(caps))
                out.append((move, d, len(caps[d])))
            else:
                for d, flipped in caps.items():
                    out.append((move, d, len(flipped)))
    return out


def is_alive(color, board, mode):
    """A player is alive if they have at least one piece AND a legal move."""
    return (
        any(p.color == color for p in board.pieces)
        and has_available_moves(color, board, mode)
    )
