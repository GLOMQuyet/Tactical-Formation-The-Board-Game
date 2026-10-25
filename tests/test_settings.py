"""Settings file: defaults, saving, and two windows of the game sharing it.

Run with: uv run python -m unittest tests.test_settings
"""

import json
import os
import tempfile
import unittest

from core import savegame
from ui import settings


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self._default_path = savegame.default_path
        savegame.default_path = lambda: os.path.join(self.folder.name, 'autosave.json')
        settings.forget()

    def tearDown(self):
        savegame.default_path = self._default_path
        settings.forget()
        self.folder.cleanup()

    def test_defaults_without_a_file(self):
        self.assertTrue(settings.get('sound'))
        self.assertFalse(settings.get('symbols'))
        self.assertTrue(settings.get('folk_start'))
        self.assertIsNone(settings.get('language'))

    def test_a_change_is_remembered(self):
        settings.toggle('symbols')
        settings.forget()
        self.assertTrue(settings.get('symbols'))

    def test_a_file_from_an_older_version_still_loads(self):
        with open(settings.path(), 'w', encoding='utf-8') as f:
            json.dump({'language': 'vi'}, f)
        self.assertEqual(settings.get('language'), 'vi')
        self.assertTrue(settings.get('sound'))

    def test_a_change_in_another_window_is_kept(self):
        self.assertTrue(settings.get('sound'))           # this window has read the file
        with open(settings.path(), 'w', encoding='utf-8') as f:
            json.dump({'symbols': True}, f)               # another window saves meanwhile
        settings.put('sound', False)
        with open(settings.path(), encoding='utf-8') as f:
            self.assertEqual(json.load(f), {'symbols': True, 'sound': False})


if __name__ == '__main__':
    unittest.main()
