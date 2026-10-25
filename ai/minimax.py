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

from ai import deadline
from ai.search import EXACT, LOWER, UPPER, WIN, Memory, choose, remember_best
from core import rules
from core.rules import make_expanded_move, unmake_move, expanded_moves

# ── Evaluation weights — tune these to taste ──────────────────────────────────
W_CAPTURE = 0.7   # ăn quân (material) — humans like capturing
W_BLOCK   = 0.3   # chặn nước đi đối thủ (mobility/blockade) — the real win


def _evaluate(board, my_color, enemy_color, mode):
    my_count, my_moves = rules.count_pieces_and_moves(my_color, board, mode)
    en_count, en_moves = rules.count_pieces_and_moves(enemy_color, board, mode)
    total = my_count + en_count
    capture = (my_count - en_count) / total if total else 0.0

    mtot = my_moves + en_moves
    block = (my_moves - en_moves) / mtot if mtot else 0.0

    return W_CAPTURE * capture + W_BLOCK * block


def _search(board, depth, alpha, beta, maximizing, my_color, enemy_color, mode, memory):
    """`memory` (an ai.search.Memory) holds the transposition table and the
    best move found in each position by any search so far, shallower ones
    included, which is tried first."""
    deadline.check()
    if depth == 0:
        return _evaluate(board, my_color, enemy_color, mode), None

    alpha0, beta0 = alpha, beta
    place = (board._hash, maximizing)
    key = (board._hash, depth, maximizing)
    tt = memory.table
    hit = tt.get(key)
    tt_best = memory.best.get(place)
    if hit is not None:
        val, flag, tt_best = hit
        if flag == EXACT:
            return val, tt_best
        if flag == LOWER:
            if val > alpha:
                alpha = val
        elif flag == UPPER:
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
        score = -(WIN + depth) if color == my_color else (WIN + depth)
        return score, None

    # Ordering: the best move known here first, then biggest captures.
    moves.sort(key=lambda m: ((m[0], m[1]) == tt_best, m[2]), reverse=True)

    best = None
    if maximizing:
        best_val = -math.inf
        for move, cd, _n in moves:
            tok = make_expanded_move(board, move, mode, cd)
            val, _ = _search(board, depth - 1, alpha, beta, False,
                             my_color, enemy_color, mode, memory)
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
                             my_color, enemy_color, mode, memory)
            unmake_move(board, tok)
            if val < best_val:
                best_val, best = val, (move, cd)
            if val < beta:
                beta = val
            if beta <= alpha:
                break

    if best_val <= alpha0:
        flag = UPPER
    elif best_val >= beta0:
        flag = LOWER
    else:
        flag = EXACT
    tt[key] = (best_val, flag, best)
    remember_best(memory, place, best, best_val, alpha0, beta0, maximizing)
    return best_val, best


def best_move(board, my_color, mode, depth=None, history=None, memory=None):
    """Return best (move, capture_direction) for `my_color`, or None.

    `move` is (fx, fy, tx, ty); `capture_direction` is the chosen sandwich ray
    (or None). `memory` (an ai.search.Memory) carries what a shallower search
    of the same position found; it changes the order and amount of
    searching, not the result.

    Two things keep the bot from playing the same line forever (fix #3). The
    eval is a continuous score, so exact ties between moves essentially never
    happen — instead every move within `TIE_EPS` of the best counts as
    equally good and one is picked at random (variety across games). And any
    move that lands the board back on a position already seen this game
    (`history`, a list of Zobrist hashes) is demoted by `REPEAT_PENALTY`, so
    the bot stops shuffling a piece back and forth between two squares. Both
    are in ai.search.choose.
    """
    if depth is None:
        depth = mode.ai_depth
    enemy_color = next(c for c in mode.players if c != my_color)
    moves = expanded_moves(my_color, board, mode)
    if not moves:
        return None
    if memory is None:
        memory = Memory()
    return choose(board, moves, mode, history, memory, lambda floor: _search(
        board, depth - 1, floor, math.inf, False, my_color, enemy_color, mode, memory)[0])
