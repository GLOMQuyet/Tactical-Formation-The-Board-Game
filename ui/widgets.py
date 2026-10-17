"""Reusable UI widgets — buttons, game-over screen."""

import pygame

from ui import assets
from ui.theme import BLACK, BTN_HOVER, BTN_NORMAL, FPS, HEIGHT, TITLE_COLOR, WHITE, WIDTH


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
                return True
        return False


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
    def __init__(self, pos, size, callback):
        self.rect = pygame.Rect(pos, size)
        self.callback = callback
        self.hovered = False

    def draw(self, win):
        pygame.draw.rect(win, (105, 105, 105), self.rect)
        win.blit(assets.undo_icon(), self.rect.topleft)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif (event.type == pygame.MOUSEBUTTONDOWN
              and event.button == 1 and self.hovered):
            self.callback()


def game_over_screen(win, winner):
    """Wait for a choice. Returns 'restart', 'menu', or 'quit' (window closed)."""
    width, height = win.get_size()
    font = assets.big_font()
    clock = pygame.time.Clock()
    restart = Button('Restart Game', (width // 2 - 120, height // 2 + 20, 240, 50))
    to_menu = Button('Main Menu', (width // 2 - 120, height // 2 + 90, 240, 50))
    over_text = font.render(f'{winner.capitalize()} Wins!', True, TITLE_COLOR)
    over_rect = over_text.get_rect(center=(width // 2, height // 2 - 100))
    while True:
        clock.tick(FPS)
        win.fill(BLACK)
        win.blit(over_text, over_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if restart.handle(event):
                return 'restart'
            if to_menu.handle(event):
                return 'menu'
        restart.draw(win, font)
        to_menu.draw(win, font)
        pygame.display.update()
