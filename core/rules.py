"""Single source of truth for game rules.

All move/capture/win logic lives here. Parameterised by a Mode so the
2/3/4-player variants share one code path. Takes a Board (with O(1)
position index) instead of a raw piece list, which keeps the hot
`piece_at` lookup constant-time during search.
"""

from core.board import _zob
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


# The board's geometry never changes, so the jumps and capture rays from each
# point are worked out once per board shape and looked up in the hot paths
# (the bots call them hundreds of thousands of times per move).
_GEOMETRY = {}   # (board_width, board_height, excluded_cells) -> (jumps, rays)


def _geometry(mode):
    key = (mode.board_width, mode.board_height, mode.excluded_cells)
    tables = _GEOMETRY.get(key)
    if tables is None:
        tables = _GEOMETRY[key] = ({}, {})
    return tables


def _jumps_from(pos, mode):
    """((adjacent, landing), ...) for every jump from `pos` that stays on the board.

    The move direction tables already preserve vertex/center kind
    (land = src + 2·dir), so no kind check is needed.
    """
    px, py = pos
    bw = mode.board_width
    bh = mode.board_height
    excluded = mode.excluded_cells
    out = []
    for dx, dy, _step in move_directions(pos):
        ax = px + dx
        ay = py + dy
        if ax < 0 or ax > bw or ay < 0 or ay > bh:
            continue
        lx = px + 2 * dx
        ly = py + 2 * dy
        if lx < 0 or lx > bw or ly < 0 or ly > bh:
            continue
        if (lx, ly) in excluded:
            continue
        out.append(((ax, ay), (lx, ly)))
    return tuple(out)


def _rays_from(pos, mode):
    """((direction, (point, point, ...)), ...): the capture rays from `pos`."""
    bw = mode.board_width
    bh = mode.board_height
    out = []
    for dx, dy in capture_directions(pos):
        x, y = pos
        step = 1 if (dx == 0 or dy == 0) else 0.5
        ray = []
        while True:
            x += dx * step
            y += dy * step
            if x < 0 or x > bw or y < 0 or y > bh:
                break
            ray.append((x, y))
        out.append(((dx, dy), tuple(ray)))
    return tuple(out)


def legal_moves(piece, board, mode):
    """All landing squares the piece can jump to under `mode`."""
    jumps_by_pos = _geometry(mode)[0]
    pos = (piece.x, piece.y)
    jumps = jumps_by_pos.get(pos)
    if jumps is None:
        jumps = jumps_by_pos[pos] = _jumps_from(pos, mode)
    index = board._index
    # Need an adjacent piece to jump over, and an empty landing square.
    return [land for adj, land in jumps if adj in index and land not in index]


def count_moves(color, board, mode):
    """Number of legal moves for `color` — counts without building tuples."""
    return count_pieces_and_moves(color, board, mode)[1]


def count_pieces_and_moves(color, board, mode):
    """(pieces, legal moves) of `color`, in one pass — the bots' evaluation."""
    jumps_by_pos = _geometry(mode)[0]
    index = board._index
    pieces = 0
    n = 0
    for p in board.pieces:
        if p.color != color:
            continue
        pieces += 1
        pos = (p.x, p.y)
        jumps = jumps_by_pos.get(pos)
        if jumps is None:
            jumps = jumps_by_pos[pos] = _jumps_from(pos, mode)
        for adj, land in jumps:
            if adj in index and land not in index:
                n += 1
    return pieces, n


def find_captures(moved_piece, board, mode):
    """Return {direction: [enemy_pieces_to_flip]} for each sandwich ray."""
    rays_by_pos = _geometry(mode)[1]
    src = (moved_piece.x, moved_piece.y)
    rays = rays_by_pos.get(src)
    if rays is None:
        rays = rays_by_pos[src] = _rays_from(src, mode)
    index = board._index
    my_color = moved_piece.color
    options = {}
    for direction, ray in rays:
        to_flip = []
        for cell in ray:
            other = index.get(cell)
            if other is None:
                break
            if other.color != my_color:
                to_flip.append(other)
            else:
                if to_flip:
                    options[direction] = to_flip
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


def make_expanded_move(board, move, mode, capture_direction):
    """`make_move` for an entry of `expanded_moves`, which already says what it flips.

    `capture_direction` None means the move flips nothing, so the rays are not
    searched again; otherwise only that ray is walked. The bots' searches use
    this; the result is the same as `make_move`'s for such an entry.
    """
    fx, fy, tx, ty = move
    index = board._index
    p = index[(fx, fy)]
    color = p.color
    board._hash ^= _zob((fx, fy), color)
    board.move_piece(p, (tx, ty))
    board._hash ^= _zob((tx, ty), color)

    flipped = []
    if capture_direction is not None:
        rays_by_pos = _geometry(mode)[1]
        rays = rays_by_pos.get((tx, ty))
        if rays is None:
            rays = rays_by_pos[(tx, ty)] = _rays_from((tx, ty), mode)
        for direction, ray in rays:
            if direction != capture_direction:
                continue
            for cell in ray:
                other = index[cell]
                if other.color == color:
                    break
                flipped.append((other, other.color))
            break
        for enemy, old in flipped:
            board._hash ^= _zob((enemy.x, enemy.y), old)
            enemy.color = color
            board._hash ^= _zob((enemy.x, enemy.y), color)
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
    always grabbing the biggest flip. Pure: the board is not changed. The
    rays are those `find_captures` would see with the piece on its landing
    square, so its starting square counts as empty. The bots call this at
    every node, so the jump and ray loops are written out here.
    """
    jumps_by_pos, rays_by_pos = _geometry(mode)
    index = board._index
    out = []
    for p in board.pieces:
        if p.color != color:
            continue
        src = (p.x, p.y)
        jumps = jumps_by_pos.get(src)
        if jumps is None:
            jumps = jumps_by_pos[src] = _jumps_from(src, mode)
        for adj, land in jumps:
            if adj not in index or land in index:
                continue
            rays = rays_by_pos.get(land)
            if rays is None:
                rays = rays_by_pos[land] = _rays_from(land, mode)
            move = (src[0], src[1], land[0], land[1])
            found = False
            for direction, ray in rays:
                n = 0
                for cell in ray:
                    if cell == src:          # the jumping piece has left it
                        break
                    other = index.get(cell)
                    if other is None:
                        break
                    if other.color != color:
                        n += 1
                    else:
                        if n:
                            out.append((move, direction, n))
                            found = True
                        break
            if not found:
                out.append((move, None, 0))
    return out


def is_alive(color, board, mode):
    """A player is alive if they have at least one piece AND a legal move."""
    return (
        any(p.color == color for p in board.pieces)
        and has_available_moves(color, board, mode)
    )
