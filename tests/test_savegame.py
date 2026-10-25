"""Autosave tests — save, load, resume with undo, and bad files.

Run with: uv run python -m unittest tests.test_savegame
"""

import json
import os
import random
import tempfile
import unittest

from core import rules, savegame
from core.board import Board
from core.history import MoveRecord, undo_record
from core.modes import (MODE_BOT_2, MODE_PLAY_3, MODE_PLAY_4_HUMAN, human_side, with_difficulty,
                        with_side)
from core.state import GameState


def _position(board):
    return sorted((p.x, p.y, p.color) for p in board.pieces)


def _play(state, n, rng):
    """Play `n` random moves the way the game screen does; return the records."""
    mode = state.mode
    records = []
    for _ in range(n):
        player = state.current_player
        if player is None or not rules.is_alive(player, state.board, mode):
            break
        fx, fy, tx, ty = rng.choice(rules.all_moves(player, state.board, mode))
        piece = state.board.piece_at((fx, fy))
        rec = MoveRecord(player, (fx, fy), (tx, ty))
        state.board.move_piece(piece, (tx, ty))
        captures = rules.find_captures(piece, state.board, mode)
        if captures:
            for p in captures[rng.choice(list(captures))]:
                rec.captured.append(((p.x, p.y), p.color))
                p.color = piece.color
        records.append(rec)
        state.advance_turn()
    return records


class TestSaveGame(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, 'saves', 'autosave.json')

    def tearDown(self):
        self.dir.cleanup()

    def test_round_trip_restores_the_game(self):
        for mode, seed in ((MODE_BOT_2, 1), (MODE_PLAY_3, 2), (MODE_PLAY_4_HUMAN, 3)):
            state = GameState.new(mode)
            moves = _play(state, 40, random.Random(seed))
            savegame.save(state, moves, path=self.path)
            saved = savegame.load(self.path)
            self.assertIsNotNone(saved, mode.name)
            self.assertEqual(saved.state.mode.name, mode.name)
            self.assertEqual(_position(saved.state.board), _position(state.board))
            self.assertEqual(saved.state.active_players, state.active_players)
            self.assertEqual(saved.state.current_player, state.current_player)
            self.assertEqual(saved.state.position_history, state.position_history)
            self.assertEqual(len(saved.moves), len(moves))

    def test_undo_works_after_resume(self):
        state = GameState.new(MODE_PLAY_3)
        moves = _play(state, 30, random.Random(4))
        savegame.save(state, moves, path=self.path)
        saved = savegame.load(self.path)
        while saved.moves:
            undo_record(saved.state.board, saved.moves.pop())
        self.assertEqual(_position(saved.state.board),
                         _position(Board.from_mode(MODE_PLAY_3)))

    def test_difficulty_is_kept(self):
        mode = with_difficulty(MODE_BOT_2, 'easy')
        state = GameState.new(mode)
        moves = _play(state, 4, random.Random(5))
        savegame.save(state, moves, 'easy', path=self.path)
        saved = savegame.load(self.path)
        self.assertEqual(saved.difficulty, 'easy')
        self.assertEqual(saved.state.mode.ai_depth, 4)

    def test_the_chosen_side_is_kept(self):
        mode = with_side(with_difficulty(MODE_PLAY_3, 'medium'), 'purple')
        state = GameState.new(mode)
        moves = _play(state, 5, random.Random(8))
        savegame.save(state, moves, 'medium', path=self.path)
        saved = savegame.load(self.path)
        self.assertEqual(human_side(saved.state.mode), 'purple')
        self.assertEqual(saved.state.mode.bot_colors, frozenset({'yellow', 'green'}))
        self.assertEqual(saved.state.mode.ai_depth, 5)

    def test_a_save_without_a_side_plays_green(self):
        state = GameState.new(with_difficulty(MODE_BOT_2, 'easy'))
        savegame.save(state, _play(state, 3, random.Random(9)), 'easy', path=self.path)
        with open(self.path, encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data.pop('side'), 'green')
        for side, expected in ((None, 'green'), ('blue', None)):   # blue is not a 2P side
            if side is not None:
                data['side'] = side
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            saved = savegame.load(self.path)
            self.assertEqual(saved and human_side(saved.state.mode), expected, side)

    def test_missing_or_broken_file_gives_none(self):
        self.assertIsNone(savegame.load(self.path))
        os.makedirs(os.path.dirname(self.path))
        for content in ('not json', '{"format": 99}', '{"format": 1, "mode": "nope"}'):
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.assertIsNone(savegame.load(self.path), content)

    def test_inconsistent_moves_resume_from_the_position(self):
        state = GameState.new(MODE_BOT_2)
        moves = _play(state, 6, random.Random(6))
        savegame.save(state, moves, path=self.path)
        with open(self.path, encoding='utf-8') as f:
            data = json.load(f)
        data['moves'] = data['moves'][:-1]          # one move lost
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        saved = savegame.load(self.path)
        self.assertEqual(_position(saved.state.board), _position(state.board))
        self.assertEqual(saved.moves, [])
        self.assertEqual(saved.state.position_history, [])

    def test_delete(self):
        state = GameState.new(MODE_BOT_2)
        savegame.save(state, _play(state, 2, random.Random(7)), path=self.path)
        self.assertTrue(os.path.exists(self.path))
        savegame.delete(self.path)
        self.assertFalse(os.path.exists(self.path))
        savegame.delete(self.path)   # deleting twice is fine

    def test_default_path_is_per_user(self):
        path = savegame.default_path()
        self.assertTrue(path.endswith('autosave.json'))
        self.assertTrue(os.path.isabs(path))


if __name__ == '__main__':
    unittest.main()
