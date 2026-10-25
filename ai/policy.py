"""Dispatcher: takes a GameState, returns the best move for the current player.

The game screen calls `compute_move_in_time` through `ai.worker.BotWorker`, in
a separate process, so the window keeps responding during the search.
"""

import dataclasses
import time

from ai import deadline, minimax, paranoid

# About how long a person waits for one bot move in the game (s).
TIME_BUDGET = 2.0


def compute_move(state):
    """Synchronous — clone the board and search. Safe to call in a worker.

    Returns (move, capture_direction) for the current player, or None if there
    are no legal moves. `move` is (fx, fy, tx, ty); `capture_direction` is the
    sandwich ray the bot chose (or None).
    """
    mode = state.mode
    board = state.board.clone()
    history = state.position_history
    if mode.ai_engine == 'minimax':
        return minimax.best_move(board, state.current_player, mode,
                                 history=history)
    elif mode.ai_engine == 'paranoid':
        return paranoid.best_move(board, list(state.active_players),
                                  state.turn_index, mode, history=history)
    raise ValueError(f"Unknown ai_engine: {mode.ai_engine}")


def compute_move_in_time(state, budget=TIME_BUDGET):
    """`compute_move` searching 1, 2, ... plies up to the mode's depth.

    A deeper search that is still running after `budget` seconds is given up,
    and the move of the deepest finished one is played (one ply always
    finishes). When time allows, the result is exactly that of `compute_move`.
    """
    stop = time.perf_counter() + budget
    result = None
    for depth in range(1, state.mode.ai_depth + 1):
        shallower = dataclasses.replace(
            state, mode=dataclasses.replace(state.mode, ai_depth=depth))
        if depth == 1:
            found = compute_move(shallower)
        else:
            try:
                with deadline.until(stop):
                    found = compute_move(shallower)
            except deadline.OutOfTime:
                break
        result = found
        if found is None or time.perf_counter() >= stop:
            break
    return result
