"""Tactical Formation — entry point: start pygame, then switch between screens.

Run with: uv run main.py
"""

import multiprocessing

import pygame

from core import savegame
from core.modes import ALL_MODES, with_difficulty
from ui import assets
from ui.screens import game, howto, menu
from ui.theme import HEIGHT, WIDTH

_HUMAN_GAMES = ('play_2', 'play_3', 'play_4')
_BOT_GAMES = ('bot_2', 'bot_3', 'bot_4')


def main():
    # The game has no sound, so only the display and font modules are started
    # (pygame.init() would also open the audio device).
    pygame.display.init()
    pygame.font.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tactical Formation')

    font = assets.font('assets/fonts/Roboto-Bold.ttf', 42)
    font_small = assets.font('assets/fonts/Roboto-Regular.ttf', 28)
    bg = assets.welcome_background_image()
    screens = (win, font, font_small, bg)

    screen = 'menu'
    while screen != 'exit':
        if screen == 'menu':
            screen = menu.main_menu(*screens, saved=savegame.load())
        elif screen == 'continue':
            saved = savegame.load()
            if saved is None:
                screen = 'menu'
            else:
                screen = game.run(win, saved.state.mode, saved.difficulty, saved)
        elif screen == 'human':
            screen = menu.human_menu(*screens)
        elif screen == 'bot':
            screen = menu.bot_menu(*screens)
        elif screen == 'howto':
            screen = howto.how_to_play_screen(*screens)
        elif screen in _HUMAN_GAMES:
            result = game.run(win, ALL_MODES[screen])
            screen = 'human' if result == 'menu' else result
        elif screen in _BOT_GAMES:
            level = menu.difficulty_menu(*screens, screen)
            if level == 'exit':
                screen = 'exit'
            elif level == 'back':
                screen = 'bot'
            else:
                mode = with_difficulty(ALL_MODES[screen], level)
                result = game.run(win, mode, level)
                screen = 'bot' if result == 'menu' else result
        else:
            screen = 'menu'

    pygame.quit()


if __name__ == '__main__':
    multiprocessing.freeze_support()   # bots search in a worker process (ai/worker.py)
    main()
