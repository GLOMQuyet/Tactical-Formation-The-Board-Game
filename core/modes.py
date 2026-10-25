"""Mode configurations — the 3 supported game variants live here.

Each Mode is a frozen description of a variant: board bounds, excluded cells,
starting layout per colour, turn order, who is human vs bot, AI depth.
Adding a new variant means adding a Mode object, not a new file tree.
"""

from dataclasses import dataclass, replace
from typing import Optional


@dataclass(frozen=True)
class Mode:
    name: str                       # 'play_2', 'bot_2', 'play_3', 'play_4'
    board_width: int                # max x (inclusive)
    board_height: int               # max y (inclusive)
    excluded_cells: frozenset       # cells that cannot be landed on
    start_positions: dict           # color -> tuple of (x, y) start positions
    players: tuple                  # turn order, e.g. ('green', 'yellow')
    bot_colors: frozenset           # subset of players that are AI
    human_colors: frozenset         # subset of players that are human
    eliminate_on_no_moves: bool     # True for 3p/4p; in 2p no-moves = loss
    bot_delay_ms: int               # least time from a bot's turn to its move,
                                    # so people can follow the bots' moves
    grid_rows: int                  # for renderer (visible grid)
    grid_cols: int
    square_size: int
    # ── fields with defaults — only required for modes with bots ───────────
    missing_cells: tuple = ()       # (col, row) lattice cells NOT part of the board
                                    # — used by the renderer to skip both the
                                    # diamond diagonals and the outer-edge
                                    # segments adjacent to those cells.
    ai_engine: Optional[str] = None # 'minimax' or 'paranoid'; None for human-only
    ai_depth: Optional[int] = None  # search depth; None for human-only


# ── 2-player layouts ─────────────────────────────────────────────────────────

