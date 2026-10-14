"""Headless game-playing harness for empirical evaluation.

No pygame / no UI — drives the same `core` rules engine and `ai` engines the
game uses, so measurements reflect the shipped bots. Used by `run_eval.py` to
produce the numbers in the paper's Evaluation section.

Three things it provides:
  * `play_2p`      — one 2-player game between two minimax bots (possibly at
                     different search depths), returning the result + per-move
                     think times + repetition count.
  * `play_np`      — one 3/4-player game between paranoid bots.
  * `random_states`— a generator of positions reached by uniform-random legal
                     play, for branching-factor sampling.
"""

import random
import time

from core import rules
from core.state import GameState
from ai import minimax, paranoid

# Cờ Trận has no move limit and no draw rule (the folk game, and the software,
# play on until a side wins). Experiments therefore play every game to its
# natural end; SAFETY_CAP only guards against a pathological endless game and
# is reported as 'unfinished' -- never as a draw. In the paper's runs no game
# reached it.
SAFETY_CAP = 100_000


def _other_2p(mode, color):
    return next(c for c in mode.players if c != color)


def play_2p(mode, depth_by_color, seed, max_plies=SAFETY_CAP, time_moves=False):
    """Play one 2-player game; return a result dict.

    `depth_by_color` maps each colour to its search depth. The game ends when
    the side to move has no legal move (it loses). If `max_plies` is reached
    first, the game is reported as unfinished (`winner` None, reason
    'ply_cap') -- the rules have no draws, so this is not a draw.
    """
    random.seed(seed)
    state = GameState.new(mode)
    move_times = []
    plies = 0
    while plies < max_plies:
        cur = state.current_player
        if not rules.is_alive(cur, state.board, mode):
            return {'winner': _other_2p(mode, cur), 'plies': plies,
                    'move_times': move_times, 'reason': 'no_move'}
        d = depth_by_color[cur]
        t0 = time.perf_counter()
        res = minimax.best_move(state.board, cur, mode, depth=d,
                                history=state.position_history)
        if time_moves:
            move_times.append(time.perf_counter() - t0)
        if res is None:
            return {'winner': _other_2p(mode, cur), 'plies': plies,
                    'move_times': move_times, 'reason': 'no_move'}
        move, cd = res
        rules.apply_move(state.board, move, mode, cd)
        state.advance_turn()
        plies += 1
    return {'winner': None, 'plies': plies, 'move_times': move_times,
            'reason': 'ply_cap'}


def repetition_count(mode, depth_by_color, seed, max_plies, use_history):
    """Play one 2-player game and count how many positions repeat.

    When `use_history` is False the anti-repetition signal is disabled by
    feeding the bot an empty history each move, isolating the fix's effect.
    Returns (n_repeated_positions, plies).
    """
    random.seed(seed)
    state = GameState.new(mode)
    seen = {}
    repeats = 0
    plies = 0
    while plies < max_plies:
        cur = state.current_player
        if not rules.is_alive(cur, state.board, mode):
            break
        d = depth_by_color[cur]
        hist = state.position_history if use_history else None
        res = minimax.best_move(state.board, cur, mode, depth=d, history=hist)
        if res is None:
            break
        move, cd = res
        rules.apply_move(state.board, move, mode, cd)
        state.advance_turn()
        h = state.board._compute_hash()
        if h in seen:
            repeats += 1
        seen[h] = seen.get(h, 0) + 1
        plies += 1
    return repeats, plies


def play_np(mode, depth, seed, max_plies=SAFETY_CAP, time_moves=False):
    """Play one 3/4-player paranoid game; return a result dict.

    Ends when one player remains (winner). If `max_plies` is reached first the
    game is reported as unfinished. A player with no legal move is eliminated
    (matches `eliminate_on_no_moves`).
    """
    random.seed(seed)
    state = GameState.new(mode)
    move_times = []
    plies = 0
    while plies < max_plies:
        if len(state.active_players) <= 1:
            winner = state.active_players[0] if state.active_players else None
            return {'winner': winner, 'plies': plies, 'move_times': move_times,
                    'reason': 'last_standing'}
        cur = state.current_player
        t0 = time.perf_counter()
        res = paranoid.best_move(state.board, list(state.active_players),
                                 state.turn_index, mode, depth=depth,
                                 history=state.position_history)
        if time_moves:
            move_times.append(time.perf_counter() - t0)
        if res is None:
            # Current player is blockaded -> eliminate it.
            state.active_players.remove(cur)
            if state.active_players:
                state.turn_index %= len(state.active_players)
            continue
        move, cd = res
        rules.apply_move(state.board, move, mode, cd)
        state.advance_turn()
        plies += 1
    return {'winner': None, 'plies': plies, 'move_times': move_times,
            'reason': 'ply_cap'}


def random_states(mode, n_games, max_plies, seed, lengths=None):
    """Yield (phase_fraction, n_moves, n_actions) for states under random play.

    `n_moves`   = number of legal (from, to) moves = branching of the *move*
                  layer, comparable to checkers (~8) / reversi (~10).
    `n_actions` = number of full actions (move + chosen capture ray) the search
                  branches over = `len(expanded_moves)`, comparable to the
                  analytic bound in the paper.
    `phase_fraction` = ply / game_length in [0,1), for early/mid/late binning.
                  Only meaningful when games run to completion, so pass a
                  `max_plies` no game reaches (e.g. SAFETY_CAP).
    `lengths`   = optional list; receives (plies, finished) for every game.
    """
    rng = random.Random(seed)
    for g in range(n_games):
        state = GameState.new(mode)
        trace = []  # (ply, color)
        records = []
        ply = 0
        while ply < max_plies:
            if len(state.active_players) <= 1:
                break
            cur = state.current_player
            moves = rules.all_moves(cur, state.board, mode)
            if not moves:
                if mode.eliminate_on_no_moves:
                    state.active_players.remove(cur)
                    if state.active_players:
                        state.turn_index %= len(state.active_players)
                    continue
                else:
                    break  # 2-player: side to move stuck -> game over
            actions = rules.expanded_moves(cur, state.board, mode)
            records.append((ply, len(moves), len(actions)))
            mv = rng.choice(moves)
            rules.apply_move(state.board, mv, mode)
            state.advance_turn()
            ply += 1
        if lengths is not None:
            lengths.append((ply, ply < max_plies))
        glen = max(ply, 1)
        for p, nm, na in records:
            yield (p / glen, nm, na)
