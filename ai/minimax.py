"""Alpha-beta minimax for 2-player mode.

Operates on `core.board.Board` — no pygame, safe to run in a worker thread.
Uses make/unmake (no per-node board clone), a transposition table keyed on the
board's Zobrist hash, and move ordering for stronger alpha-beta cutoffs.

Evaluation thinks like a human player: 0.7 weight on capturing pieces, 0.3 on
restricting the opponent's moves (toward a blockade win). Both terms are
normalised to [-1, 1] so the weights are meaningful. The bot also considers
*non-greedy* captures (via `rules.expanded_moves`) instead of always grabbing
the biggest flip, and randomises among equally-best moves so it is no longer
perfectly repeatable.
"""

import math
import random

from ai import deadline
from core import rules
from core.rules import make_expanded_move, unmake_move, expanded_moves

# ── Evaluation weights — tune these to taste ──────────────────────────────────
W_CAPTURE = 0.7   # ăn quân (material) — humans like capturing
W_BLOCK   = 0.3   # chặn nước đi đối thủ (mobility/blockade) — the real win

# Transposition-table entry flags.
_EXACT, _LOWER, _UPPER = 0, 1, 2

_WIN = 10000   # magnitude of a win/loss; +depth prefers faster wins

# Anti-repetition / variety knobs (eval is in [-1, 1]).
_REPEAT_PENALTY = 0.5   # demotion per prior occurrence of the resulting position
_TIE_EPS        = 0.02  # moves within this of the best are treated as equally good


def _evaluate(board, my_color, enemy_color, mode):
    my_count, my_moves = rules.count_pieces_and_moves(my_color, board, mode)
    en_count, en_moves = rules.count_pieces_and_moves(enemy_color, board, mode)
    total = my_count + en_count
    capture = (my_count - en_count) / total if total else 0.0

    mtot = my_moves + en_moves
    block = (my_moves - en_moves) / mtot if mtot else 0.0

    return W_CAPTURE * capture + W_BLOCK * block


def _search(board, depth, alpha, beta, maximizing, my_color, enemy_color, mode, tt, hints):
    """`hints` holds the best move found in each position by any search so far,
    shallower ones included, and is tried first."""
    deadline.check()
    if depth == 0:
        return _evaluate(board, my_color, enemy_color, mode), None

    alpha0, beta0 = alpha, beta
    place = (board._hash, maximizing)
    key = (board._hash, depth, maximizing)
    hit = tt.get(key)
    tt_best = hints.get(place)
    if hit is not None:
        val, flag, tt_best = hit
        if flag == _EXACT:
            return val, tt_best
        if flag == _LOWER:
            if val > alpha:
                alpha = val
        elif flag == _UPPER:
            if val < beta:
                beta = val
        if alpha >= beta:
            return val, tt_best

    color = my_color if maximizing else enemy_color
    moves = expanded_moves(color, board, mode)
    if not moves:
        # Side to move is stuck (no pieces or no legal move) -> it loses.
        # Equivalent to the old `not is_alive(color)` terminal, but folded into
        # move generation so no extra scan is needed per node.
        score = -(_WIN + depth) if color == my_color else (_WIN + depth)
        return score, None

    # Ordering: the best move known here first, then biggest captures.
    moves.sort(key=lambda m: ((m[0], m[1]) == tt_best, m[2]), reverse=True)

    best = None
    if maximizing:
        best_val = -math.inf
        for move, cd, _n in moves:
            tok = make_expanded_move(board, move, mode, cd)
            val, _ = _search(board, depth - 1, alpha, beta, False,
                             my_color, enemy_color, mode, tt, hints)
            unmake_move(board, tok)
            if val > best_val:
                best_val, best = val, (move, cd)
            if val > alpha:
                alpha = val
            if beta <= alpha:
                break
    else:
        best_val = math.inf
        for move, cd, _n in moves:
            tok = make_expanded_move(board, move, mode, cd)
            val, _ = _search(board, depth - 1, alpha, beta, True,
                             my_color, enemy_color, mode, tt, hints)
            unmake_move(board, tok)
            if val < best_val:
                best_val, best = val, (move, cd)
            if val < beta:
                beta = val
            if beta <= alpha:
                break

    if best_val <= alpha0:
        flag = _UPPER
    elif best_val >= beta0:
        flag = _LOWER
    else:
        flag = _EXACT
    tt[key] = (best_val, flag, best)
    hints[place] = best
    return best_val, best


def best_move(board, my_color, mode, depth=None, history=None, hints=None):
    """Return best (move, capture_direction) for `my_color`, or None.

    `move` is (fx, fy, tx, ty); `capture_direction` is the chosen sandwich ray
    (or None). Only the moves within `_TIE_EPS` of the best (below) need an
    exact value, so each root move is searched with alpha just below that
    margin: a clearly worse move stops as soon as it is known to be out of the
    running. `hints` (a dict) carries the best moves found from one search to
    the next one deeper (ai.policy.compute_move_in_time); they change the
    order of the search, not its result.

    Two things keep the bot from playing the same line forever (fix #3). The
    eval is a continuous score, so exact ties between moves essentially never
    happen — instead we treat every move within `_TIE_EPS` of the best as
    equally good and pick one at random (variety across games). And any move
    that lands the board back on a position already seen this game (`history`,
    a list of Zobrist hashes) is demoted by `_REPEAT_PENALTY`, so the bot stops
    shuffling a piece back and forth between two squares.
    """
    if depth is None:
        depth = mode.ai_depth
    enemy_color = next(c for c in mode.players if c != my_color)
    moves = expanded_moves(my_color, board, mode)
    if not moves:
        return None

    seen = {}
    if history:
        for h in history:
            seen[h] = seen.get(h, 0) + 1

    if hints is None:
        hints = {}
    moves.sort(key=lambda m: m[2], reverse=True)
    # Search the best move of the last search first: the others then mostly
    # stop early. The ties keep the order above, whatever the search order.
    root = (board._hash, True)
    first = hints.get(root)
    order = sorted(range(len(moves)), key=lambda i: (moves[i][0], moves[i][1]) != first)
    tt = {}
    values = [None] * len(moves)
    best_val = -math.inf
    best = None
    for i in order:
        move, cd, _n = moves[i]
        tok = make_expanded_move(board, move, mode, cd)
        # The hash of the resulting position, against the game so far.
        penalty = _REPEAT_PENALTY * seen.get(board._hash, 0)
        floor = best_val - _TIE_EPS + penalty - 1e-9
        val, _ = _search(board, depth - 1, floor, math.inf, False,
                         my_color, enemy_color, mode, tt, hints)
        unmake_move(board, tok)
        val -= penalty
        values[i] = val
        if val > best_val:
            best_val, best = val, (move, cd)
    hints[root] = best

    ties = [(move, cd) for val, (move, cd, _n) in zip(values, moves)
            if val >= best_val - _TIE_EPS]
    return random.choice(ties)
