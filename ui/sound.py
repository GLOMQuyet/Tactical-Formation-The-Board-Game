"""Short sound effects (assets/sounds/*.wav, made by tools/make_sounds.py).

Sound is optional: if the audio device cannot be opened, or the player
turned sound off (ui.settings 'sound'), play() does nothing.
"""

import pygame

from ui import assets, settings

_sounds = {}
_ready = None


def _init():
    global _ready
    if _ready is None:
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            _ready = True
        except pygame.error:
            _ready = False
    return _ready


def play(name):
    """Play sound `name` ('jump', 'flip', 'tap', 'beat', 'reveal', 'win', 'lose')."""
    if not settings.get('sound') or not _init():
        return
    sound = _sounds.get(name)
    if sound is None:
        try:
            sound = pygame.mixer.Sound(assets.resource_path(f'assets/sounds/{name}.wav'))
        except (pygame.error, FileNotFoundError):
            sound = False
        _sounds[name] = sound
    if sound:
        sound.play()
