"""Best-Reply Search for 3/4-player modes (Schadd & Winands, 2011).

The bot's own moves alternate with a single reply: of all the moves every
opponent could make, the one worst for the bot, while the other opponents
pass. So 6 plies see three moves of the bot and three answers, as in a
2-player game, where Paranoid search (ai/paranoid.py) would spend most plies
on the opponents' turns, and with four players, depending on the turn order,
not even reach the next human move.

Like the 2-player engine it uses make/unmake, a transposition table on the
board's Zobrist hash, move ordering for alpha-beta cutoffs, and randomises
among equally-best root moves (ai/search.py). The evaluation is Paranoid's:
the bot's pieces against all the others' together, and its own mobility.
"""

import math

from ai import deadline
from ai.paranoid import _evaluate
from ai.search import EXACT, LOWER, UPPER, WIN, Memory, choose, remember_best
from core.rules import make_expanded_move, unmake_move, expanded_moves


def _search(board, depth, alpha, beta, maximizing, my_color, opponents, mode, memory):
    """Value of the position for `my_color`; `opponents` are the sides still in.

    At the bot's plies it picks its best move; at the others' plies the
    opponents' moves are pooled and the worst one for the bot is taken. An
    opponent with no move just then adds none, but stays in: in the game a
    side is only out when it cannot move on its own turn, and a later move
    can free it.
    """
    deadline.check()
    if depth == 0:
        return _evaluate(board, my_color, mode), None

    alpha0, beta0 = alpha, beta
    place = (board._hash, maximizing)
    key = (board._hash, depth, maximizing)
    table = memory.table
    hit = table.get(key)
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

    if maximizing:
        moves = expanded_moves(my_color, board, mode)
        if not moves:
            return -(WIN + depth), None   # the bot cannot move: it is out
    else:
        moves = []
        for color in opponents:
            moves.extend(expanded_moves(color, board, mode))
        if not moves:
            # No opponent can move: each is out on its turn, the bot wins.
            return WIN + depth, None

    # Ordering: the best move known here first, then the move that last cut
    # off a search at this ply elsewhere (a "killer"), then biggest captures.
    killer_key = (depth, maximizing)
    killer = memory.killers.get(killer_key)
    moves.sort(key=lambda m: ((m[0], m[1]) == tt_best, (m[0], m[1]) == killer, m[2]),
               reverse=True)

    best = None
    if maximizing:
        best_val = -math.inf
        for move, cd, _n in moves:
            tok = make_expanded_move(board, move, mode, cd)
            val, _ = _search(board, depth - 1, alpha, beta, False,
                             my_color, opponents, mode, memory)
            unmake_move(board, tok)
            if val > best_val:
                best_val, best = val, (move, cd)
            if val > alpha:
                alpha = val
            if beta <= alpha:
                memory.killers[killer_key] = (move, cd)
                break
    else:
        best_val = math.inf
        for move, cd, _n in moves:
            tok = make_expanded_move(board, move, mode, cd)
            val, _ = _search(board, depth - 1, alpha, beta, True,
                             my_color, opponents, mode, memory)
            unmake_move(board, tok)
            if val < best_val:
                best_val, best = val, (move, cd)
            if val < beta:
                beta = val
            if beta <= alpha:
                memory.killers[killer_key] = (move, cd)
                break

    if best_val <= alpha0:
        flag = UPPER
    elif best_val >= beta0:
        flag = LOWER
    else:
        flag = EXACT
    table[key] = (best_val, flag, best)
    remember_best(memory, place, best, best_val, alpha0, beta0, maximizing)
    return best_val, best


def best_move(board, active_players, turn_index, mode, depth=None, history=None,
              memory=None):
    """Return best (move, capture_direction) for the current player, or None.

    Like the 2-player engine, demotes moves that recreate a position already
    seen this game (`history`) and picks at random among the equally best
    (ai.search.choose). `memory` (an ai.search.Memory) carries what a
    shallower search of the same position found; it changes the order and
    amount of searching, not the result.
    """
    if depth is None:
        depth = mode.ai_depth
    my_color = active_players[turn_index % len(active_players)]
    opponents = tuple(c for c in active_players if c != my_color)
    moves = expanded_moves(my_color, board, mode)
    if not moves:
        return None
    if memory is None:
        memory = Memory()
    return choose(board, moves, mode, history, memory, lambda floor: _search(
        board, depth - 1, floor, math.inf, False, my_color, opponents, mode, memory)[0])
