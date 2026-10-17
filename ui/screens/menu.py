"""Menu screens: main menu, player-count choices and bot difficulty.

Each screen runs until the player picks something and returns a short string
naming the next screen; main.py does the switching.
"""

import pygame

from ui import assets
from ui.theme import (BTN_BACK, BTN_EXIT, BTN_HOWTO, BTN_NORMAL, BTN_RESUME,
                      FPS, HEIGHT, NOTE_BACKING, TITLE_COLOR, WHITE, WIDTH)
from ui.widgets import make_buttons

_GAME_NAMES = {
    'play_2': '2 players', 'play_3_human': '3 players', 'play_4_human': '4 players',
    'bot_2': '1 vs Bot (2P)', 'play_3': '2 Bots (3P)', 'play_4': '3 Bots (4P)',
}

_BOT_GAMES = {'bot_2': '1 vs Bot (2P)', 'bot_3': '2 Bots (3P)', 'bot_4': '3 Bots (4P)'}

# Sub-menu buttons start below the title and subtitle.
_SUBMENU_TOP = HEIGHT // 2 - 70


def _choose(win, font, font_small, bg, title, subtitle, buttons, results,
            notes=(), title_y=HEIGHT // 2 - 160):
    """Draw a menu and return the result of the clicked button ('exit' on close)."""
    clock = pygame.time.Clock()
    while True:
        clock.tick(FPS)
        win.blit(bg, (0, 0))
        t = font.render(title, True, TITLE_COLOR)
        win.blit(t, t.get_rect(center=(WIDTH // 2, title_y)))
        s = font_small.render(subtitle, True, WHITE)
        win.blit(s, s.get_rect(center=(WIDTH // 2, title_y + 50)))
        for text, y in notes:
            n = assets.small_font().render(text, True, WHITE)
            rect = n.get_rect(center=(WIDTH // 2, y))
            backing = pygame.Surface(rect.inflate(24, 10).size, pygame.SRCALPHA)
            backing.fill(NOTE_BACKING)
            win.blit(backing, rect.inflate(24, 10))
            win.blit(n, rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            for button, result in zip(buttons, results):
                if button.handle(event):
                    return result
        for b in buttons:
            b.draw(win, font_small)
        pygame.display.flip()


def main_menu(win, font, font_small, bg, saved=None):
    """`saved` is the autosaved game (core.savegame.SavedGame) or None."""
    labels = ['Play Human', 'Play Bot', 'How to Play', 'Exit']
    colors = [BTN_NORMAL, BTN_NORMAL, BTN_HOWTO, BTN_EXIT]
    results = ['human', 'bot', 'howto', 'exit']
    notes = ()
    top = None
    if saved is not None:
        labels.insert(0, 'Continue')
        colors.insert(0, BTN_RESUME)
        results.insert(0, 'continue')
        name = _GAME_NAMES.get(saved.state.mode.name, saved.state.mode.name)
        level = f', {saved.difficulty}' if saved.difficulty else ''
        notes = ((f'Saved game: {name}{level}, {len(saved.moves)} moves played',
                  HEIGHT // 2 - 85),)
        top = HEIGHT // 2 - 55
    buttons = make_buttons(labels, colors, top=top)
    return _choose(win, font, font_small, bg, 'Tactical Formation',
                   'Strategy Board Game', buttons, results, notes,
                   title_y=HEIGHT // 2 - 175)


def human_menu(win, font, font_small, bg):
    buttons = make_buttons(['2 Players', '3 Players', '4 Players', '<- Back'],
                           [BTN_NORMAL, BTN_NORMAL, BTN_NORMAL, BTN_BACK], top=_SUBMENU_TOP)
    return _choose(win, font, font_small, bg, 'Play Human',
                   'Choose number of players', buttons,
                   ['play_2', 'play_3', 'play_4', 'menu'])


def bot_menu(win, font, font_small, bg):
    buttons = make_buttons(['1 vs Bot  (2P)', '2P + 2 Bots (3P)', '1P + 3 Bots (4P)', '<- Back'],
                           [BTN_NORMAL, BTN_NORMAL, BTN_NORMAL, BTN_BACK], top=_SUBMENU_TOP)
    return _choose(win, font, font_small, bg, 'Play vs Bot',
                   'You always play as Green', buttons,
                   ['bot_2', 'bot_3', 'bot_4', 'menu'])


def difficulty_menu(win, font, font_small, bg, game):
    """Pick the bots' strength for `game` ('bot_2', 'bot_3' or 'bot_4').

    Returns 'easy', 'medium', 'hard', 'back' or 'exit'.
    """
    buttons = make_buttons(['Easy', 'Medium', 'Hard', '<- Back'],
                           [BTN_NORMAL, BTN_NORMAL, BTN_NORMAL, BTN_BACK], top=_SUBMENU_TOP)
    return _choose(win, font, font_small, bg, 'Difficulty', _BOT_GAMES[game],
                   buttons, ['easy', 'medium', 'hard', 'back'],
                   notes=(('Harder bots look further ahead and think longer',
                           _SUBMENU_TOP + 300),))
