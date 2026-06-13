"""Board geometry primitives — pure, no pygame.

The board uses a hybrid coordinate system: integer points are vertex squares,
half-integer points (e.g. 0.5, 1.5) are diamond-centre squares between them.
"""


def is_vertex(pos):
    return pos[0] % 1 == 0 and pos[1] % 1 == 0


def is_center(pos):
    return pos[0] % 1 == 0.5 and pos[1] % 1 == 0.5


_MOVE_DIRS_VERTEX = (
    (0, -1, 1), (1, 0, 1), (0, 1, 1), (-1, 0, 1),
    (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5),
)
_MOVE_DIRS_CENTER = (
    (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5),
)

_CAPTURE_DIRS_VERTEX = (
    (0, -1), (1, 0), (0, 1), (-1, 0),
    (-1, -1), (-1, 1), (1, -1), (1, 1),
)
_CAPTURE_DIRS_CENTER = (
    (-1, -1), (-1, 1), (1, -1), (1, 1),
)


def move_directions(pos):
    if is_vertex(pos):
        return _MOVE_DIRS_VERTEX
    if is_center(pos):
        return _MOVE_DIRS_CENTER
    return ()


def capture_directions(pos):
    if is_vertex(pos):
        return _CAPTURE_DIRS_VERTEX
    if is_center(pos):
        return _CAPTURE_DIRS_CENTER
    return ()
