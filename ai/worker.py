"""Run a bot search in a separate process so the window keeps responding.

A thread is not enough: the search is pure Python, and a thread would share
the interpreter lock with the game loop, slowing both the search and the
redraws. A worker process runs on its own core instead. It is started once
and reused for every move; `cancel()` (undo, restart, leaving the game) stops
a search that is still running.
"""

import multiprocessing

from ai.policy import compute_move
from core.state import GameState

# "spawn" behaves the same on Windows, macOS and Linux, and avoids forking a
# process that already runs SDL threads.
_CONTEXT = multiprocessing.get_context('spawn')


class BotWorker:
    def __init__(self, search=compute_move):
        # `search` runs in the worker process, so it must be a module-level
        # function (picklable). Tests pass small fakes.
        self._search = search
        self._pool = None
        self._pending = None   # multiprocessing AsyncResult of the current search

    def warm_up(self):
        """Start the worker process now, so the first bot move does not wait for it."""
        if self._pool is None:
            self._pool = _CONTEXT.Pool(processes=1)

    @property
    def busy(self):
        """True from `start()` until the result is collected or cancelled."""
        return self._pending is not None

    def start(self, state):
        """Begin searching the current player's move in a snapshot of `state`."""
        snapshot = GameState(
            board=state.board.clone(),
            active_players=list(state.active_players),
            turn_index=state.turn_index,
            mode=state.mode,
            position_history=list(state.position_history),
        )
        self.warm_up()
        self._pending = self._pool.apply_async(self._search, (snapshot,))

    def done(self):
        """True once the current search has finished."""
        return self._pending is not None and self._pending.ready()

    def result(self):
        """Collect the finished search: (move, capture_direction) or None.

        Re-raises any error from the search, so a bug in the bot is not hidden.
        """
        pending, self._pending = self._pending, None
        return pending.get()

    def cancel(self):
        """Forget the current search, stopping it if it is still running."""
        if self._pending is not None and not self._pending.ready():
            self.close()   # a running search cannot be interrupted, only killed
        self._pending = None

    def close(self):
        """Stop the worker process."""
        if self._pool is not None:
            self._pool.terminate()
            self._pool.join()
            self._pool = None