_2P_YELLOW = (
    (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
    (0.5, 0.5), (1.5, 0.5), (2.5, 0.5), (3.5, 0.5),
    (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
)
_2P_GREEN = (
    (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
    (0.5, 3.5), (1.5, 3.5), (2.5, 3.5), (3.5, 3.5),
    (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
)

MODE_PLAY_2 = Mode(
    name='play_2',
    board_width=4, board_height=4,
    excluded_cells=frozenset(),
    start_positions={'yellow': _2P_YELLOW, 'green': _2P_GREEN},
    players=('green', 'yellow'),
    bot_colors=frozenset(),
    human_colors=frozenset({'green', 'yellow'}),
    eliminate_on_no_moves=False,
    bot_delay_ms=0,
    grid_rows=4, grid_cols=4, square_size=150,
)

MODE_BOT_2 = Mode(
    name='bot_2',
    board_width=4, board_height=4,
    excluded_cells=frozenset(),
    start_positions={'yellow': _2P_YELLOW, 'green': _2P_GREEN},
    players=('green', 'yellow'),
    bot_colors=frozenset({'yellow'}),
    human_colors=frozenset({'green'}),
    eliminate_on_no_moves=False,
    bot_delay_ms=400,
    grid_rows=4, grid_cols=4, square_size=150,
    ai_engine='minimax',
    ai_depth=6,
)

# ── 3-player layouts ─────────────────────────────────────────────────────────

_3P_YELLOW = (
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
    (0.5, 0.5), (0.5, 1.5), (0.5, 2.5), (0.5, 3.5),
    (1, 0), (1, 1), (1, 2), (1, 3),
)
_3P_GREEN = (
    (6, 0), (6, 1), (6, 2), (6, 3), (6, 4),
    (5.5, 0.5), (5.5, 1.5), (5.5, 2.5), (5.5, 3.5),
    (5, 0), (5, 1), (5, 2), (5, 3),
)
_3P_PURPLE = (
    (1, 5), (2, 5), (3, 5), (4, 5), (5, 5),
    (1.5, 4.5), (2.5, 4.5), (3.5, 4.5), (4.5, 4.5),
    (1, 4), (2, 4), (3, 4), (4, 4), (5, 4),
)
_3P_EXCLUDED = frozenset({(0, 5), (0.5, 4.5), (6, 5), (5.5, 4.5)})

MODE_PLAY_3 = Mode(
    name='play_3',
    board_width=6, board_height=5,
    excluded_cells=_3P_EXCLUDED,
    start_positions={'yellow': _3P_YELLOW, 'green': _3P_GREEN, 'purple': _3P_PURPLE},
    players=('purple', 'yellow', 'green'),
    bot_colors=frozenset({'purple', 'yellow'}),
    human_colors=frozenset({'green'}),
    eliminate_on_no_moves=True,
    bot_delay_ms=600,
    grid_rows=5, grid_cols=6, square_size=100,
    # bottom-left and bottom-right corner cells (col, row)
    missing_cells=((0, 4), (5, 4)),
    ai_engine='paranoid',
    ai_depth=6,
)

# 3-player human-only variant (used when user picks "Play Human → 3 Players")
MODE_PLAY_3_HUMAN = Mode(
    name='play_3_human',
    board_width=6, board_height=5,
    excluded_cells=_3P_EXCLUDED,
    start_positions={'yellow': _3P_YELLOW, 'green': _3P_GREEN, 'purple': _3P_PURPLE},
    players=('purple', 'yellow', 'green'),
    bot_colors=frozenset(),
    human_colors=frozenset({'purple', 'yellow', 'green'}),
    eliminate_on_no_moves=True,
    bot_delay_ms=0,
    grid_rows=5, grid_cols=6, square_size=100,
    missing_cells=((0, 4), (5, 4)),
)

# ── 4-player layouts ─────────────────────────────────────────────────────────

_4P_BLUE = (
    (1, 0), (2, 0), (3, 0), (4, 0), (5, 0),
    (1.5, 0.5), (2.5, 0.5), (3.5, 0.5), (4.5, 0.5),
    (1, 1), (2, 1), (3, 1), (4, 1),
)
_4P_YELLOW = (
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
    (0.5, 1.5), (0.5, 2.5), (0.5, 3.5), (0.5, 4.5),
    (1, 2), (1, 3), (1, 4), (1, 5),
)
_4P_PURPLE = (
    (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),
    (1.5, 5.5), (2.5, 5.5), (3.5, 5.5), (4.5, 5.5),
    (2, 5), (3, 5), (4, 5), (5, 5),
)
_4P_GREEN = (
    (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
    (5.5, 1.5), (5.5, 2.5), (5.5, 3.5), (5.5, 4.5),
    (5, 1), (5, 2), (5, 3), (5, 4),
)
_4P_EXCLUDED = frozenset({
    (0, 0), (0.5, 0.5), (6, 0), (5.5, 0.5),
    (0, 6), (0.5, 5.5), (6, 6), (5.5, 5.5),
})

MODE_PLAY_4 = Mode(
    name='play_4',
    board_width=6, board_height=6,
    excluded_cells=_4P_EXCLUDED,
    start_positions={
        'blue': _4P_BLUE, 'yellow': _4P_YELLOW,
        'purple': _4P_PURPLE, 'green': _4P_GREEN,
    },
    players=('blue', 'green', 'purple', 'yellow'),
    bot_colors=frozenset({'blue', 'purple', 'yellow'}),
    human_colors=frozenset({'green'}),
    eliminate_on_no_moves=True,
    bot_delay_ms=600,
    grid_rows=6, grid_cols=6, square_size=100,
    missing_cells=((0, 0), (5, 0), (0, 5), (5, 5)),
    ai_engine='paranoid',
    ai_depth=6,
)

# 4-player human-only variant (used when user picks "Play Human → 4 Players")
MODE_PLAY_4_HUMAN = Mode(
    name='play_4_human',
    board_width=6, board_height=6,
    excluded_cells=_4P_EXCLUDED,
    start_positions={
        'blue': _4P_BLUE, 'yellow': _4P_YELLOW,
        'purple': _4P_PURPLE, 'green': _4P_GREEN,
    },
    players=('blue', 'green', 'purple', 'yellow'),
    bot_colors=frozenset(),
    human_colors=frozenset({'blue', 'green', 'purple', 'yellow'}),
    eliminate_on_no_moves=True,
    bot_delay_ms=0,
    grid_rows=6, grid_cols=6, square_size=100,
    missing_cells=((0, 0), (5, 0), (0, 5), (5, 5)),
)


ALL_MODES = {
    'play_2': MODE_PLAY_2,
    'bot_2': MODE_BOT_2,
    'play_3': MODE_PLAY_3_HUMAN,
    'bot_3': MODE_PLAY_3,
    'play_4': MODE_PLAY_4_HUMAN,
    'bot_4': MODE_PLAY_4,
}


# ── Bot difficulty ────────────────────────────────────────────────────────────
# Search depth (plies) for each difficulty, keyed by Mode.name; 'hard' is each
# bot mode's default ai_depth. 4, 5 and 6 plies in every mode, as in the
# browser version. Each ply costs about 3 to 10 times the one before, and with
# three or four players 5 or 6 plies can take longer than a person should wait,
# so a bot gives up a ply that runs past the time limit and plays the deepest
# one it finished (ai.policy.compute_move_in_time). The paper measured fixed
# depths of 6, 4 and 3 plies for 2, 3 and 4 players (experiments/).

DIFFICULTIES = ('easy', 'medium', 'hard')

DIFFICULTY_DEPTH = {
    'bot_2':  {'easy': 4, 'medium': 5, 'hard': 6},
    'play_3': {'easy': 4, 'medium': 5, 'hard': 6},
    'play_4': {'easy': 4, 'medium': 5, 'hard': 6},
}


def with_difficulty(mode, level):
    """Return `mode` searching at the depth for `level` ('easy', 'medium', 'hard')."""
    return replace(mode, ai_depth=DIFFICULTY_DEPTH[mode.name][level])


MODES_BY_NAME = {m.name: m for m in ALL_MODES.values()}
