"""Paranoid minimax for 3/4-player modes — current player maximises, all
others minimise together. Operates on `core.board.Board` (O(1) piece_at)."""

import math

from core import rules


def _evaluate(board, my_color, mode):
    my_count = 0
    enemy_count = 0
    for p in board.pieces:
        if p.color == my_color:
            my_count += 1
        else:
            enemy_count += 1
    my_moves = len(rules.all_moves(my_color, board, mode))
    return (my_count - enemy_count) * 10 + my_moves


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
    if not active_players:
        return _evaluate(board, my_color, mode), None

    if len(active_players) == 1:
        winner = active_players[0]
        score = (10000 + depth) if winner == my_color else -(10000 + depth)
        return score, None

    current = active_players[turn_index % len(active_players)]
    moves = rules.all_moves(current, board, mode)

    if depth == 0:
        return _evaluate(board, my_color, mode), None

    if not moves:
        new_active = [c for c in active_players if c != current]
        if not new_active:
            return _evaluate(board, my_color, mode), None
        new_idx = turn_index % len(new_active)
        return _search(board, new_active, new_idx, depth, alpha, beta, my_color, mode)

    maximizing = (current == my_color)
    best_val  = -math.inf if maximizing else math.inf
    best_move = None

    for move in moves:
        child = board.clone()
        rules.apply_move(child, move, mode)
        new_active, new_idx = _advance_turn(child, list(active_players), turn_index, mode)
        val, _ = _search(child, new_active, new_idx, depth - 1, alpha, beta, my_color, mode)
        if maximizing:
            if val > best_val:
                best_val, best_move = val, move
            alpha = max(alpha, val)
        else:
            if val < best_val:
                best_val, best_move = val, move
            beta = min(beta, val)
        if beta <= alpha:
            break

    return best_val, best_move


def best_move(board, active_players, turn_index, mode, depth=None):
    """Return best (fx, fy, tx, ty) move for the current player, or None."""
    if depth is None:
        depth = mode.ai_depth
    my_color = active_players[turn_index % len(active_players)]
    moves = rules.all_moves(my_color, board, mode)
    if not moves:
        return None
    _, move = _search(board, list(active_players), turn_index,
                      depth, -math.inf, math.inf, my_color, mode)
    return move if move is not None else moves[0]
