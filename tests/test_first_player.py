"""Who moves first, the folk way: oẳn tù tì and úp lá xòe.

Run with: uv run python -m unittest tests.test_first_player
"""

import random
import unittest

from core import first_player
from core.first_player import settle


class TestRockPaperScissors(unittest.TestCase):
    def test_each_hand_beats_one_other(self):
        self.assertEqual(settle(['green', 'yellow'], {'green': 'rock', 'yellow': 'scissors'}), ['green'])
        self.assertEqual(settle(['green', 'yellow'], {'green': 'rock', 'yellow': 'paper'}), ['yellow'])
        self.assertEqual(settle(['green', 'yellow'], {'green': 'scissors', 'yellow': 'paper'}), ['green'])

    def test_the_same_hand_is_played_again(self):
        for hand in first_player.ROCK_PAPER_SCISSORS:
            self.assertEqual(settle(['green', 'yellow'], {'green': hand, 'yellow': hand}),
                             ['green', 'yellow'])


class TestPalmDownPalmUp(unittest.TestCase):
    def test_the_odd_one_drops_out(self):
        players = ['purple', 'yellow', 'green']
        self.assertEqual(settle(players, {'purple': 'down', 'yellow': 'up', 'green': 'down'}),
                         ['purple', 'green'])
        four = ['blue', 'green', 'purple', 'yellow']
        self.assertEqual(settle(four, {'blue': 'up', 'green': 'up', 'purple': 'down', 'yellow': 'up'}),
                         ['blue', 'green', 'yellow'])

    def test_all_alike_or_an_even_split_is_shown_again(self):
        four = ['blue', 'green', 'purple', 'yellow']
        self.assertEqual(settle(four, dict.fromkeys(four, 'up')), four)
        self.assertEqual(settle(four, {'blue': 'up', 'green': 'down', 'purple': 'up', 'yellow': 'down'}),
                         four)

    def test_three_or_four_players_show_palms_two_play_rock_paper_scissors(self):
        self.assertEqual(first_player.hands_for(['a', 'b', 'c']), first_player.DOWN_UP)
        self.assertEqual(first_player.hands_for(['a', 'b']), first_player.ROCK_PAPER_SCISSORS)

    def test_random_hands_always_end_with_one_player(self):
        rng = random.Random(7)
        for players in (['g', 'y'], ['p', 'y', 'g'], ['b', 'g', 'p', 'y']):
            for _ in range(200):
                left = list(players)
                for _round in range(1000):
                    if len(left) == 1:
                        break
                    left = settle(left, {c: first_player.bot_hand(left, rng) for c in left})
                self.assertEqual(len(left), 1)
                self.assertIn(left[0], players)


if __name__ == '__main__':
    unittest.main()
