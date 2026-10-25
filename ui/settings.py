"""The player's settings, kept in `settings.json` next to the autosave.

    language     'en' or 'vi' (read and written by ui.i18n)
    sound        sound effects on or off
    symbols      a shape on each colour's pieces, for colour-blind players
    folk_start   choose who moves first with oẳn tù tì before a new game

No pygame here. A missing or unreadable file means the defaults; a file
that cannot be written leaves the choice in force for this run only.
"""

import json
import os

from core import savegame

DEFAULTS = {'sound': True, 'symbols': False, 'folk_start': True}

_values = None


def path():
    return os.path.join(os.path.dirname(savegame.default_path()), 'settings.json')


def _load():
    global _values
    if _values is None:
        try:
            with open(path(), encoding='utf-8') as f:
                data = json.load(f)
            _values = data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            _values = {}
    return _values


def get(key):
    value = _load().get(key, DEFAULTS.get(key))
    default = DEFAULTS.get(key)
    if isinstance(default, bool) and not isinstance(value, bool):
        return default
    return value


def put(key, value, save=True):
    """Change a setting and, unless `save` is False, remember it for the next run."""
    _load()[key] = value
    if save:
        try:
            os.makedirs(os.path.dirname(path()), exist_ok=True)
            tmp = path() + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(_values, f)
            os.replace(tmp, path())
        except OSError:
            pass


def toggle(key):
    put(key, not get(key))


def forget():
    """Read the file again on next use (tests point the save folder elsewhere)."""
    global _values
    _values = None
