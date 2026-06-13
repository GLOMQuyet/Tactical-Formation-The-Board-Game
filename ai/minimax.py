"""Alpha-beta minimax for 2-player mode.

Operates on `core.board.Board` — no pygame, safe to run in a worker thread.
Cloning a Board is O(N) for both the piece list and the position index, but
that one-time cost per branch beats the per-call linear scan that the old
`piece_at(pieces, pos)` did inside legal_moves/find_captures.
"""

import math

from core import rules


def _evaluate(board, my_color, enemy_color, mode):
    my_count = 0
    en_count = 0
    for p in board.pieces:
        if p.color == my_color:
            my_count += 1
        elif p.color == enemy_color:
            en_count += 1
    my_moves = len(rules.all_moves(my_color, board, mode))
    en_moves = len(rules.all_moves(enemy_color, board, mode))
    return (my_count - en_count) * 10 + (my_moves - en_moves)


def _terminal(board, my_color, enemy_color, mode):
    my_alive = rules.is_alive(my_color, board, mode)
    en_alive = rules.is_alive(enemy_color, board, mode)
    if not my_alive:
        return -10000
    if not en_alive:
        return +10000
    return None


def _search(board, depth, alpha, beta, maximizing, my_color, enemy_color, mode):
    terminal_score = _terminal(board, my_color, enemy_color, mode)
    if terminal_score is not None:
        return terminal_score, None
    if depth == 0:
        return _evaluate(board, my_color, enemy_color, mode), None

    color = my_color if maximizing else enemy_color
    moves = rules.all_moves(color, board, mode)
    if not moves:
        return _evaluate(board, my_color, enemy_color, mode), None

    best_move = None
    if maximizing:
        best_val = -math.inf
        for move in moves:
            child = board.clone()
            rules.apply_move(child, move, mode)
            val, _ = _search(child, depth - 1, alpha, beta, False,
                             my_color, enemy_color, mode)
            if val > best_val:
                best_val, best_move = val, move
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return best_val, best_move
    else:
        best_val = math.inf
        for move in moves:
            child = board.clone()
            rules.apply_move(child, move, mode)
            val, _ = _search(child, depth - 1, alpha, beta, True,
                             my_color, enemy_color, mode)
            if val < best_val:
                best_val, best_move = val, move
            beta = min(beta, val)
            if beta <= alpha:
                break
        return best_val, best_move


def best_move(board, my_color, mode, depth=None):
    """Return best (fx, fy, tx, ty) move for `my_color`, or None."""
    if depth is None:
        depth = mode.ai_depth
    enemy_color = next(c for c in mode.players if c != my_color)
    moves = rules.all_moves(my_color, board, mode)
    if not moves:
        return None
    _, move = _search(board, depth, -math.inf, math.inf, True,
                      my_color, enemy_color, mode)
    return move if move is not None else moves[0]
