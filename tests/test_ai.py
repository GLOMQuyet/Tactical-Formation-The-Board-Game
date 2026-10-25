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

from ai import minimax, paranoid, policy
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
        self.assertEqual(easy.ai_depth, 2)
        self.assertEqual(easy.players, MODE_PLAY_4.players)
        self.assertEqual(MODE_PLAY_4.ai_depth, 4)   # the original is unchanged


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
