"""What the game's two searches share (ai/minimax.py, ai/brs.py).

Scoring the root moves, and the memory that the searches for one bot move
(1, 2, ... plies, see ai.policy.compute_move_in_time) pass on from one depth
to the next. web/src/engine/ai.js has the same in JavaScript.
"""

import math
import random

from core.rules import make_expanded_move, unmake_move

EXACT, LOWER, UPPER = 0, 1, 2   # transposition-table entry flags

WIN = 10000   # magnitude of a win/loss; +depth prefers faster wins

# Anti-repetition / variety knobs (eval is in [-1, 1]).
REPEAT_PENALTY = 0.5   # demotion per prior occurrence of the resulting position
TIE_EPS        = 0.02  # moves within this of the best are treated as equally good


class Memory:
    """What one search leaves for the next, deeper one of the same bot move.

    It changes the order and the amount of searching, never the result.
    """

    __slots__ = ('table', 'best', 'killers')

    def __init__(self):
        # Transposition table: (hash, plies left, bot to move) -> (value,
        # flag, best move). A value depends only on the position and the plies
        # left, so a shallower search's entries stay valid in a deeper one.
        self.table = {}
        # (hash, bot to move) -> the best move found there at any depth.
        self.best = {}
        # (plies left, bot to move) -> the last move that cut off a search there.
        self.killers = {}


def remember_best(memory, place, best, best_val, alpha0, beta0, maximizing):
    """Keep `best` as the move to try first at `place`, unless the node failed
    low (for the side to move): then no move was good, and `best` is merely
    the least bad bound, so an earlier hint is worth more."""
    if (best_val > alpha0) if maximizing else (best_val < beta0):
        memory.best[place] = best


def choose(board, moves, mode, history, memory, search_one):
    """The bot's move among the root `moves` (entries of `expanded_moves`).

    `search_one(floor)` returns the value for the bot of the position just
    reached, searched with alpha at `floor`. Moves that recreate a position
    already seen this game (`history`, Zobrist hashes) are demoted by
    `REPEAT_PENALTY` per earlier time, and the move is picked at random among
    those within `TIE_EPS` of the best. Only those need an exact value, so each
    move is searched with alpha just below the tie margin: a clearly worse
    move stops as soon as it is known to be out of the running. The best move
    of the last search goes first; the ties keep the order of `moves` (biggest
    captures first), whatever the search order.
    """
    seen = {}
    if history:
        for h in history:
            seen[h] = seen.get(h, 0) + 1

    moves.sort(key=lambda m: m[2], reverse=True)
    root = (board._hash, True)
    first = memory.best.get(root)
    order = sorted(range(len(moves)), key=lambda i: (moves[i][0], moves[i][1]) != first)
    values = [None] * len(moves)
    best_val = -math.inf
    best = None
    for i in order:
        move, cd, _n = moves[i]
        token = make_expanded_move(board, move, mode, cd)
        penalty = REPEAT_PENALTY * seen.get(board._hash, 0)
        floor = best_val - TIE_EPS + penalty - 1e-9
        val = search_one(floor) - penalty
        unmake_move(board, token)
        values[i] = val
        if val > best_val:
            best_val, best = val, (move, cd)
    memory.best[root] = best

    ties = [(move, cd) for val, (move, cd, _n) in zip(values, moves)
            if val >= best_val - TIE_EPS]
    return random.choice(ties)
