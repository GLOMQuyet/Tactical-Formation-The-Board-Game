"""Run a bot search in a separate process so the window keeps responding.

A thread is not enough: the search is pure Python, and a thread would share
the interpreter lock with the game loop, slowing both the search and the
redraws. A worker process runs on its own core instead. It is started once
and reused for every move; `cancel()` (undo, restart, leaving the game) stops
a search that is still running. If the worker process dies (for example when
the computer runs out of memory) its search would never finish, so a search
that takes far longer than any real one is started again in a new process.
"""

import multiprocessing
import time

from ai.policy import compute_move_in_time
from core.state import GameState

# "spawn" behaves the same on Windows, macOS and Linux, and avoids forking a
# process that already runs SDL threads.
_CONTEXT = multiprocessing.get_context('spawn')

# A search keeps to about ai.policy.TIME_BUDGET; one taking minutes is stuck.
STALL_SECONDS = 120


class BotWorker:
    def __init__(self, search=compute_move_in_time, stall_seconds=STALL_SECONDS):
        # `search` runs in the worker process, so it must be a module-level
        # function (picklable). Tests pass small fakes.
        self._search = search
        self._stall_seconds = stall_seconds
        self._pool = None
        self._pending = None   # multiprocessing AsyncResult of the current search
        self._snapshot = None
        self._started = 0.0

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
        self._snapshot = snapshot
        self._submit()

    def _submit(self):
        self.warm_up()
        self._started = time.monotonic()
        self._pending = self._pool.apply_async(self._search, (self._snapshot,))

    def done(self):
        """True once the current search has finished.

        A search running past `stall_seconds` is restarted in a new process.
        """
        if self._pending is None:
            return False
        if self._pending.ready():
            return True
        if time.monotonic() - self._started > self._stall_seconds:
            self.close()
            self._submit()
        return False

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
            self.warm_up()   # start the next process now, not at the next search
        self._pending = None

    def close(self):
        """Stop the worker process."""
        if self._pool is not None:
            self._pool.terminate()
            self._pool.join()
            self._pool = None
