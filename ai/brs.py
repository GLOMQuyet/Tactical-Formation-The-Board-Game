"""Best-Reply Search for 3/4-player modes (Schadd & Winands, 2011).

The bot's own moves alternate with a single reply: of all the moves every
opponent could make, the one worst for the bot, while the other opponents
pass. So 6 plies see three moves of the bot and three answers, as in a
2-player game, where Paranoid search (ai/paranoid.py) would spend most plies
on the opponents' turns, and with four players, depending on the turn order,
not even reach the next human move.

Like the 2-player engine it uses make/unmake, a transposition table on the
board's Zobrist hash, move ordering for alpha-beta cutoffs, and randomises
among equally-best root moves. The evaluation is Paranoid's: the bot's
pieces against all the others' together, and its own mobility.
"""

import math
import random

from ai import deadline
from ai.paranoid import _evaluate
from core.rules import make_expanded_move, unmake_move, expanded_moves

_EXACT, _LOWER, _UPPER = 0, 1, 2   # transposition-table entry flags

_WIN = 10000   # magnitude of a win/loss; +depth prefers faster wins

# Anti-repetition / variety knobs (eval is in [-1, 1]) — see ai.minimax.
_REPEAT_PENALTY = 0.5
_TIE_EPS        = 0.02


def _search(board, depth, alpha, beta, maximizing, my_color, opponents, mode, tt, hints):
    """Value of the position for `my_color`; `opponents` are the sides still in.

    At the bot's plies it picks its best move; at the others' plies the
    opponents' moves are pooled and the worst one for the bot is taken.
    `hints` holds the best move found in each position by any search so far,
    shallower ones included, and is tried first.
    """
    deadline.check()
    if depth == 0:
        return _evaluate(board, my_color, mode), None

    alpha0, beta0 = alpha, beta
    place = (board._hash, maximizing, opponents)
    key = (place, depth)
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

    if maximizing:
        moves = expanded_moves(my_color, board, mode)
        if not moves:
            return -(_WIN + depth), None   # the bot cannot move: it is out
    else:
        moves = []
        still_in = []
        for color in opponents:
            theirs = expanded_moves(color, board, mode)
            if theirs:
                still_in.append(color)
                moves.extend(theirs)
        if not still_in:
            return _WIN + depth, None   # no opponent can move: the bot has won
        # A side that cannot move is out (core.state.GameState.start_turn).
        opponents = tuple(still_in)

    # Ordering: the best move known here first, then the move that last cut
    # off a search at this ply elsewhere (a "killer"), then biggest captures.
    killer_key = (depth, maximizing)
    killer = hints.get(killer_key)
    moves.sort(key=lambda m: ((m[0], m[1]) == tt_best, (m[0], m[1]) == killer, m[2]),
               reverse=True)

    best = None
    if maximizing:
        best_val = -math.inf
        for move, cd, _n in moves:
            tok = make_expanded_move(board, move, mode, cd)
            val, _ = _search(board, depth - 1, alpha, beta, False,
                             my_color, opponents, mode, tt, hints)
            unmake_move(board, tok)
            if val > best_val:
                best_val, best = val, (move, cd)
            if val > alpha:
                alpha = val
            if beta <= alpha:
                hints[killer_key] = (move, cd)
                break
    else:
        best_val = math.inf
        for move, cd, _n in moves:
            tok = make_expanded_move(board, move, mode, cd)
            val, _ = _search(board, depth - 1, alpha, beta, True,
                             my_color, opponents, mode, tt, hints)
            unmake_move(board, tok)
            if val < best_val:
                best_val, best = val, (move, cd)
            if val < beta:
                beta = val
            if beta <= alpha:
                hints[killer_key] = (move, cd)
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


def best_move(board, active_players, turn_index, mode, depth=None, history=None,
              hints=None):
    """Return best (move, capture_direction) for the current player, or None.

    Like the 2-player engine, demotes moves that recreate a position already
    seen this game (`history`) and picks at random among moves within
    `_TIE_EPS` of the best. Only those moves need an exact value, so each root
    move is searched with alpha just below the tie margin: a clearly worse
    move stops as soon as it is known to be out of the running.

    `hints` (a dict) carries the best moves found from one search to the next
    one deeper (ai.policy.compute_move_in_time); they change the order of the
    search, not its result.
    """
    if depth is None:
        depth = mode.ai_depth
    my_color = active_players[turn_index % len(active_players)]
    opponents = tuple(c for c in active_players if c != my_color)
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
    root = (board._hash, True, opponents)
    first = hints.get(root)
    order = sorted(range(len(moves)), key=lambda i: (moves[i][0], moves[i][1]) != first)
    tt = {}
    values = [None] * len(moves)
    best_val = -math.inf
    best = None
    for i in order:
        move, cd, _n = moves[i]
        tok = make_expanded_move(board, move, mode, cd)
        penalty = _REPEAT_PENALTY * seen.get(board._hash, 0)
        floor = best_val - _TIE_EPS + penalty - 1e-9
        val, _ = _search(board, depth - 1, floor, math.inf, False,
                         my_color, opponents, mode, tt, hints)
        unmake_move(board, tok)
        val -= penalty
        values[i] = val
        if val > best_val:
            best_val, best = val, (move, cd)
    hints[root] = best

    ties = [(move, cd) for val, (move, cd, _n) in zip(values, moves)
            if val >= best_val - _TIE_EPS]
    return random.choice(ties)
