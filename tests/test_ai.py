"""Bot tests — search results, difficulty levels and the background worker.

Run with: uv run python -m unittest tests.test_ai
"""

import dataclasses
import os
import random
import tempfile
import time
import unittest
from unittest import mock

from ai import brs, minimax, paranoid, policy
from ai.policy import compute_move
from ai.worker import BotWorker
from core import rules
from core.board import Board
from core.modes import (
    ALL_MODES, DIFFICULTIES, DIFFICULTY_DEPTH, MODE_BOT_2, MODE_PLAY_3,
    MODE_PLAY_4, with_difficulty,
)
from core.piece import Piece
from core.state import GameState


def _wait(worker, timeout=60):
    end = time.monotonic() + timeout
    while not worker.done():
        if time.monotonic() > end:
            raise AssertionError('bot search did not finish in time')
        time.sleep(0.01)


class TestMinimax(unittest.TestCase):
    def setUp(self):
        random.seed(1)

    def test_takes_the_capturing_move(self):
        # Green (0,2) can jump its own piece (1,2) to (2,2) and sandwich the
        # yellow piece at (3,2) against green (4,2). The only other move,
        # (4,2) over (3,2) to (2,2), captures nothing.
        board = Board([Piece(0, 2, 'green'), Piece(1, 2, 'green'),
                       Piece(3, 2, 'yellow'), Piece(4, 2, 'green')])
        for depth in (1, 2):
            move, _direction = minimax.best_move(board.clone(), 'green',
                                                 MODE_BOT_2, depth=depth)
            self.assertEqual(move, (0, 2, 2, 2), f'depth {depth}')

    def test_no_legal_move_returns_none(self):
        board = Board([Piece(2, 2, 'green'), Piece(0, 0, 'yellow')])
        self.assertIsNone(minimax.best_move(board, 'green', MODE_BOT_2, depth=2))

    def test_easy_bots_play_only_legal_moves(self):
        mode = with_difficulty(MODE_BOT_2, 'easy')
        state = GameState.new(mode)
        for _ in range(20):
            player = state.current_player
            if not rules.is_alive(player, state.board, mode):
                break
            move, direction = compute_move(state)
            self.assertIn(move, rules.all_moves(player, state.board, mode))
            rules.make_move(state.board, move, mode, direction)
            state.advance_turn()
            self.assertEqual(len(state.pieces), 28)


class TestParanoid(unittest.TestCase):
    def setUp(self):
        random.seed(2)

    def test_opening_move_is_legal_3p_and_4p(self):
        for mode in (MODE_PLAY_3, MODE_PLAY_4):
            state = GameState.new(mode)
            move, _direction = paranoid.best_move(
                state.board.clone(), list(state.active_players),
                state.turn_index, mode, depth=1)
            self.assertIn(move, rules.all_moves(state.current_player,
                                                state.board, mode), mode.name)


def _positions(key, count, seed):
    """Positions of random games in mode `key`, some way into the game."""
    rng = random.Random(seed)
    out = []
    while len(out) < count:
        state = GameState.new(ALL_MODES[key])
        for _ in range(rng.randrange(40)):
            if state.start_turn()[0]:
                break
            move, direction, _n = rng.choice(
                rules.expanded_moves(state.current_player, state.board, state.mode))
            rules.make_move(state.board, move, state.mode, direction)
            state.advance_turn()
        if not state.start_turn()[0]:
            out.append(state)
    return out


def _brs_value(board, depth, maximizing, my_color, opponents, mode):
    """Best-Reply Search written plainly: no pruning, no table, no ordering."""
    if depth == 0:
        return paranoid._evaluate(board, my_color, mode)
    if maximizing:
        moves = rules.expanded_moves(my_color, board, mode)
        if not moves:
            return -(brs._WIN + depth)
    else:
        moves = []
        still_in = []
        for color in opponents:
            theirs = rules.expanded_moves(color, board, mode)
            if theirs:
                still_in.append(color)
                moves += theirs
        if not still_in:
            return brs._WIN + depth
        opponents = tuple(still_in)
    values = []
    for move, cd, _n in moves:
        token = rules.make_move(board, move, mode, cd)
        values.append(_brs_value(board, depth - 1, not maximizing, my_color, opponents, mode))
        rules.unmake_move(board, token)
    return max(values) if maximizing else min(values)


def _ties_of(search):
    """The equally-best moves a search hands to random.choice."""
    seen = []
    with mock.patch.object(random, 'choice', side_effect=lambda ties: seen.append(ties) or ties[0]):
        search()
    return seen[0]


