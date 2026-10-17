"""Pure-Python rule tests — no pygame, headless.

Run with: uv run python -m unittest tests.test_rules
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


class TestMakeUnmake(unittest.TestCase):
    def test_round_trip_restores_board_and_hash(self):
        import random as _r
        rng = _r.Random(123)
        s = _make(MODE_PLAY_2)
        board = s.board
        before_state = sorted((p.x, p.y, p.color) for p in board.pieces)
        before_hash = board._hash

        color = 'green'
        tokens = []
        for _ in range(8):
            moves = rules.expanded_moves(color, board, MODE_PLAY_2)
            if not moves:
                break
            move, cd, _n = rng.choice(moves)
            tokens.append(rules.make_move(board, move, MODE_PLAY_2, cd))
            color = 'yellow' if color == 'green' else 'green'

        # hash actually changed mid-sequence (sanity: we did something)
        self.assertTrue(tokens)

        for tok in reversed(tokens):
            rules.unmake_move(board, tok)

        after_state = sorted((p.x, p.y, p.color) for p in board.pieces)
        self.assertEqual(before_state, after_state)
        self.assertEqual(before_hash, board._hash)
        # index stays consistent with piece positions
        self.assertEqual(len(board._index), len(board.pieces))
        for p in board.pieces:
            self.assertIs(board.piece_at((p.x, p.y)), p)

    def test_apply_move_returns_moved_and_flipped_list(self):
        # green at (4,0) jumps left over (3,0) onto (2,0); at (2,0) it sandwiches
        # yellow@(1,0) against green@(0,0) -> one flip.
        pieces = [
            Piece(0, 0, 'green'),   # anchor
            Piece(1, 0, 'yellow'),  # to be flipped
            Piece(3, 0, 'green'),   # jumped over
            Piece(4, 0, 'green'),   # mover
        ]
        board = Board(pieces)
        moved, flipped = rules.apply_move(board, (4, 0, 2, 0), MODE_PLAY_2)
        self.assertIs(moved, board.piece_at((2, 0)))
        self.assertEqual([f.color for f in flipped], ['green'])
        self.assertIsNone(board.piece_at((4, 0)))
        self.assertEqual(board.piece_at((1, 0)).color, 'green')


class TestExpandedMoves(unittest.TestCase):
    def test_multi_ray_landing_yields_one_entry_per_ray(self):
        # green mover at (4,2) jumps left over (3,2) onto (2,2); from (2,2) it
        # sandwiches yellow@(1,2)->green@(0,2)  AND  yellow@(2,1)->green@(2,0).
        pieces = [
            Piece(4, 2, 'green'),   # mover
            Piece(3, 2, 'yellow'),  # jumped over (not captured)
            Piece(1, 2, 'yellow'),  # flipped by left ray
            Piece(0, 2, 'green'),   # left anchor
            Piece(2, 1, 'yellow'),  # flipped by up ray
            Piece(2, 0, 'green'),   # up anchor
        ]
        board = Board(pieces)
        moves = rules.expanded_moves('green', board, MODE_PLAY_2)
        entries = [m for m in moves if m[0] == (4, 2, 2, 2)]
        self.assertEqual(len(entries), 2)
        self.assertEqual({cd for (_mv, cd, _n) in entries}, {(-1, 0), (0, -1)})
        # expanding must not corrupt the board (temp move is restored)
        self.assertIs(board.piece_at((4, 2)), pieces[0])
        self.assertIsNone(board.piece_at((2, 2)))


class TestBestMoveContract(unittest.TestCase):
    def test_minimax_returns_move_and_capture_direction(self):
        from ai import minimax
        s = _make(MODE_BOT_2)
        result = minimax.best_move(s.board, 'yellow', MODE_BOT_2, depth=2)
        self.assertIsNotNone(result)
        move, cd = result
        self.assertEqual(len(move), 4)
        legal = {(fx, fy, tx, ty) for (fx, fy, tx, ty) in
                 rules.all_moves('yellow', s.board, MODE_BOT_2)}
        self.assertIn(move, legal)


class TestPieceConservation(unittest.TestCase):
    """Capture changes a piece's side; it never adds or removes a piece."""

    def _random_game_keeps_counts(self, mode, seed, max_plies=400):
        import random
        rng = random.Random(seed)
        s = GameState.new(mode)
        total = len(s.pieces)
        kinds = sorted((p.x % 1, p.y % 1) for p in s.pieces)
        for _ in range(max_plies):
            if len(s.active_players) <= 1:
                break
            cur = s.current_player
            moves = rules.all_moves(cur, s.board, mode)
            if not moves:
                if mode.eliminate_on_no_moves:
                    s.active_players.remove(cur)
                    if s.active_players:
                        s.turn_index %= len(s.active_players)
                    continue
                break
            rules.apply_move(s.board, rng.choice(moves), mode)
            s.advance_turn()
            self.assertEqual(len(s.pieces), total)
            # every piece stays on its own layer (vertex or centre)
            self.assertEqual(sorted((p.x % 1, p.y % 1) for p in s.pieces), kinds)

    def test_conservation_2p(self):
        for seed in range(20):
            self._random_game_keeps_counts(MODE_PLAY_2, seed)

    def test_conservation_3p(self):
        for seed in range(10):
            self._random_game_keeps_counts(MODE_PLAY_3_HUMAN, seed)

    def test_conservation_4p(self):
        for seed in range(10):
            self._random_game_keeps_counts(MODE_PLAY_4_HUMAN, seed)


if __name__ == '__main__':
    unittest.main()
