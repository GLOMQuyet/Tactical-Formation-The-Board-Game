"""A time limit for one bot search in the game (ai.policy.compute_move_in_time).

The searches call `check()` at every node. Without a limit (the experiments,
the tests) it only compares a variable with None.
"""

import time
from contextlib import contextmanager


class OutOfTime(Exception):
    """The search went past its time limit."""


_at = None


def check():
    if _at is not None and time.perf_counter() > _at:
        raise OutOfTime


@contextmanager
def until(moment):
    """Searches inside the block stop with OutOfTime after `moment` (perf_counter)."""
    global _at
    _at = moment
    try:
        yield
    finally:
        _at = None
