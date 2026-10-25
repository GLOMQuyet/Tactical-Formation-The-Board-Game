"""Dispatcher: takes a GameState, returns the best move for the current player.

The game screen calls `compute_move_in_time` through `ai.worker.BotWorker`, in
a separate process, so the window keeps responding during the search.
"""

import dataclasses
import math
import time

from ai import brs, deadline, minimax, paranoid
from ai.search import Memory

# The longest one bot move may take in the game (s): no limit. The bots
# always search the full depth of their difficulty (core.modes.DIFFICULTY_DEPTH),
# a few seconds at most on an ordinary computer.
TIME_BUDGET = math.inf


def compute_move(state, memory=None):
    """Synchronous — clone the board and search. Safe to call in a worker.

    Returns (move, capture_direction) for the current player, or None if there
    are no legal moves. `move` is (fx, fy, tx, ty); `capture_direction` is the
    sandwich ray the bot chose (or None). `memory` (an ai.search.Memory)
    carries what a shallower search of the same position found (see
    `compute_move_in_time`).
    """
    mode = state.mode
    board = state.board.clone()
    history = state.position_history
    if mode.ai_engine == 'minimax':
        return minimax.best_move(board, state.current_player, mode,
                                 history=history, memory=memory)
    elif mode.ai_engine == 'brs':
        return brs.best_move(board, list(state.active_players),
                             state.turn_index, mode, history=history, memory=memory)
    elif mode.ai_engine == 'paranoid':
        return paranoid.best_move(board, list(state.active_players),
                                  state.turn_index, mode, history=history)
    raise ValueError(f"Unknown ai_engine: {mode.ai_engine}")


def compute_move_in_time(state, budget=TIME_BUDGET):
    """`compute_move` searching 1, 2, ... plies up to the mode's depth.

    Each search leaves what it found in `memory` for the next, which makes the
    deepest one faster than searching it alone. In the game there is no time
    limit; with a `budget` (seconds), a deeper search still running after it
    is given up,
    and the move of the deepest finished one is played (one ply always
    finishes, so there is always a move). When time allows, the move is one
    `compute_move` could play: the same search, though the random pick among
    equally good moves may fall differently.
    """
    stop = time.perf_counter() + budget
    memory = Memory()   # what each search leaves for the next, deeper one
    result = None
    for depth in range(1, state.mode.ai_depth + 1):
        shallower = dataclasses.replace(
            state, mode=dataclasses.replace(state.mode, ai_depth=depth))
        if depth == 1:
            found = compute_move(shallower, memory)
        else:
            try:
                with deadline.until(stop):
                    found = compute_move(shallower, memory)
            except deadline.OutOfTime:
                break
        result = found
        if found is None or time.perf_counter() >= stop:
            break
    return result
