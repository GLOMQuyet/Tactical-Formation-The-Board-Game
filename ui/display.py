"""The game window: an 800×800 drawing surface shown in a window of any size.

Every screen draws on the surface returned by `open_window()`, in 800×800
units, then calls `present()`; `events()` gives pygame events with mouse
positions converted to those units. The window starts small enough to fit
the screen (a 1366×768 laptop cannot show 800 pixels plus a title bar), can
be resized, and F11 switches full screen. pygame's own SCALED mode is not
used because it never lets the window get smaller than 800×800.

Before `open_window()` (tools and tests that make their own 800×800 display)
`present()` just flips the display and positions are left as they are.
"""

import pygame

from ui.theme import BLACK, HEIGHT, WIDTH

# Room left on screen for the title bar and taskbar when sizing the window.
SCREEN_MARGIN = 120
SMALLEST = 400

_canvas = None
_windowed_size = None
_MOUSE_EVENTS = (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)


def open_window(caption, icon=None):
    """Open the window and return the 800×800 surface to draw on."""
    global _canvas
    if icon is not None:
        pygame.display.set_icon(icon)   # before set_mode, as some systems require
    side = WIDTH
    try:
        free = pygame.display.get_desktop_sizes()[0][1] - SCREEN_MARGIN
        side = max(SMALLEST, min(WIDTH, free))
    except (pygame.error, IndexError):
        pass
    pygame.display.set_mode((side, side), pygame.RESIZABLE)
    pygame.display.set_caption(caption)
    _canvas = pygame.Surface((WIDTH, HEIGHT)).convert()
    return _canvas


def _fit():
    """(window surface, scale, top-left offset, scaled size) of the canvas."""
    screen = pygame.display.get_surface()
    sw, sh = screen.get_size()
    scale = min(sw / WIDTH, sh / HEIGHT)
    size = (max(1, round(WIDTH * scale)), max(1, round(HEIGHT * scale)))
    return screen, scale, ((sw - size[0]) // 2, (sh - size[1]) // 2), size


def present():
    """Show what has been drawn, scaled to the window."""
    if _canvas is not None:
        screen, _scale, offset, size = _fit()
        if size == (WIDTH, HEIGHT):
            screen.blit(_canvas, offset)
        else:
            screen.fill(BLACK)
            screen.blit(pygame.transform.smoothscale(_canvas, size), offset)
    pygame.display.flip()


def to_canvas(pos):
    """A window position in 800×800 drawing units."""
    if _canvas is None:
        return pos
    _screen, scale, (ox, oy), _size = _fit()
    return (int((pos[0] - ox) / scale), int((pos[1] - oy) / scale))


def toggle_full_screen():
    global _windowed_size
    try:
        if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
            pygame.display.set_mode(_windowed_size or (WIDTH, HEIGHT), pygame.RESIZABLE)
        else:
            _windowed_size = pygame.display.get_surface().get_size()
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    except pygame.error:
        pass   # some video drivers cannot go full screen


def events():
    """pygame events, with mouse positions in drawing units; F11 is handled here."""
    out = []
    for event in pygame.event.get():
        if event.type in _MOUSE_EVENTS:
            event = pygame.event.Event(event.type, {**event.dict, 'pos': to_canvas(event.pos)})
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            toggle_full_screen()
            continue
        out.append(event)
    return out
