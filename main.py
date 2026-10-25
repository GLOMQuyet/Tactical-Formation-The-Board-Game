"""Tactical Formation — entry point: start pygame, then switch between screens.

Run with: uv run main.py
"""

import multiprocessing

import pygame

from core import savegame
from core.modes import ALL_MODES, with_difficulty, with_side
from ui import assets, display, i18n, settings
from ui.screens import game, howto, menu

_HUMAN_GAMES = ('play_2', 'play_3', 'play_4')
_BOT_GAMES = ('bot_2', 'bot_3', 'bot_4')


def main():
    # Only the display and fonts are started here; ui.sound opens the audio
    # device on the first sound, and a computer without one stays quiet.
    pygame.display.init()
    pygame.font.init()
    win = display.open_window('Tactical Formation', assets.image('assets/green_piece.png'))

    font = assets.font('assets/fonts/Roboto-Bold.ttf', 42)
    font_small = assets.font('assets/fonts/Roboto-Regular.ttf', 28)
    bg = assets.welcome_background_image()
    screens = (win, font, font_small, bg)

    def start(mode, difficulty=None, back='menu'):
        """Start a new game, first asking if it would replace a saved one."""
        saved = savegame.load()
        if saved is not None:
            choice = menu.unfinished_game_menu(*screens, saved)
            if choice == 'continue':
                return 'continue'
            if choice != 'new':
                return 'exit' if choice == 'exit' else back
            # The saved game stays until the new one's first move replaces
            # it, so leaving before that (even while choosing who goes
            # first) loses nothing.
        result = game.run(win, mode, difficulty)
        return 'exit' if result == 'exit' else 'menu'

    screen = 'menu'
    while screen != 'exit':
        if screen == 'menu':
            screen = menu.main_menu(*screens, saved=savegame.load())
        elif screen == 'language':
            i18n.toggle()
            screen = 'menu'
        elif screen == 'continue':
            saved = savegame.load()
            if saved is None:
                screen = 'menu'
            else:
                result = game.run(win, saved.state.mode, saved.difficulty, saved)
                screen = 'exit' if result == 'exit' else 'menu'
        elif screen == 'human':
            screen = menu.human_menu(*screens)
        elif screen == 'bot':
            screen = menu.bot_menu(*screens)
        elif screen == 'howto':
            screen = howto.how_to_play_screen(*screens)
        elif screen == 'settings':
            choice = menu.settings_menu(*screens)
            if choice in ('sound', 'symbols', 'folk_start'):
                settings.toggle(choice)
                choice = 'settings'
            screen = choice
        elif screen in _HUMAN_GAMES:
            screen = start(ALL_MODES[screen], back='human')
        elif screen in _BOT_GAMES:
            mode = ALL_MODES[screen]
            level = menu.difficulty_menu(*screens, mode)
            if level in ('exit', 'back'):
                screen = 'exit' if level == 'exit' else 'bot'
                continue
            side = menu.side_menu(*screens, mode, level)
            if side == 'exit':
                screen = 'exit'
            elif side != 'back':   # back from the sides shows the difficulties again
                screen = start(with_side(with_difficulty(mode, level), side), level, back='bot')
        else:
            screen = 'menu'

    pygame.quit()


if __name__ == '__main__':
    multiprocessing.freeze_support()   # bots search in a worker process (ai/worker.py)
    main()
