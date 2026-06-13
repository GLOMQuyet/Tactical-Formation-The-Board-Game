"""Reusable UI widgets — buttons, game-over screen."""

import asyncio
import sys

import pygame

from ui import assets


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 215, 0)
BTN_NORMAL = (65, 105, 225)
BTN_HOVER = (70, 130, 180)


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


async def game_over_screen(win, winner):
    """Block until user clicks Restart or Exit. Returns 'restart' or 'exit'."""
    width, height = win.get_size()
    font = assets.big_font()
    restart = Button('Restart Game',
                     (width // 2 - 120, height // 2 + 20, 240, 50))
    exit_btn = Button('Exit',
                      (width // 2 - 120, height // 2 + 90, 240, 50))
    over_text = font.render(f'{winner.capitalize()} Wins!', True, HIGHLIGHT_COLOR)
    over_rect = over_text.get_rect(center=(width // 2, height // 2 - 100))
    while True:
        win.fill(BLACK)
        win.blit(over_text, over_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if restart.handle(event):
                return 'restart'
            if exit_btn.handle(event):
                return 'exit'
        restart.draw(win, font)
        exit_btn.draw(win, font)
        pygame.display.update()
        await asyncio.sleep(0)
