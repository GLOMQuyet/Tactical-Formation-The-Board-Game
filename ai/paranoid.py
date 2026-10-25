"""Paranoid minimax for 3/4-player modes — current player maximises, all
others minimise together. Operates on `core.board.Board` (O(1) piece_at).

The game's 3/4-player bots use Best-Reply Search (ai/brs.py), which shares
this module's evaluation; Paranoid search stays for the experiments behind
the paper (experiments/), which measured it.

Like the 2-player engine it uses make/unmake (no per-node clone), considers
non-greedy captures via `rules.expanded_moves`, orders moves by capture size,
and randomises among equally-best root moves. Evaluation uses the same
human-like 0.7 capture / 0.3 mobility split. (No transposition table here —
the active-player set and turn cursor make the key fiddly; left for later.)
"""

import math
import random

from ai import deadline
from core import rules
from core.rules import make_move, unmake_move, expanded_moves

W_CAPTURE = 0.7   # ăn quân (material vs all opponents combined)
W_BLOCK   = 0.3   # giữ nước đi cho mình (mobility) — tránh bị phong tỏa

# Anti-repetition / variety knobs (eval is in [-1, 1]) — see ai.minimax.
_REPEAT_PENALTY = 0.5
_TIE_EPS        = 0.02


def _evaluate(board, my_color, mode):
    total = len(board.pieces)
    my_count, my_moves = rules.count_pieces_and_moves(my_color, board, mode)
    en_count = total - my_count
    capture = (my_count - en_count) / total if total else 0.0

    denom = my_moves + total
    block = my_moves / denom if denom else 0.0
    return W_CAPTURE * capture + W_BLOCK * block


def _advance_turn(board, active_players, turn_index, mode):
    """Return (new_active_players, new_turn_index) — skips dead players."""
    active = list(active_players)
    if not active:
        return active, 0
    next_idx = (turn_index + 1) % len(active)
    n = len(active)
    for _ in range(n):
        if not active:
            return active, 0
        color = active[next_idx % len(active)]
        if rules.is_alive(color, board, mode):
            return active, next_idx % len(active)
        active.remove(color)
        if not active:
            return active, 0
        next_idx = next_idx % len(active)
    return active, 0


def _search(board, active_players, turn_index, depth, alpha, beta, my_color, mode):
    deadline.check()
    if not active_players:
        return _evaluate(board, my_color, mode), None

    if len(active_players) == 1:
        winner = active_players[0]
        score = (10000 + depth) if winner == my_color else -(10000 + depth)
        return score, None

    if depth == 0:
        return _evaluate(board, my_color, mode), None

    current = active_players[turn_index % len(active_players)]
    moves = expanded_moves(current, board, mode)

    if not moves:
        new_active = [c for c in active_players if c != current]
        if not new_active:
            return _evaluate(board, my_color, mode), None
        new_idx = turn_index % len(new_active)
        return _search(board, new_active, new_idx, depth, alpha, beta, my_color, mode)

    moves.sort(key=lambda m: m[2], reverse=True)
    maximizing = (current == my_color)
    best_val = -math.inf if maximizing else math.inf
    best = None

    for move, cd, _n in moves:
        tok = make_move(board, move, mode, cd)
        new_active, new_idx = _advance_turn(board, list(active_players), turn_index, mode)
        val, _ = _search(board, new_active, new_idx, depth - 1, alpha, beta, my_color, mode)
        unmake_move(board, tok)
        if maximizing:
            if val > best_val:
                best_val, best = val, (move, cd)
            alpha = max(alpha, val)
        else:
            if val < best_val:
                best_val, best = val, (move, cd)
            beta = min(beta, val)
        if beta <= alpha:
            break

    return best_val, best


def best_move(board, active_players, turn_index, mode, depth=None, history=None):
    """Return best (move, capture_direction) for the current player, or None.

    Like the 2-player engine, demotes moves that recreate a position already
    seen this game (`history`) and randomises among moves within `_TIE_EPS` of
    the best — so the bot neither shuffles in place nor replays one fixed line.
    """
    if depth is None:
        depth = mode.ai_depth
    my_color = active_players[turn_index % len(active_players)]
    moves = expanded_moves(my_color, board, mode)
    if not moves:
        return None

    seen = {}
    if history:
        for h in history:
            seen[h] = seen.get(h, 0) + 1

    moves.sort(key=lambda m: m[2], reverse=True)
    scored = []
    best_val = -math.inf
    for move, cd, _n in moves:
        tok = make_move(board, move, mode, cd)
        repeats = seen.get(board._hash, 0)
        new_active, new_idx = _advance_turn(board, list(active_players), turn_index, mode)
        val, _ = _search(board, new_active, new_idx, depth - 1,
                         -math.inf, math.inf, my_color, mode)
        unmake_move(board, tok)
        if repeats:
            val -= _REPEAT_PENALTY * repeats
        scored.append((val, move, cd))
        if val > best_val:
            best_val = val

    ties = [(move, cd) for val, move, cd in scored if val >= best_val - _TIE_EPS]
    return random.choice(ties)