class TestBestReplySearch(unittest.TestCase):
    def test_finds_the_same_best_moves_as_a_plain_search(self):
        # Pruning, the table, the move hints and the narrow root window only
        # make the search faster: the best moves must be those of a plain one.
        for key in ('bot_3', 'bot_4'):
            for state in _positions(key, 4, seed=3):
                mode = state.mode
                me = state.current_player
                opponents = tuple(c for c in state.active_players if c != me)
                board = state.board.clone()
                scored = []
                for move, cd, _n in rules.expanded_moves(me, board, mode):
                    token = rules.make_move(board, move, mode, cd)
                    scored.append((_brs_value(board, 2, False, me, opponents, mode), (move, cd)))
                    rules.unmake_move(board, token)
                best = max(v for v, _m in scored)
                expected = {m for v, m in scored if v >= best - brs._TIE_EPS}
                found = _ties_of(lambda: brs.best_move(
                    state.board.clone(), list(state.active_players), state.turn_index,
                    mode, depth=3))
                self.assertEqual(set(found), expected, key)

    def test_hints_from_a_shallower_search_change_nothing(self):
        for key in ('bot_3', 'bot_4'):
            for state in _positions(key, 3, seed=4):
                args = (list(state.active_players), state.turn_index, state.mode)
                hints = {}
                for depth in (1, 2, 3):
                    with_hints = _ties_of(lambda: brs.best_move(
                        state.board.clone(), *args, depth=depth, hints=hints))
                without = _ties_of(lambda: brs.best_move(state.board.clone(), *args, depth=3))
                self.assertEqual(with_hints, without, key)   # the same moves, in the same order

    def test_sees_the_reply_of_a_side_that_moves_later(self):
        # Four players move Blue, Green, Purple, Yellow. Purple, the bot, can
        # take the yellow piece at (3, 3) by jumping from (0, 3) to (2, 3).
        # That empties (0, 3), and Green, three turns later, jumps there over
        # Blue's (0, 4) and flips all four purple pieces on the row. Paranoid
        # search at three plies only sees Yellow's and Blue's answers and takes
        # the piece; Best-Reply Search sees Green's answer at two plies.
        mode = MODE_PLAY_4
        board = Board([Piece(0, 3, 'purple'), Piece(1, 3, 'purple'), Piece(4, 3, 'purple'),
                       Piece(3, 3, 'yellow'), Piece(2, 6, 'yellow'), Piece(3, 6, 'yellow'),
                       Piece(0, 4, 'blue'), Piece(2, 0, 'blue'), Piece(3, 0, 'blue'),
                       Piece(0, 5, 'green'), Piece(5, 3, 'green')])
        active = ['blue', 'green', 'purple', 'yellow']
        trap = (0, 3, 2, 3)
        move, _direction = paranoid.best_move(board.clone(), active, 2, mode, depth=3)
        self.assertEqual(move, trap)
        move, _direction = brs.best_move(board.clone(), active, 2, mode, depth=2)
        self.assertNotEqual(move, trap)


class TestTimeBudget(unittest.TestCase):
    def test_with_time_it_plays_the_full_depth_move(self):
        # Ties are broken at random; take the first so both searches can be compared.
        state = GameState.new(with_difficulty(MODE_BOT_2, 'medium'))
        with mock.patch.object(minimax.random, 'choice', side_effect=lambda ties: ties[0]):
            full = policy.compute_move(state)
            timed = policy.compute_move_in_time(state, budget=60)
        self.assertEqual(timed, full)   # the same move as one search at full depth

    def test_without_time_it_plays_the_one_ply_move(self):
        for key in ('bot_2', 'bot_3', 'bot_4'):
            state = GameState.new(with_difficulty(ALL_MODES[key], 'hard'))
            one_ply = dataclasses.replace(state, mode=dataclasses.replace(state.mode, ai_depth=1))
            with mock.patch.object(random, 'choice', side_effect=lambda ties: ties[0]):
                started = time.perf_counter()
                timed = policy.compute_move_in_time(state, budget=0)
                elapsed = time.perf_counter() - started
                expected = compute_move(one_ply)
            self.assertLess(elapsed, 1.0, key)   # one shallow search
            self.assertEqual(timed, expected, key)


