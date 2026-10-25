"""Reusable UI widgets — buttons, game-over screen."""

import functools

import pygame

from ui import assets, display, i18n, sound
from ui.theme import (BLACK, BTN_HOVER, BTN_NORMAL, FPS, HEIGHT, OVERLAY_PANEL,
                      OVERLAY_SHADE, TITLE_COLOR, WHITE, WIDTH)


class Button:
    def __init__(self, text, rect, color=BTN_NORMAL, hover_color=BTN_HOVER):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, win, font):
        c = self.hover_color if self.hovered else self.color
        pygame.draw.rect(win, c, self.rect, border_radius=8)
        pygame.draw.rect(win, WHITE, self.rect, 2, border_radius=8)
        surf = font.render(self.text, True, WHITE)
        win.blit(surf, surf.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                sound.play('tap')
                return True
        return False


@functools.lru_cache(maxsize=64)
def _shadowed(font, text, color):
    """`text` over a soft dark outline, so it reads on a busy picture."""
    face = font.render(text, True, color)
    dark = font.render(text, True, BLACK)
    pad = 4
    surf = pygame.Surface((face.get_width() + 2 * pad, face.get_height() + 2 * pad), pygame.SRCALPHA)
    dark.set_alpha(110)
    for dx in (-2, 0, 2):
        for dy in (-2, 0, 2, 3):
            surf.blit(dark, (pad + dx, pad + dy))
    surf.blit(face, (pad, pad))
    return surf


def shadowed_text(win, font, text, color, center):
    surf = _shadowed(font, text, color)
    win.blit(surf, surf.get_rect(center=center))


def make_buttons(labels, colors=None, top=None, width=260, height=52, gap=18):
    """A centred column of buttons; `top` defaults to just below mid-screen."""
    total = len(labels) * height + (len(labels) - 1) * gap
    if top is None:
        top = HEIGHT // 2 - total // 2 + 30
    buttons = []
    for i, label in enumerate(labels):
        x = WIDTH // 2 - width // 2
        y = top + i * (height + gap)
        c = colors[i] if colors and colors[i] else BTN_NORMAL
        buttons.append(Button(label, (x, y, width, height), color=c))
    return buttons


class UndoButton:
    """A square button with the undo arrow, framed like the other buttons."""
    def __init__(self, pos, size, callback):
        self.rect = pygame.Rect(pos, size)
        self.callback = callback
        self.hovered = False

    def draw(self, win, enabled=True):
        face = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        box = face.get_rect()
        color = BTN_HOVER if self.hovered and enabled else BTN_NORMAL
        pygame.draw.rect(face, color, box, border_radius=8)
        pygame.draw.rect(face, WHITE, box, 2, border_radius=8)
        icon = pygame.transform.smoothscale(assets.undo_icon(), (box.w - 12, box.h - 12))
        face.blit(icon, icon.get_rect(center=box.center))
        if not enabled:
            face.set_alpha(110)
        win.blit(face, self.rect)

    def handle_event(self, event):
        """Run the callback on a click; return True if the click hit the button."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif (event.type == pygame.MOUSEBUTTONDOWN
              and event.button == 1 and self.rect.collidepoint(event.pos)):
            sound.play('tap')
            self.callback()
            return True
        return False


def pressed(event, *keys):
    """True if `event` is a key press of one of `keys`."""
    return event.type == pygame.KEYDOWN and event.key in keys


def button_font():
    return assets.font('assets/fonts/Roboto-Regular.ttf', 26)


def choice_overlay(win, background, title, options, subtitle=None, escape=None):
    """Show a panel with `title` and buttons over a dimmed `background`.

    `options` is a list of (label, result). Returns the chosen result, `escape`
    when Esc is pressed (if given), or 'quit' if the window is closed.
    """
    width, height = win.get_size()
    clock = pygame.time.Clock()
    panel = pygame.Rect(0, 0, 460, 140 + len(options) * 64)
    panel.center = (width // 2, height // 2)
    buttons = [Button(label, (panel.centerx - 150, panel.top + 120 + i * 64, 300, 52))
               for i, (label, _result) in enumerate(options)]
    shade = pygame.Surface((width, height), pygame.SRCALPHA)
    shade.fill(OVERLAY_SHADE)
    box = pygame.Surface(panel.size, pygame.SRCALPHA)
    pygame.draw.rect(box, OVERLAY_PANEL, box.get_rect(), border_radius=14)
    title_surf = assets.big_font().render(title, True, TITLE_COLOR)
    sub_surf = assets.small_font().render(subtitle, True, WHITE) if subtitle else None
    while True:
        clock.tick(FPS)
        win.blit(background, (0, 0))
        win.blit(shade, (0, 0))
        win.blit(box, panel.topleft)
        pygame.draw.rect(win, TITLE_COLOR, panel, 2, border_radius=14)
        win.blit(title_surf, title_surf.get_rect(center=(panel.centerx, panel.top + 45)))
        if sub_surf is not None:
            win.blit(sub_surf, sub_surf.get_rect(center=(panel.centerx, panel.top + 88)))
        for event in display.events():
            if event.type == pygame.QUIT:
                return 'quit'
            if escape is not None and pressed(event, pygame.K_ESCAPE):
                return escape
            for button, (_label, result) in zip(buttons, options):
                if button.handle(event):
                    return result
        for b in buttons:
            b.draw(win, button_font())
        display.present()


def game_over_screen(win, winner, background, yours=False):
    """Result over the final board. Returns 'restart', 'menu' or 'quit'.

    `yours` says "You win!" (a person who beat the bots).
    """
    title = (i18n.t('you_win') if yours else i18n.t('wins', color=i18n.color(winner))
             if winner else '?')
    return choice_overlay(win, background, title,
                          [(i18n.t('new_game'), 'restart'), (i18n.t('main_menu'), 'menu')],
                          escape='menu')


def eliminated_screen(win, background):
    """The human is out of a bot game. Returns 'watch', 'restart', 'menu' or 'quit'."""
    return choice_overlay(win, background, i18n.t('you_are_out'),
                          [(i18n.t('watch'), 'watch'), (i18n.t('new_game'), 'restart'),
                           (i18n.t('main_menu'), 'menu')],
                          subtitle=i18n.t('bots_play_on'), escape='watch')
