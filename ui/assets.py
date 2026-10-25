"""Lazy, cached pygame asset loading.

Top-level `core` and `ai` modules MUST NOT import this — only UI does. That way
unit tests and headless AI runs don't need a display surface.
"""

import os
import sys
import functools

import pygame


def resource_path(rel):
    try:
        base = sys._MEIPASS
    except AttributeError:
        try:
            base = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
        except AttributeError:
            base = os.path.abspath(".")
    return os.path.join(base, rel)


@functools.lru_cache(maxsize=None)
def image(rel_path, size=None):
    img = pygame.image.load(resource_path(rel_path))
    if pygame.display.get_surface() is not None:
        try:
            img = img.convert_alpha()
        except pygame.error:
            pass
    if size is not None:
        img = pygame.transform.scale(img, size)
    return img


@functools.lru_cache(maxsize=None)
def font(rel_path, size):
    return pygame.font.Font(resource_path(rel_path), size)


# ── shared resource handles used throughout the UI ───────────────────────────

def piece_image(color):
    return image(f'assets/{color}_piece.png', size=(40, 40))


def background_image():
    return image('assets/background.jpg', size=(800, 800))


def welcome_background_image():
    return image('assets/welcome_background.png', size=(800, 800))


def undo_icon():
    return image('assets/undo_icon.png', size=(40, 40))


def big_font():
    return font('assets/fonts/Roboto-Bold.ttf', 36)


def small_font():
    return font('assets/fonts/Roboto-Regular.ttf', 24)


def hint_font(bold=False):
    return font(f'assets/fonts/Roboto-{"Bold" if bold else "Regular"}.ttf', 18)
