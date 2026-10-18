"""Screen tests — the real menus and game screen, headless (SDL dummy driver).

Run with: uv run python -m unittest tests.test_ui
"""

import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import dataclasses  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402

import pygame  # noqa: E402

from core import savegame  # noqa: E402
from core.board import Board  # noqa: E402
from core.modes import MODE_BOT_2, MODE_PLAY_3  # noqa: E402
from core.piece import Piece  # noqa: E402
from core.savegame import SavedGame  # noqa: E402
from core.state import GameState  # noqa: E402
from ui import assets, display, i18n  # noqa: E402
from ui.screens import game, howto, menu  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _Screens(unittest.TestCase):
    """An 800×800 display, assets from the repository, a throw-away save file."""

    @classmethod
    def setUpClass(cls):
        cls._resource_path = assets.resource_path
        assets.resource_path = lambda rel: os.path.join(REPO, rel)
        pygame.display.init()
        pygame.font.init()
        cls.win = pygame.display.set_mode((800, 800))

    @classmethod
    def tearDownClass(cls):
        assets.resource_path = cls._resource_path

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self._default_path = savegame.default_path
        savegame.default_path = lambda: os.path.join(self.folder.name, 'autosave.json')
        self._screens = (game.game_over_screen, game.eliminated_screen)
        self._get = pygame.event.get

    def tearDown(self):
        savegame.default_path = self._default_path
        game.game_over_screen, game.eliminated_screen = self._screens
        pygame.event.get = self._get
        self.folder.cleanup()

    def quit_on_second_frame(self):
        frames = {'n': 0}

        def get(*a, **k):
            self._get()
            frames['n'] += 1
            return [pygame.event.Event(pygame.QUIT)] if frames['n'] > 1 else []
        pygame.event.get = get


class TestGameScreen(_Screens):
    def test_a_finished_game_shows_the_result(self):
        # Green (a 1-ply bot here) can flip Yellow's last piece; the game must end.
        mode = dataclasses.replace(MODE_BOT_2, ai_depth=1, bot_delay_ms=0,
                                   bot_colors=frozenset({'green', 'yellow'}),
                                   human_colors=frozenset())
        board = Board([Piece(0, 2, 'green'), Piece(1, 2, 'green'),
                       Piece(3, 2, 'yellow'), Piece(4, 2, 'green')])
        state = GameState(board=board, active_players=['green', 'yellow'], turn_index=0, mode=mode)
        shown = []
        game.game_over_screen = lambda win, winner, background: shown.append(winner) or 'menu'
        self.assertEqual(game.run(self.win, mode, saved=SavedGame(state, [], None)), 'menu')
        self.assertEqual(shown, ['green'])
        self.assertFalse(os.path.exists(savegame.default_path()))

    def test_a_knocked_out_player_is_told(self):
        # Green (the human) has no move on its turn in a game against two bots.
        mode = dataclasses.replace(MODE_PLAY_3, bot_delay_ms=0)
        board = Board([Piece(6, 0, 'green'),
                       Piece(1, 1, 'purple'), Piece(2, 1, 'purple'),
                       Piece(1, 3, 'yellow'), Piece(2, 3, 'yellow')])
        state = GameState(board=board, active_players=['purple', 'yellow', 'green'],
                          turn_index=2, mode=mode)
        savegame.save(state, [])   # an earlier save of this game
        asked = []
        game.eliminated_screen = lambda win, background: asked.append(True) or 'menu'
        self.assertEqual(game.run(self.win, mode, 'hard', SavedGame(state, [], 'hard')), 'menu')
        self.assertEqual(asked, [True])
        self.assertFalse(os.path.exists(savegame.default_path()))

    def test_closing_the_window_leaves_the_game(self):
        self.quit_on_second_frame()
        self.assertEqual(game.run(self.win, MODE_BOT_2, 'easy'), 'exit')


class TestMenus(_Screens):
    def test_every_menu_draws_in_both_languages(self):
        font = assets.font('assets/fonts/Roboto-Bold.ttf', 42)
        small = assets.font('assets/fonts/Roboto-Regular.ttf', 28)
        bg = assets.welcome_background_image()
        screens = (self.win, font, small, bg)
        saved = SavedGame(GameState.new(MODE_BOT_2), [], 'easy')
        before = i18n.lang()
        try:
            for lang in i18n.LANGS:
                i18n.set_lang(lang, save=False)
                for draw in (lambda: menu.main_menu(*screens, saved=saved),
                             lambda: menu.human_menu(*screens),
                             lambda: menu.bot_menu(*screens),
                             lambda: menu.difficulty_menu(*screens, MODE_PLAY_3),
                             lambda: menu.unfinished_game_menu(*screens, saved),
                             lambda: howto.how_to_play_screen(*screens)):
                    self.quit_on_second_frame()
                    self.assertEqual(draw(), 'exit', lang)
        finally:
            i18n.set_lang(before, save=False)


class TestWindow(unittest.TestCase):
    def tearDown(self):
        display._canvas = None
        pygame.display.set_mode((800, 800))

    def test_clicks_map_to_the_board_in_a_small_window(self):
        pygame.display.init()
        pygame.display.set_mode((600, 400))           # a wide, small window
        display._canvas = pygame.Surface((800, 800))
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(300, 200), button=1))
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 0), button=1))
        clicks = [e.pos for e in display.events() if e.type == pygame.MOUSEBUTTONDOWN]
        self.assertEqual(clicks, [(400, 400), (0, 0)])   # centre, and the board's corner
        display.present()                                # scaling must not fail


if __name__ == '__main__':
    unittest.main()
