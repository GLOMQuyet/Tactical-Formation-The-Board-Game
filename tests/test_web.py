"""The browser version (web/) plays by exactly the same rules as this game.

web/src/engine/ is a second implementation of the rules and the bots, in
JavaScript, so that the game runs in a web browser, also on phones. These tests play
random games with the Python engine and replay them in the JavaScript engine
with Node.js (tests/web_replay.mjs). At every turn both must agree on the
list of moves (with the capture lines each move offers), the position after
the move, whose turn it is, who is out and who won. At some turns the two
bots must also agree on which moves are best. Skipped if Node.js is missing.

Run with: uv run python -m unittest tests.test_web
"""

import json
import random
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from ai.policy import compute_move
from core import rules
from core.modes import ALL_MODES, with_difficulty
from core.state import GameState

ROOT = Path(__file__).resolve().parent.parent
NODE = shutil.which('node')

# The longest random game played here, in moves (the game itself has no limit).
MAX_PLIES = 1500


def _move(move, direction):
    fx, fy, tx, ty = move
    return [fx, fy, tx, ty, None if direction is None else list(direction)]


def _bot_ties(state, bot_mode, repeat):
    """The moves the Python bot finds equally best, as it hands them to random.choice.

    With `repeat`, the position after the first listed move counts as played
    that many times before, so the bot's penalty for repeating is tested too.
    """
    history = list(state.position_history)
    if repeat:
        move, direction, _n = rules.expanded_moves(
            state.current_player, state.board, state.mode)[0]
        probe = state.board.clone()
        rules.make_move(probe, move, state.mode, direction)
        history += [probe._compute_hash()] * repeat
    snapshot = GameState(board=state.board.clone(), active_players=list(state.active_players),
                         turn_index=state.turn_index, mode=bot_mode,
                         position_history=history)
    seen = []

    def choose(ties):
        seen.append([_move(m, d) for m, d in ties])
        return ties[0]

    with mock.patch.object(random, 'choice', side_effect=choose):
        compute_move(snapshot)
    return seen[0]


def _random_game(mode_key, seed, bot_mode, bot_plies):
    """Play random moves to the end (or MAX_PLIES) and record every turn.

    Games with an odd seed mostly pick captures: they end sooner, so the
    eliminations and endings of 3- and 4-player games get tested too.
    """
    rng = random.Random(seed)
    capture_bias = 0.8 if seed % 2 else 0.0
    mode = ALL_MODES[mode_key]
    state = GameState.new(mode)
    plies = []
    for k in range(MAX_PLIES):
        over, winner = state.start_turn()
        ply = {'over': over, 'winner': winner, 'active': list(state.active_players),
               'turn': state.turn_index}
        plies.append(ply)
        if over:
            break
        moves = rules.expanded_moves(state.current_player, state.board, mode)
        ply['moves'] = [_move(m, d) + [n] for m, d, n in moves]
        if k in bot_plies:
            repeat = k % 3
            ply['bot'] = {'engine': bot_mode.ai_engine, 'depth': bot_mode.ai_depth,
                          'repeat': repeat, 'ties': _bot_ties(state, bot_mode, repeat)}
        captures = [i for i, (_m, _d, n) in enumerate(moves) if n]
        if captures and rng.random() < capture_bias:
            choice = rng.choice(captures)
        else:
            choice = rng.randrange(len(moves))
        greedy = rng.random() < 0.2   # sometimes leave the capture line to the default
        move, direction, _n = moves[choice]
        rules.make_move(state.board, move, mode, None if greedy else direction)
        state.advance_turn()
        ply.update(choice=choice, greedy=greedy,
                   after=[[p.x, p.y, p.color] for p in state.board.pieces])
    return {'mode': mode.name, 'seed': seed, 'plies': plies}


@unittest.skipIf(NODE is None, 'Node.js is not installed')
class TestWebVersion(unittest.TestCase):
    def _replay(self, mode_key, bot_key, games, bot_plies):
        bot_mode = with_difficulty(ALL_MODES[bot_key], 'medium')
        recorded = [_random_game(mode_key, seed, bot_mode, bot_plies if seed < 3 else ())
                    for seed in range(games)]
        result = subprocess.run([NODE, str(ROOT / 'tests' / 'web_replay.mjs')],
                                input=json.dumps(recorded), capture_output=True, text=True,
                                cwd=ROOT, timeout=600)
        lines = result.stdout.strip().splitlines()
        self.assertTrue(lines, result.stderr)
        report = json.loads(lines[-1])
        self.assertTrue(report['ok'], report.get('error'))
        self.assertEqual(report['plies'], sum(len(g['plies']) for g in recorded))
        self.assertGreater(report['botChecks'], 0)
        return recorded

    def test_two_players(self):
        games = self._replay('play_2', 'bot_2', games=30, bot_plies=(0, 9, 40, 101))
        self.assertGreaterEqual(sum(g['plies'][-1]['over'] for g in games), 25)

    def test_three_players(self):
        self._multiplayer('play_3', 'bot_3', games=16)

    def test_four_players(self):
        self._multiplayer('play_4', 'bot_4', games=12)

    def _multiplayer(self, mode_key, bot_key, games):
        recorded = self._replay(mode_key, bot_key, games, bot_plies=(0, 9, 40, 101))
        players = len(ALL_MODES[mode_key].players)
        endings = [g['plies'][-1] for g in recorded if g['plies'][-1]['over']]
        self.assertGreaterEqual(len(endings), games // 3)
        self.assertTrue(all(len(end['active']) == 1 for end in endings))
        # Sides went out one at a time, with their pieces left on the board.
        self.assertTrue(any(players > len(p['active']) > 1
                            for g in recorded for p in g['plies']))


if __name__ == '__main__':
    unittest.main()
