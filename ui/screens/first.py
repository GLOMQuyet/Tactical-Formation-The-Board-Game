"""Who goes first, the folk way (core.first_player), over the dimmed board.

Each person picks a hand in turn (hidden from the others when several people
share the computer) and the bots pick at random. Everybody chants, then all
hands are shown at once. Rounds go on until one player is left; that player
moves first.
"""

import math
import random
import time

import pygame

from core import first_player
from ui import assets, display, i18n, sound
from ui.theme import BTN_BACK, BTN_HOVER, BTN_NORMAL, FPS, OVERLAY_PANEL, OVERLAY_SHADE, TITLE_COLOR, WHITE
from ui.widgets import Button, button_font, pressed

BEAT = 0.45     # s for each word of the chant
SHOW = 1.8      # s the hands stay shown before the next round
DONE = 3.0      # s before the game starts by itself once the first player is known
HAND = 100      # px, a player's hand
CHOICE = 84     # px, a hand on a choice button

_PANEL = pygame.Rect(50, 110, 700, 580)


def _hand(name, size=HAND):
    return assets.image(f'assets/hands/{name}.png', size=(size, size))


def _text(win, font, text, color, center):
    surf = font.render(text, True, color)
    win.blit(surf, surf.get_rect(center=center))


def choose_first(win, mode, background, rng=random):
    """Return the colour that moves first, or 'menu' (Esc) or 'quit'.

    "Skip" keeps the usual order: the first colour of the mode.
    """
    clock = pygame.time.Clock()
    humans = [c for c in mode.players if c in mode.human_colors]
    name_font = assets.font('assets/fonts/Roboto-Bold.ttf', 20)
    chant_font = assets.font('assets/fonts/Roboto-Bold.ttf', 40)
    line_font = assets.font('assets/fonts/Roboto-Bold.ttf', 24)
    skip = Button(i18n.t('skip'), (_PANEL.right - 130, _PANEL.bottom - 52, 110, 38), color=BTN_BACK)
    start = Button(i18n.t('start_game'), (_PANEL.centerx - 110, _PANEL.top + 470, 220, 50))
    shade = pygame.Surface(win.get_size(), pygame.SRCALPHA)
    shade.fill(OVERLAY_SHADE)
    box = pygame.Surface(_PANEL.size, pygame.SRCALPHA)
    pygame.draw.rect(box, OVERLAY_PANEL, box.get_rect(), border_radius=14)
    xs = {c: _PANEL.left + _PANEL.w * (i + 0.5) / len(mode.players)
          for i, c in enumerate(mode.players)}

    contenders = list(mode.players)
    round_players = list(contenders)   # who showed a hand in the round on screen
    hands = {}
    to_pick = []
    phase = 'pick'
    since = time.monotonic()
    beat = -1
    lines = []
    winner = None
    choices = []

    def new_round():
        nonlocal hands, to_pick, phase, since, beat, round_players, choices
        round_players = list(contenders)
        hands = {c: first_player.bot_hand(contenders, rng)
                 for c in contenders if c not in mode.human_colors}
        to_pick = [c for c in contenders if c in mode.human_colors]
        options = first_player.hands_for(contenders)
        width = 130
        left = _PANEL.centerx - (len(options) * width + (len(options) - 1) * 20) // 2
        choices = [(name, pygame.Rect(left + k * (width + 20), _PANEL.top + 345, width, 128))
                   for k, name in enumerate(options)]
        phase = 'pick' if to_pick else 'chant'
        since, beat = time.monotonic(), -1

    def settle():
        nonlocal contenders, phase, since, lines, winner
        left = first_player.settle(contenders, hands)
        lines = []
        if len(left) == 1:
            winner = left[0]
            if len(contenders) == 2:
                loser = next(c for c in contenders if c != winner)
                lines.append(i18n.t('beats', a=i18n.t(f'hand_{hands[winner]}'),
                                    b=i18n.t(f'hand_{hands[loser]}').lower()))
            mine = bool(mode.bot_colors) and winner in mode.human_colors
            lines.append(i18n.t('you_go_first') if mine
                         else i18n.t('goes_first', color=i18n.color(winner)))
            phase = 'done'
            sound.play('win')
        else:
            if left == contenders:
                lines.append(i18n.t('same_again' if len(contenders) == 2 else 'even_again'))
            else:
                out = ', '.join(i18n.color(c) for c in contenders if c not in left)
                lines.append(i18n.t('drops_out', color=out))
            contenders = left
            phase = 'show'
            sound.play('reveal')
        since = time.monotonic()

    new_round()
    while True:
        clock.tick(FPS)
        now = time.monotonic()
        mouse_hover = None

        # ── Timed steps ──────────────────────────────────────────────────
        if phase == 'chant':
            k = int((now - since) / BEAT)
            if k != beat and k < 3:
                beat = k
                sound.play('beat')
            if now - since >= 3 * BEAT:
                settle()
        elif phase == 'show' and now - since >= SHOW:
            new_round()
        elif phase == 'done' and now - since >= DONE:
            return winner

        # ── Events ───────────────────────────────────────────────────────
        for event in display.events():
            if event.type == pygame.QUIT:
                return 'quit'
            if pressed(event, pygame.K_ESCAPE):
                return 'menu'
            if event.type == pygame.MOUSEMOTION:
                mouse_hover = event.pos
            if phase != 'done' and skip.handle(event):
                return mode.players[0]
            if phase == 'done':
                if start.handle(event) or pressed(event, pygame.K_RETURN, pygame.K_SPACE):
                    return winner
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if phase == 'pick':
                    for name, rect in choices:
                        if rect.collidepoint(event.pos):
                            hands[to_pick.pop(0)] = name
                            sound.play('tap')
                            if not to_pick:
                                phase, since, beat = 'chant', time.monotonic(), -1
                            break
                elif phase == 'show':
                    new_round()   # a click skips the pause

        # ── Drawing ──────────────────────────────────────────────────────
        win.blit(background, (0, 0))
        win.blit(shade, (0, 0))
        win.blit(box, _PANEL.topleft)
        pygame.draw.rect(win, TITLE_COLOR, _PANEL, 2, border_radius=14)
        _text(win, assets.big_font(), i18n.t('who_first'), TITLE_COLOR, (_PANEL.centerx, _PANEL.top + 40))
        rule = 'rule_rps' if len(round_players) == 2 else 'rule_updown'
        _text(win, assets.hint_font(), i18n.t(rule), WHITE, (_PANEL.centerx, _PANEL.top + 78))

        shown = phase in ('show', 'done')
        for color in mode.players:
            x = xs[color]
            playing = color in round_players
            icon = assets.piece_image(color).copy()
            name = name_font.render(i18n.color(color), True, WHITE)
            if not playing:
                icon.set_alpha(70)
                name.set_alpha(90)
            win.blit(icon, icon.get_rect(center=(x, _PANEL.top + 118)))
            win.blit(name, name.get_rect(center=(x, _PANEL.top + 152)))
            if not playing:
                continue
            center = (x, _PANEL.top + 236)
            if shown:
                img = _hand(hands[color])
                if color == winner or (phase == 'show' and color in contenders):
                    pygame.draw.circle(win, TITLE_COLOR, center, HAND // 2 + 8, 4)
                elif phase == 'show' or winner is not None:
                    img = img.copy()
                    img.set_alpha(110)
                win.blit(img, img.get_rect(center=center))
            elif phase == 'chant':   # everyone shakes a closed hand to the chant
                t = (now - since) / BEAT
                lift = 14 * abs(math.sin(math.pi * t))
                img = _hand('rock')
                win.blit(img, img.get_rect(center=(center[0], center[1] - lift)))
            elif color in hands:     # picked: a tick that gives nothing away
                cx, cy = center
                pygame.draw.circle(win, TITLE_COLOR, center, 34, 3)
                pygame.draw.lines(win, TITLE_COLOR, False,
                                  [(cx - 15, cy + 1), (cx - 4, cy + 13), (cx + 16, cy - 12)], 6)
            else:
                pygame.draw.circle(win, WHITE, center, 34, 3)
                _text(win, chant_font, '?', WHITE, center)

        if phase == 'pick' and to_pick:
            picker = to_pick[0]
            prompt = (i18n.t('pick_secret', color=i18n.color(picker)) if len(humans) > 1
                      else i18n.t('pick_yours'))
            _text(win, line_font, prompt, TITLE_COLOR, (_PANEL.centerx, _PANEL.top + 318))
            pointer = mouse_hover or display.to_canvas(pygame.mouse.get_pos())
            for name, rect in choices:
                hover = rect.collidepoint(pointer)
                pygame.draw.rect(win, BTN_HOVER if hover else BTN_NORMAL, rect, border_radius=10)
                pygame.draw.rect(win, WHITE, rect, 2, border_radius=10)
                img = _hand(name, CHOICE)
                win.blit(img, img.get_rect(center=(rect.centerx, rect.top + 52)))
                _text(win, assets.hint_font(bold=True), i18n.t(f'hand_{name}'), WHITE,
                      (rect.centerx, rect.bottom - 18))
        elif phase == 'chant':
            word = i18n.t(f"chant_{'rps' if len(round_players) == 2 else 'updown'}_{min(max(beat, 0), 2) + 1}")
            _text(win, chant_font, word, TITLE_COLOR, (_PANEL.centerx, _PANEL.top + 390))
        else:
            for k, line in enumerate(lines):
                last = k == len(lines) - 1
                _text(win, chant_font if last and winner else line_font, line,
                      TITLE_COLOR if last else WHITE,
                      (_PANEL.centerx, _PANEL.top + 345 + 50 * k + (10 if len(lines) == 1 else 0)))
        if phase == 'done':
            start.draw(win, button_font())
        else:
            skip.draw(win, assets.hint_font(bold=True))
        display.present()