class TestDifficulty(unittest.TestCase):
    def test_every_bot_mode_has_three_levels(self):
        for key in ('bot_2', 'bot_3', 'bot_4'):
            mode = ALL_MODES[key]
            depths = [with_difficulty(mode, level).ai_depth for level in DIFFICULTIES]
            self.assertEqual(depths, sorted(depths), key)
            self.assertLess(depths[0], depths[-1], key)

    def test_hard_is_the_default_depth(self):
        for key in ('bot_2', 'bot_3', 'bot_4'):
            mode = ALL_MODES[key]
            self.assertEqual(DIFFICULTY_DEPTH[mode.name]['hard'], mode.ai_depth)

    def test_difficulty_changes_only_the_depth(self):
        easy = with_difficulty(MODE_PLAY_4, 'easy')
        self.assertEqual(easy.ai_depth, 4)
        self.assertEqual(easy.players, MODE_PLAY_4.players)
        self.assertEqual(MODE_PLAY_4.ai_depth, 6)   # the original is unchanged

    def test_the_same_depths_in_every_mode(self):
        for key in ('bot_2', 'bot_3', 'bot_4'):
            mode = ALL_MODES[key]
            depths = {level: with_difficulty(mode, level).ai_depth for level in DIFFICULTIES}
            self.assertEqual(depths, {'easy': 4, 'medium': 5, 'hard': 6}, key)


# The worker runs searches in another process, so fake searches must be
# module-level functions.

def _count_pieces(snapshot):
    return len(snapshot.pieces)


def _slow(_snapshot):
    time.sleep(30)
    return 'stale'


def _fresh(_snapshot):
    return 'fresh'


def _broken(_snapshot):
    raise ValueError('bug in search')


def _die_once(_snapshot):
    flag = os.environ['TF_TEST_FLAG']
    if not os.path.exists(flag):
        open(flag, 'w').close()
        os._exit(1)            # the worker process dies in the middle of a search
    return 'recovered'


class TestBotWorker(unittest.TestCase):
    def setUp(self):
        self.worker = BotWorker()

    def tearDown(self):
        self.worker.close()

    def test_returns_a_legal_move_from_the_worker_process(self):
        state = GameState.new(with_difficulty(MODE_BOT_2, 'easy'))
        self.worker.start(state)
        self.assertTrue(self.worker.busy)
        _wait(self.worker)
        move, _direction = self.worker.result()
        self.assertIn(move, rules.all_moves('green', state.board, state.mode))
        self.assertFalse(self.worker.busy)

    def test_search_uses_a_snapshot(self):
        state = GameState.new(MODE_BOT_2)
        self.worker._search = _count_pieces
        self.worker.start(state)
        state.board.pieces.clear()          # the game changes after start()
        _wait(self.worker)
        self.assertEqual(self.worker.result(), 28)

    def test_cancel_stops_a_running_search(self):
        self.worker._search = _slow
        self.worker.start(GameState.new(MODE_BOT_2))
        self.worker.cancel()
        self.assertFalse(self.worker.busy)
        self.assertFalse(self.worker.done())

        # The next search does not wait behind the cancelled 30-second one.
        self.worker._search = _fresh
        began = time.monotonic()
        self.worker.start(GameState.new(MODE_BOT_2))
        _wait(self.worker, timeout=20)
        self.assertEqual(self.worker.result(), 'fresh')
        self.assertLess(time.monotonic() - began, 20)

    def test_errors_reach_the_game_loop(self):
        self.worker._search = _broken
        self.worker.start(GameState.new(MODE_BOT_2))
        _wait(self.worker)
        with self.assertRaises(ValueError):
            self.worker.result()
        self.assertFalse(self.worker.busy)

    def test_a_dead_worker_process_is_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            os.environ['TF_TEST_FLAG'] = os.path.join(folder, 'died')
            worker = BotWorker(_die_once, stall_seconds=2)
            try:
                worker.start(GameState.new(MODE_BOT_2))
                _wait(worker, timeout=30)
                self.assertEqual(worker.result(), 'recovered')
            finally:
                worker.close()
                del os.environ['TF_TEST_FLAG']

    def test_hashes_match_across_processes(self):
        # The bots' anti-repetition compares hashes made by the game with
        # hashes made in the worker process.
        state = GameState.new(MODE_PLAY_4)
        self.worker._search = _board_hash
        self.worker.start(state)
        _wait(self.worker)
        self.assertEqual(self.worker.result(), state.board._compute_hash())


def _board_hash(snapshot):
    return snapshot.board.clone()._hash


if __name__ == '__main__':
    unittest.main()
