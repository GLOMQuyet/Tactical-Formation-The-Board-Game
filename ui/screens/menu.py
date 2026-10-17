"""Menu screens: main menu, player-count choices, bot difficulty and the
unfinished-game question.

Each screen runs until the player picks something and returns a short string
naming the next screen; main.py does the switching. Labels come from ui.i18n,
so every screen follows the language chosen on the main menu.
"""

import pygame

from ui import assets, i18n
from ui.theme import (BTN_BACK, BTN_EXIT, BTN_HOWTO, BTN_LANG, BTN_NORMAL, BTN_RESUME,
                      FPS, HEIGHT, NOTE_BACKING, TITLE_COLOR, WHITE, WIDTH)
from ui.widgets import Button, make_buttons

# Sub-menu buttons start below the title and subtitle.
_SUBMENU_TOP = HEIGHT // 2 - 70


def describe(saved):
    """One line about a saved game, e.g. 'Saved game: 1 vs Bot (2P), Hard, 12 moves played'."""
    game = i18n.t(f'game_{saved.state.mode.name}')
    level = f', {i18n.t(saved.difficulty)}' if saved.difficulty else ''
    return i18n.t('saved_game', game=game, level=level, moves=len(saved.moves))


def _choose(win, font, font_small, bg, title, subtitle, buttons, results,
            notes=(), title_y=HEIGHT // 2 - 160, extra=()):
    """Draw a menu and return the result of the clicked button ('exit' on close).

    `extra` holds (button, result, font) for small buttons drawn with their own font.
    """
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
            for button, result, _font in extra:
                if button.handle(event):
                    return result
        for b in buttons:
            b.draw(win, font_small)
        for button, _result, button_font in extra:
            button.draw(win, button_font)
        pygame.display.flip()


def main_menu(win, font, font_small, bg, saved=None):
    """`saved` is the autosaved game (core.savegame.SavedGame) or None.

    Returns 'continue', 'human', 'bot', 'howto', 'language' or 'exit'.
    """
    labels = [i18n.t('play_human'), i18n.t('play_bot'), i18n.t('how_to_play'), i18n.t('exit')]
    colors = [BTN_NORMAL, BTN_NORMAL, BTN_HOWTO, BTN_EXIT]
    results = ['human', 'bot', 'howto', 'exit']
    notes = ()
    top = None
    if saved is not None:
        labels.insert(0, i18n.t('continue'))
        colors.insert(0, BTN_RESUME)
        results.insert(0, 'continue')
        notes = ((describe(saved), HEIGHT // 2 - 85),)
        top = HEIGHT // 2 - 55
    buttons = make_buttons(labels, colors, top=top)
    language = Button(i18n.t('other_language'), (WIDTH - 170, 12, 156, 40), color=BTN_LANG)
    return _choose(win, font, font_small, bg, 'Tactical Formation', i18n.t('subtitle'),
                   buttons, results, notes, title_y=HEIGHT // 2 - 175,
                   extra=((language, 'language', assets.small_font()),))


def human_menu(win, font, font_small, bg):
    buttons = make_buttons([i18n.t('players_2'), i18n.t('players_3'), i18n.t('players_4'),
                            i18n.t('back')],
                           [BTN_NORMAL, BTN_NORMAL, BTN_NORMAL, BTN_BACK], top=_SUBMENU_TOP)
    return _choose(win, font, font_small, bg, i18n.t('play_human'), i18n.t('choose_players'),
                   buttons, ['play_2', 'play_3', 'play_4', 'menu'])


def bot_menu(win, font, font_small, bg):
    buttons = make_buttons([i18n.t('game_bot_2'), i18n.t('game_play_3'), i18n.t('game_play_4'),
                            i18n.t('back')],
                           [BTN_NORMAL, BTN_NORMAL, BTN_NORMAL, BTN_BACK], top=_SUBMENU_TOP,
                           width=320)
    return _choose(win, font, font_small, bg, i18n.t('vs_bot'), i18n.t('you_are_green'),
                   buttons, ['bot_2', 'bot_3', 'bot_4', 'menu'])


def difficulty_menu(win, font, font_small, bg, mode):
    """Pick the bots' strength for `mode`. Returns 'easy', 'medium', 'hard', 'back' or 'exit'."""
    buttons = make_buttons([i18n.t('easy'), i18n.t('medium'), i18n.t('hard'), i18n.t('back')],
                           [BTN_NORMAL, BTN_NORMAL, BTN_NORMAL, BTN_BACK], top=_SUBMENU_TOP)
    return _choose(win, font, font_small, bg, i18n.t('difficulty'),
                   i18n.t(f'game_{mode.name}'), buttons, ['easy', 'medium', 'hard', 'back'],
                   notes=((i18n.t('difficulty_note'), _SUBMENU_TOP + 300),))


def unfinished_game_menu(win, font, font_small, bg, saved):
    """Asked before a new game would replace the saved one.

    Returns 'new', 'continue', 'back' or 'exit'.
    """
    buttons = make_buttons([i18n.t('start_new'), i18n.t('keep_saved'), i18n.t('back')],
                           [BTN_NORMAL, BTN_RESUME, BTN_BACK], top=_SUBMENU_TOP, width=320)
    return _choose(win, font, font_small, bg, i18n.t('unfinished'), i18n.t('replace_note'),
                   buttons, ['new', 'continue', 'back'],
                   notes=((describe(saved), _SUBMENU_TOP + 240),))
