"""Pure-Python rule tests — no pygame, headless.

Run with: .venv/bin/python -m unittest tests.test_rules
"""

import unittest

from core import rules
from core.board import Board
from core.modes import (
    MODE_PLAY_2, MODE_BOT_2,
    MODE_PLAY_3, MODE_PLAY_3_HUMAN,
    MODE_PLAY_4, MODE_PLAY_4_HUMAN,
)
from core.piece import Piece
from core.state import GameState


def _make(mode):
    return GameState.new(mode)


class TestOpeningPositions(unittest.TestCase):
    def test_2p_opening(self):
        s = _make(MODE_PLAY_2)
        self.assertEqual(len(s.pieces), 28)
        self.assertEqual(sum(1 for p in s.pieces if p.color == 'yellow'), 14)
        self.assertEqual(sum(1 for p in s.pieces if p.color == 'green'), 14)
        self.assertEqual(s.current_player, 'green')

    def test_3p_opening(self):
        s = _make(MODE_PLAY_3)
        # 3 colors × 13/14 pieces — should sum to 40
        self.assertEqual(len(s.pieces), 40)
        self.assertEqual(s.current_player, 'purple')

    def test_4p_opening(self):
        s = _make(MODE_PLAY_4)
        self.assertEqual(len(s.pieces), 52)
        self.assertEqual(s.current_player, 'blue')


class TestLegalMoves(unittest.TestCase):
    def test_2p_corner_piece_can_jump_own_to_open_row(self):
        s = _make(MODE_PLAY_2)
        back = next(p for p in s.pieces if p.x == 0 and p.y == 0 and p.color == 'yellow')
        moves = rules.legal_moves(back, s.board, MODE_PLAY_2)
        self.assertIn((0, 2), moves)

    def test_2p_opening_move_count(self):
        s = _make(MODE_PLAY_2)
        green_moves = rules.all_moves('green', s.board, MODE_PLAY_2)
        yellow_moves = rules.all_moves('yellow', s.board, MODE_PLAY_2)
        self.assertEqual(len(green_moves), len(yellow_moves))

    def test_excluded_cells_not_landable_3p(self):
        s = _make(MODE_PLAY_3)
        all_landings = {
            (tx, ty)
            for c in MODE_PLAY_3.players
            for (_fx, _fy, tx, ty) in rules.all_moves(c, s.board, MODE_PLAY_3)
        }
        for ex in MODE_PLAY_3.excluded_cells:
            self.assertNotIn(ex, all_landings)


class TestCapture(unittest.TestCase):
    def test_sandwich_flips_to_capturer_color(self):
        mode = MODE_PLAY_2
        pieces = [
            Piece(0, 0, 'green'),
            Piece(1, 0, 'yellow'),
            Piece(2, 0, 'green'),
        ]
        board = Board(pieces)
        moved = pieces[2]
        caps = rules.find_captures(moved, board, mode)
        self.assertIn((-1, 0), caps)
        self.assertEqual(len(caps[(-1, 0)]), 1)
        self.assertEqual(caps[(-1, 0)][0].color, 'yellow')


class TestEliminationSemantics(unittest.TestCase):
    def test_2p_does_not_eliminate(self):
        self.assertFalse(MODE_PLAY_2.eliminate_on_no_moves)
        self.assertFalse(MODE_BOT_2.eliminate_on_no_moves)

    def test_3p_4p_eliminate(self):
        self.assertTrue(MODE_PLAY_3.eliminate_on_no_moves)
        self.assertTrue(MODE_PLAY_4.eliminate_on_no_moves)


class TestApplyMoveAndUndo(unittest.TestCase):
    def test_apply_move_moves_piece(self):
        s = _make(MODE_PLAY_2)
        moves = rules.all_moves('green', s.board, MODE_PLAY_2)
        first = moves[0]
        fx, fy, tx, ty = first
        rules.apply_move(s.board, first, MODE_PLAY_2)
        self.assertIsNone(s.board.piece_at((fx, fy)))
        self.assertIsNotNone(s.board.piece_at((tx, ty)))


class TestBoardIndex(unittest.TestCase):
    def test_piece_at_after_move(self):
        b = Board([Piece(0, 0, 'green'), Piece(2, 2, 'yellow')])
        g = b.piece_at((0, 0))
        b.move_piece(g, (1, 1))
        self.assertIsNone(b.piece_at((0, 0)))
        self.assertIs(b.piece_at((1, 1)), g)
        self.assertIs(b.piece_at((2, 2)).color, 'yellow')

    def test_clone_independence(self):
        b = Board([Piece(0, 0, 'green')])
        c = b.clone()
        b.move_piece(b.piece_at((0, 0)), (3, 3))
        # cloned board still has piece at (0,0)
        self.assertIsNotNone(c.piece_at((0, 0)))
        self.assertIsNone(c.piece_at((3, 3)))


class TestAdvanceTurn(unittest.TestCase):
    def test_2p_rotation(self):
        s = _make(MODE_PLAY_2)
        self.assertEqual(s.current_player, 'green')
        s.advance_turn()
        self.assertEqual(s.current_player, 'yellow')
        s.advance_turn()
        self.assertEqual(s.current_player, 'green')


class TestHumanModesHaveNoBots(unittest.TestCase):
    def test_play_2_no_bots(self):
        self.assertEqual(MODE_PLAY_2.bot_colors, frozenset())
        self.assertEqual(MODE_PLAY_2.human_colors, frozenset({'green', 'yellow'}))

    def test_play_3_human_no_bots(self):
        self.assertEqual(MODE_PLAY_3_HUMAN.bot_colors, frozenset())
        self.assertEqual(MODE_PLAY_3_HUMAN.human_colors,
                         frozenset({'green', 'yellow', 'purple'}))

    def test_play_4_human_no_bots(self):
        self.assertEqual(MODE_PLAY_4_HUMAN.bot_colors, frozenset())
        self.assertEqual(MODE_PLAY_4_HUMAN.human_colors,
                         frozenset({'green', 'yellow', 'purple', 'blue'}))

    def test_bot_modes_have_bots(self):
        self.assertEqual(MODE_BOT_2.bot_colors, frozenset({'yellow'}))
        self.assertEqual(MODE_PLAY_3.bot_colors, frozenset({'purple', 'yellow'}))
        self.assertEqual(MODE_PLAY_4.bot_colors,
                         frozenset({'blue', 'purple', 'yellow'}))


class TestMissingCells(unittest.TestCase):
    def test_play_3_missing_bottom_corners(self):
        # bottom-left and bottom-right lattice corners are cut for 3p
        self.assertEqual(set(MODE_PLAY_3.missing_cells), {(0, 4), (5, 4)})
        self.assertEqual(set(MODE_PLAY_3_HUMAN.missing_cells), {(0, 4), (5, 4)})

    def test_play_4_missing_all_corners(self):
        # all 4 lattice corners are cut for 4p
        self.assertEqual(set(MODE_PLAY_4.missing_cells),
                         {(0, 0), (5, 0), (0, 5), (5, 5)})
        self.assertEqual(set(MODE_PLAY_4_HUMAN.missing_cells),
                         {(0, 0), (5, 0), (0, 5), (5, 5)})

    def test_play_2_no_missing_cells(self):
        self.assertEqual(MODE_PLAY_2.missing_cells, ())


if __name__ == '__main__':
    unittest.main()
