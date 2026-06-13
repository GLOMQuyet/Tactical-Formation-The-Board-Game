"""Dispatcher: takes a GameState, returns the best move for the current player.

UI calls this through a thread pool so the game loop doesn't freeze during
search.
"""

from ai import minimax, paranoid


def compute_move(state):
    """Synchronous — clone the board and search. Safe to call in a worker."""
    mode = state.mode
    board = state.board.clone()
    if mode.ai_engine == 'minimax':
        return minimax.best_move(board, state.current_player, mode)
    elif mode.ai_engine == 'paranoid':
        return paranoid.best_move(board, list(state.active_players),
                                  state.turn_index, mode)
    raise ValueError(f"Unknown ai_engine: {mode.ai_engine}")
